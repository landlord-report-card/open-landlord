import sys
import csv
import argparse
import uuid
import json
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
    {"csv_column": "Tenant Complaint - Count by Source - In the last 12 months", "db_column": "tenant_complaints", "column_type":types.Integer, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Owner_1", "db_column": "name", "column_type":types.String, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Zip Code", "db_column": "zip_code", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Public Owner", "db_column": "public_owner", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Address", "db_column": "address", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": CODE_VIOLATIONS_TOTAL_COUNT_COLUMN, "db_column": "code_violations_count", "column_type":types.Integer, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Owner Occupied", "db_column": "owner_occupied", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "OwnAddr_1", "db_column": "address", "column_type":types.String, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Is Business", "db_column": "is_business", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Business Entity Type", "db_column": "business_entity_type", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Owner Property Count", "db_column": "property_count", "column_type":types.Integer, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Owner Location", "db_column": "location", "column_type":types.String, "is_owner_col": True, "is_owner_aggregate": False},
    {"csv_column": "Current Use", "db_column": "current_use", "column_type":types.String, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "Police Incidents - Count - LANDLORD/TENANT TROUBLE - In the last 12 months", "db_column": "police_incidents_count", "column_type":types.Integer, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Unsafe & Unfit Buildings - In the last 12 months", "db_column": "unsafe_unfit_count", "column_type":types.Integer, "is_owner_col": False, "is_owner_aggregate": True},
    {"csv_column": "Rental Registry - Count by Rental Units - In the last 30 months", "db_column": "unit_count", "column_type":types.Integer, "is_owner_col": False, "is_owner_aggregate": False},
    {"csv_column": "ROP Code Cases - Count By Status - Closed - In the last 30 months", "db_column": "has_rop", "column_type":types.Boolean, "is_owner_col": False, "is_owner_aggregate": False},
]


def populate_alias_table(property_list_file, group_id_filename):
    # This holds a mapping of Landlord name to group ID
    landlord_name_to_group_id = {}
    with open(group_id_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            landlord_name_to_group_id[row["name"]] = row["group_id"]

    current_id = 1
    with app.app_context():
        with open(property_list_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            landlords_seen = []
            for row in reader:
                if row["Owner_1"] in landlords_seen or len(row["Owner_1"]) == 0:
                    continue
                else:
                    landlords_seen.append(row["Owner_1"])

                owner = Landlord.query.filter_by(name=row["Owner_1"]).first()
                if owner is None:
                    group_id = landlord_name_to_group_id[row["Owner_1"]]
                    owner = Landlord.query.filter_by(group_id=group_id).first()
                if owner is None:
                    print(f"Failure on {row}")
                alias = {
                    "id": current_id,
                    "name": row["Owner_1"],
                    "landlord_id": owner.id
                }
                alias_obj = Alias(**alias)
                db.session.add(alias_obj)
                current_id = current_id + 1
        db.session.commit()
                


def update_owner_id(property_list_file, group_id_filename):
    # This holds a mapping of Landlord name to group ID
    landlord_name_to_group_id = {}
    with open(group_id_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            landlord_name_to_group_id[row["name"]] = row["group_id"]

    with app.app_context():
        with open(property_list_file, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if len(row["Owner_1"]) == 0:
                    continue
                prop = Property.query.filter_by(parcel_id=row["Parcel ID"]).first()
                owner = Landlord.query.filter_by(name=row["Owner_1"]).first()
                if owner is None:
                    group_id = landlord_name_to_group_id[row["Owner_1"]]
                    owner = Landlord.query.filter_by(group_id=group_id).first()
                if owner is None:
                    print(f"Failure on {row}")
                prop.owner_id = owner.id
        db.session.commit()

# Helper function to build out aggregated list of landlords (by group id) in a big dictionary
def generate_landlord_group_dict(property_list_file, group_id_filename):
    # This holds a mapping of Landlord name to group ID
    landlord_name_to_group_id = {}
    with open(group_id_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            landlord_name_to_group_id[row["name"]] = row["group_id"]

    landlord_groups = {}
    with open(property_list_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if len(row["Owner_1"]) == 0:
                continue

            # If we already have a group ID for this LL, use it, otherwise generate a new one.
            if row["Owner_1"] in landlord_name_to_group_id:
                group_id = landlord_name_to_group_id[row["Owner_1"]]
            else:
                group_id = str(uuid.uuid4())
                landlord_name_to_group_id[row["Owner_1"]] = group_id

            # Aggregate the stats if we already have seen this landlord, or else create new entry
            if group_id in landlord_groups:
                landlord = landlord_groups[group_id]
                landlord["properties_associated"] = landlord["properties_associated"] + 1
                for column_obj in COLUMN_LIST:
                    # Sum the aggregated columns
                    if column_obj["is_owner_aggregate"]:
                        landlord[column_obj["db_column"]] = landlord[column_obj["db_column"]] + get_clean_value(row, column_obj)
            else:
                landlord_groups[group_id] = {}
                for column_obj in COLUMN_LIST:
                    landlord = landlord_groups[group_id]
                    landlord["properties_associated"] = 1
                    if column_obj["is_owner_aggregate"] or column_obj["is_owner_col"]:
                        landlord[column_obj["db_column"]] = get_clean_value(row, column_obj)
    return landlord_groups


def update_landlord_aggregate_values(property_list_file, group_id_filename):
    with app.app_context():
        landlord_groups = generate_landlord_group_dict(property_list_file, group_id_filename)

        #print(json.dumps(landlord_groups))

        for group_id, landlord_metadata in landlord_groups.items():

            # For property count, take the max of the properties associated and the count provided by the city.
            if landlord_metadata["properties_associated"] > landlord_metadata["property_count"]:
                landlord_metadata["property_count"] = landlord_metadata["properties_associated"]

            queried_landlord = Landlord.query.filter_by(name=landlord_metadata["name"]).first()

            # If this landlord does not exist yet, create, otherwise update.
            if queried_landlord is None:
                landlord_dict = {"group_id": group_id}
                for column_obj in COLUMN_LIST:
                    if column_obj["is_owner_aggregate"] or column_obj["is_owner_col"]: 
                        landlord_dict[column_obj["db_column"]] = landlord_metadata[column_obj["db_column"]]
                landlord_obj = Landlord(**landlord_dict)
                db.session.add(landlord_obj)
            else:
                setattr(queried_landlord, "group_id", group_id)
                for column_obj in COLUMN_LIST:
                    if column_obj["is_owner_aggregate"] or column_obj["is_owner_col"]:
                        setattr(queried_landlord, column_obj["db_column"], landlord_metadata[column_obj["db_column"]])

        db.session.commit()



def populate_evictions(filename):
    with app.app_context():
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter ='\t')
            for row in reader:
                # Try matching on Landlord Name first, then Building Blocks Entity Name, then Group ID
                filter_criteria = Alias.name.ilike(row["Landlord Name"]) | Alias.name.ilike(row["Building Blocks Entity Name"])
                alias = Alias.query.filter(filter_criteria).first()
                if alias is None:
                    print("Unable to find Landlord {}".format(row["Landlord Name"]))
                    continue
                else:
                    landlord = Landlord.query.filter_by(id=alias.landlord_id).first()


                landlord.eviction_count = row["# of new filings, Q3"]

        db.session.commit()



def add_property_group_column(filename):
    with app.app_context():
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                landlord = Landlord.query.filter_by(name=row["name"]).first()
                if landlord is None:
                    print("Missing property with name {}".format(row["name"]))
                    continue
                landlord.group_id = row["group_id"]

        db.session.commit()


def populate_empty_db(filename):
    with app.app_context():
        db.create_all()
        landlords = {}
        # For convenience, we process all landlords first, store their IDs, then process properties
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter ='\t')
            for row in reader:
                # If we've already processed this landlord, return
                if row["Owner_1"] in landlords:
                    return

                create_landlord(row, db)
                landlords[row["Owner_1"]] = landlord_obj.id
        db.session.flush()

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter ='\t')
            for row in reader:
                # Hack to ignore "address unknown"
                if "Address Unknown" in row["Address"]:
                    return
                create_property(row, landlords, db)


        db.session.commit()


# Removes ROP Code Violations
def generate_code_violations_columns(filename):
    with app.app_context():
        # For convenience, we process all landlords first, store their IDs, then process properties
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                prop = Property.query.filter_by(parcel_id=row["Parcel ID"]).first()
                if prop is None:
                    print("Missing property with address {}".format(row["Address"]))
                    continue
                code_violations_count = get_adjusted_code_violations(row)
                print("Address {} violations {}".format(row["Address"], code_violations_count))
                prop.code_violations_count = code_violations_count
        db.session.commit()


def get_adjusted_code_violations(row):
    total_violations = 0
    rop_violations = 0
    if row[CODE_VIOLATIONS_TOTAL_COUNT_COLUMN]:
        total_violations = int(row[CODE_VIOLATIONS_TOTAL_COUNT_COLUMN])
    if row[CODE_VIOLATIONS_ROP_COUNT_COLUMN]:
        rop_violations = int(row[CODE_VIOLATIONS_ROP_COUNT_COLUMN])
    code_violations_count = total_violations - rop_violations
    return code_violations_count

def create_landlord(row, db):
    landlord_dict = {}
    for column_obj in COLUMN_LIST:
        if column_obj["is_owner_col"]:
            landlord_dict[column_obj["db_column"]] = row[column_obj["csv_column"]]
    landlord_obj = Landlord(**landlord_dict)
    db.session.add(landlord_obj)
    return landlord_obj


def update_landlord(row, landlords, db):
    # If we've already processed this landlord, return
    if row["Owner_1"] in landlords:
        return

    landlord = Landlord.query.filter_by(name=row["Owner_1"]).first()


    if landlord is None:
        landlord = create_landlord(row, db)
        # print("Creating landlord")
    else:
        # print("Landlord Found")
        # print(landlord.name)
        for column_obj in COLUMN_LIST:
            if column_obj["is_owner_col"]:
                setattr(landlord, column_obj["db_column"], row[column_obj["csv_column"]])

    db.session.flush()
    landlords[row["Owner_1"]] = landlord.id


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
        clean_value = 0 if clean_value is None else int(float(clean_value)) # Parse as float because sometimes we get decimals
    return clean_value


def create_property(row, landlords, db):
    property_dict = {}
    for column_obj in COLUMN_LIST:
        if not column_obj["is_owner_col"]:

            # Parse empty strings as nulls
            property_dict[column_obj["db_column"]] = get_clean_value(row, column_obj)

    # Include mapping to landlord table
    property_dict["owner_id"] = landlords[row["Owner_1"]]

    if property_dict["parcel_id"] is not None:
        property_obj = Property(**property_dict)
        db.session.add(property_obj)


def update_property(row, landlords, db):
    # Hack to ignore "address unknown"
    if "Address Unknown" in row["Address"]:
        return

    prop = Property.query.filter_by(parcel_id=row["Parcel ID"]).first()

    if prop is None:
        create_property(row, landlords, db)
    else:
        for column_obj in COLUMN_LIST:
            if not column_obj["is_owner_col"]:
                setattr(prop, column_obj["db_column"], get_clean_value(row, column_obj))


# TODO: Still requires deleting bogus lines at beginning of CSV and removing errant "=" signs from CSV
def update_database(filename):
    with app.app_context():
        landlords = {}
        # For convenience, we process all landlords first, store their IDs, then process properties
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                update_landlord(row, landlords, db)
        db.session.flush()

        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                update_property(row, landlords, db)


        db.session.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Database Population Helper Scripts')

    parser.add_argument('--group', action='store_true', help='Adds the property group column from a spreadsheet')
    parser.add_argument('--update', action='store_true', help='Update property and landlord data from a spreadsheet')
    parser.add_argument('--populate', action='store_true', help='Does initial population from a spreadsheet to an empty DB')
    parser.add_argument('--generate', action='store_true', help='Generates parsed address columns')
    parser.add_argument('--rop', action='store_true', help='Generates ROP violations count')
    parser.add_argument('--evictions', action='store_true', help='Populates evictions from Evictions TSV')
    parser.add_argument('--aggregate', action='store_true', help='Generate Landlord Aggregate stats')
    parser.add_argument('--ownerid', action='store_true', help='Update owner ids only')
    parser.add_argument('--alias', action='store_true', help='Populate alias table')
    parser.add_argument('--filename', type=str, help='Filename to import from')
    parser.add_argument('--groupid', type=str, help='Group id file to import ')


    args = parser.parse_args()

    if args.group:
        add_property_group_column(args.filename)
    elif args.populate:
        populate_empty_db(args.filename)
    elif args.update:
        update_database(args.filename)
    elif args.generate:
        generate_parsed_address_columns()
    elif args.evictions:
        populate_evictions(args.filename)
    elif args.rop:
        generate_code_violations_columns(args.filename)
    elif args.aggregate:
        update_landlord_aggregate_values(args.filename, args.groupid)
    elif args.ownerid:
        update_owner_id(args.filename, args.groupid)
    elif args.alias:
        populate_alias_table(args.filename, args.groupid)


