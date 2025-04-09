import sys
import csv
import argparse
import uuid
import json
import logging
import usaddress
from hashlib import sha256
from models import db, Landlord, Property, Alias, CodeCase
from app import app
from sqlalchemy import types, func
from datetime import datetime
from dateutil.relativedelta import relativedelta


COLUMN_LIST = [
    {"csv_column": "Parcel ID", "db_column": "parcel_id", "column_type":types.String, "is_owner_col": False}, 
    {"csv_column": "Owner_1", "db_column": "name", "column_type":types.String, "is_owner_col": True},
    {"csv_column": "Address", "db_column": "address", "column_type":types.String, "is_owner_col": False},
    {"csv_column": "OwnAddr_1", "db_column": "address", "column_type":types.String, "is_owner_col": True}, 
]

COMMON_NAMES = [
    "Albany Housing Authority",
]


##########################################
# Helper Functions
#
##########################################


def get_clean_value(row, column_obj):
    clean_value = None if row[column_obj["csv_column"]] == "" else row[column_obj["csv_column"]]
    if column_obj["column_type"] == types.Integer:
        clean_value = column_obj["default_value"] if clean_value is None else int(float(clean_value)) # Parse as float because sometimes we get decimals
    return clean_value



def clean_name(name):
    return ''.join(name.split()).lower()


def get_group_id(name, groupings):
    # Add group ID
    group_id = None
    for group in groupings:
        if clean_name(name) == clean_name(group["name"]):
            group_id = group["group_id"]

    # Generate our own hash based on owner name if none exists. We may want to use Name + Address to avoid overly matching
    if group_id is None:
        return sha256(clean_name(name).encode('utf-8')).hexdigest()

    return group_id


def update_landlord_obj(prop, landlord):
    for column_obj in COLUMN_LIST:
        # Use preferred/common names if applicable:
        if prop["Owner_1"] in COMMON_NAMES and column_obj["is_owner_col"]:
            landlord[column_obj["db_column"]] = get_clean_value(prop, column_obj)


def create_landlord_obj(prop):
    landlord_dict = {}
    for column_obj in COLUMN_LIST:
        if column_obj["is_owner_col"]:
            landlord_dict[column_obj["db_column"]] = get_clean_value(prop, column_obj)

    return landlord_dict


def parse_csv_as_dict_list(csv_filename):
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def parse_geocoded_csv_as_map(csv_filename):
    geocoded_parcel_ids = {}
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            geocoded_parcel_ids[row["parcel_id"]] = (row["latitude"], row["longitude"]) 

    return geocoded_parcel_ids

##########################################
# Data Transformation Functions
#
##########################################

def create_alias_list(properties, groupings):
    logging.warning("Creating Alias List.")
    aliases = []
    seen_aliases = set()
    for prop in properties:
        alias_name = prop["Owner_1"]
        if alias_name in seen_aliases:
            continue
            
        group_id = get_group_id(prop["Owner_1"], groupings)

        alias = {
            "name": alias_name,
            "group_id": group_id
        }
        aliases.append(alias)
        seen_aliases.add(alias_name)

    return aliases


def get_street_name_and_number(raw_address):
    street_name = None
    house_number = None
    address_dict = {}
    parsed_address_tuple_list = usaddress.parse(raw_address)
    for value, field in parsed_address_tuple_list:
        address_dict[field] = value

    if "StreetName" in address_dict:
        street_name = address_dict["StreetName"]
    if "AddressNumber" in address_dict:
        house_number = address_dict["AddressNumber"]

    return (street_name, house_number)


def create_property_list(properties, groupings, geocoding_map):
    logging.warning("Creating Property List.")
    property_objects = []
    count = 0

    for prop in properties:
        if prop["Parcel ID"] is "" or prop["Owner_1"] is "":
            continue

        if count % 5000 == 0:
            logging.warning(f"Property list, iterated over row {count}.")

        property_dict = {}
        for column_obj in COLUMN_LIST:
            if not column_obj["is_owner_col"]:
                property_dict[column_obj["db_column"]] = get_clean_value(prop, column_obj)

        street_name, house_number = get_street_name_and_number(property_dict["address"])
        property_dict["street_name"] = street_name
        property_dict["house_number"] = house_number

        if prop["Parcel ID"] in geocoding_map:
            property_dict["latitude"] = geocoding_map[prop["Parcel ID"]][0]
            property_dict["longitude"] = geocoding_map[prop["Parcel ID"]][1]

        property_dict["group_id"] = get_group_id(prop["Owner_1"], groupings)


        property_objects.append(property_dict)
        count = count + 1


    return property_objects

def create_landlord_list(properties, groupings):
    logging.warning("Creating Landlord List.")
    landlords = {}
    logging.warning("Iterating over all properties.")
    count = 0
    for prop in properties:
        if prop["Parcel ID"] is "" or prop["Owner_1"] is "":
            continue

        if count % 5000 == 0:
            logging.warning(f"Landlord list, iterated over row {count}.")

        group_id = get_group_id(prop["Owner_1"], groupings)

        if group_id in landlords:
            update_landlord_obj(prop, landlords[group_id])
        else:
            landlord = create_landlord_obj(prop)
            landlord["group_id"] = group_id
            landlords[group_id] = landlord

        if landlord["name"] is None:
            print(prop)
            print(landlord)

        count = count + 1

    return landlords

def commit_to_db(landlord_list, property_list, alias_list):
    landlords = []
    properties = []
    aliases = []

    with app.app_context():
        for group_id, landlord in landlord_list.items():
            landlords.append(Landlord(**landlord))
        for prop in property_list:
            properties.append(Property(**prop))
        for alias in alias_list:
            aliases.append(Alias(**alias))

        logging.warning("Deleting all data from tables.")

        # Delete all rows from all tables
        db.session.query(Landlord).delete()
        db.session.query(Property).delete()
        db.session.query(Alias).delete()

        logging.warning("Saving all objects now.")

        db.session.bulk_save_objects(landlords)
        db.session.bulk_save_objects(properties)
        db.session.bulk_save_objects(aliases)

        logging.warning("Committing to database.")

        db.session.commit()


# TODO: Still requires deleting bogus lines at beginning of CSV and removing errant "=" signs from CSV
def populate_database(properties_filename, groupings_filename, geo_filename):
    logging.warning("Parsing CSVs as Dictionaries.")

    properties = parse_csv_as_dict_list(properties_filename) # "/Users/akaier/Downloads/tolemi-export1680275139690.csv")
    groupings = parse_csv_as_dict_list(groupings_filename) # "/Users/akaier/Downloads/albany_owner_groups_with_properties_2023_03_23.csv")
    geocoding_map = parse_geocoded_csv_as_map(geo_filename) #"/Users/akaier/Downloads/albany_properties_lat_lon.csv")
    
    landlord_list = create_landlord_list(properties, groupings)
    property_list = create_property_list(properties, groupings, geocoding_map)
    alias_list = create_alias_list(properties, groupings)



##########################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database Population Helper Scripts')

    parser.add_argument('--properties', type=str)
    parser.add_argument('--groupings', type=str)
    parser.add_argument('--geocoding', type=str)

    args = parser.parse_args()

    populate_database(args.properties, args.groupings, args.geocoding)




