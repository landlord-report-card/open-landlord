import sys
import csv
import argparse
import uuid
import json
import logging
from hashlib import sha256
from models import db, Landlord, Property, Alias
from app import app
from sqlalchemy import types


CODE_VIOLATIONS_TOTAL_COUNT_COLUMN = "Code Violations - Count - In the last 12 months" 
CODE_VIOLATIONS_ROP_COUNT_COLUMN = "Code Violations - Count - ROP - In the last 12 months"

ROP_POSSIBLE_COLUMNS = [
    "ROP Code Cases - Count By Status - Closed - In the last 30 months",
    "ROP Code Cases - Count By Status - In Compliance - In the last 30 months",
    "ROP Code Cases - Count By Status - Open - In the last 30 months",
]

COLUMN_LIST = [
    {"csv_column": "Parcel ID", "db_column": "parcel_id", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Tenant Complaint - Count by Source - In the last 12 months", "db_column": "tenant_complaints_count", "column_type":types.Integer, "default_value": 0, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Owner_1", "db_column": "name", "column_type":types.String, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Zip Code", "db_column": "zip_code", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Public Owner", "db_column": "public_owner", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Address", "db_column": "address", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": CODE_VIOLATIONS_TOTAL_COUNT_COLUMN, "db_column": "code_violations_count", "column_type":types.Integer, "default_value": 0, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Owner Occupied", "db_column": "owner_occupied", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "OwnAddr_1", "db_column": "address", "column_type":types.String, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Is Business", "db_column": "is_business", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Business Entity Type", "db_column": "business_entity_type", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Owner Property Count", "db_column": "property_count", "column_type":types.Integer, "default_value": 0, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Owner Location", "db_column": "location", "column_type":types.String, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Current Use", "db_column": "current_use", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Police Incidents - Count - LANDLORD/TENANT TROUBLE - In the last 12 months", "db_column": "police_incidents_count", "column_type":types.Integer, "default_value": 0, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Unsafe & Unfit Buildings - In the last 12 months", "db_column": "unsafe_unfit_count", "column_type":types.Integer, "default_value": 0, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Rental Registry - Count by Rental Units - In the last 30 months", "db_column": "unit_count", "column_type":types.Integer, "default_value": 1, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "ROP Code Cases - Count By Status - Closed - In the last 30 months", "db_column": "has_rop", "column_type":types.Boolean, "is_owner_col": False, "is_owner_aggregate": False},
]


##########################################
# Helper Functions
#
##########################################

def get_adjusted_code_violations(row):
    total_violations = 0
    rop_violations = 0
    if row[CODE_VIOLATIONS_TOTAL_COUNT_COLUMN]:
        total_violations = int(row[CODE_VIOLATIONS_TOTAL_COUNT_COLUMN])
    if row[CODE_VIOLATIONS_ROP_COUNT_COLUMN]:
        rop_violations = int(row[CODE_VIOLATIONS_ROP_COUNT_COLUMN])
    code_violations_count = total_violations - rop_violations
    return code_violations_count


def check_for_rop(row):
    for rop_column in ROP_POSSIBLE_COLUMNS:
        if row[rop_column] != "":
            return True
    return False


def get_clean_value(row, column_obj):
    clean_value = None if row[column_obj["csv_column"]] == "" else row[column_obj["csv_column"]]
    if column_obj["db_column"] == "code_violations_count":
        clean_value = get_adjusted_code_violations(row)
    if column_obj["db_column"] == "has_rop":
        clean_value = check_for_rop(row)
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
    landlord["properties_associated"] = landlord["properties_associated"] + 1
    for column_obj in COLUMN_LIST:
        # Sum the aggregated columns
        if column_obj["is_owner_aggregate"]:
            landlord[column_obj["db_column"]] = landlord[column_obj["db_column"]] + get_clean_value(prop, column_obj)


def create_landlord_obj(prop):
    landlord_dict = {}
    landlord_dict["properties_associated"] = 1
    landlord_dict["eviction_count"] = 0
    for column_obj in COLUMN_LIST:
        if column_obj["is_owner_col"] or column_obj["is_owner_aggregate"]:
            landlord_dict[column_obj["db_column"]] = get_clean_value(prop, column_obj)
    return landlord_dict


def parse_csv_as_dict_list(csv_filename):
    with open(csv_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


##########################################
# Data Transformation Functions
#
##########################################

def create_alias_list(properties, groupings, evictions):
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


def create_property_list(properties, groupings, evictions):
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

        property_dict["group_id"] = get_group_id(prop["Owner_1"], groupings)

        property_objects.append(property_dict)
        count = count + 1

    return property_objects


def create_landlord_list(properties, groupings, evictions):
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


    # Choose the higher of properties associated and property count, and remove the associated value
    logging.warning("Resetting property associated values.")
    for group_id, landlord in landlords.items():
        if landlord["properties_associated"] > landlord["property_count"]:
            landlord["property_count"] = landlord["properties_associated"]
        del landlord["properties_associated"]
      
    logging.warning("Adding Evictions.")
    for evictor in evictions:
        group_id = get_group_id(evictor["Evictor"], groupings)
        if group_id in landlords:
            landlords[group_id]["eviction_count"] = landlords[group_id]["eviction_count"] + int(evictor["Eviction Count"])
        else:
            print("No match found for {}".format(evictor["Evictor"]))

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
def populate_database(properties_filename, groupings_filename, evictions_filename):
    logging.warning("Parsing CSVs as Dictionaries.")

    properties = parse_csv_as_dict_list(properties_filename) # "/Users/akaier/Downloads/tolemi-export1680275139690.csv")
    groupings = parse_csv_as_dict_list(groupings_filename) # "/Users/akaier/Downloads/albany_owner_groups_with_properties_2023_03_23.csv")
    evictions = parse_csv_as_dict_list(evictions_filename) #"/Users/akaier/Downloads/Albany Evictions Logger - Counter.csv")
    
    landlord_list = create_landlord_list(properties, groupings, evictions)
    property_list = create_property_list(properties, groupings, evictions)
    alias_list = create_alias_list(properties, groupings, evictions)

    commit_to_db(landlord_list, property_list, alias_list)


##########################################


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database Population Helper Scripts')

    parser.add_argument('--properties', type=str)
    parser.add_argument('--groupings', type=str)
    parser.add_argument('--evictions', type=str)

    args = parser.parse_args()

    populate_database(args.properties, args.groupings, args.evictions)




