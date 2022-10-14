import sys
import csv
import argparse
from models import db, Landlord, Property
from address import AddressParser, Address
from app import app

CODE_VIOLATIONS_TOTAL_COUNT_COLUMN = "Code Violations - Count - In the last 24 months" 
CODE_VIOLATIONS_ROP_COUNT_COLUMN = "Code Violations - Count - ROP - In the last 24 months"

COLUMN_LIST = [
    {"csv_column": "Parcel ID", "db_column": "parcel_id", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Tenant Complaint - Count by Source - In the last 24 months", "db_column": "tenant_complaints", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner_1", "db_column": "name", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Zip Code", "db_column": "zip_code", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Public Owner", "db_column": "public_owner", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Address", "db_column": "address", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": CODE_VIOLATIONS_TOTAL_COUNT_COLUMN, "db_column": "code_violations_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner Occupied", "db_column": "owner_occupied", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "OwnAddr_1", "db_column": "address", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Is Business", "db_column": "is_business", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Business Entity Type", "db_column": "business_entity_type", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner Property Count", "db_column": "property_count", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Owner Location", "db_column": "location", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Current Use", "db_column": "current_use", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Police Incidents - Count - LANDLORD/TENANT TROUBLE - In the last 24 months", "db_column": "police_incidents_count", "column_type":"STRING", "is_owner_col": False},
]


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


def generate_parsed_address_columns():
    with app.app_context():
        ap = AddressParser()
        properties = Property.query.all()

        for prop in properties:
            parsed_address = ap.parse_address(prop.address)
            prop.street_name = parsed_address.street
            prop.house_number  = parsed_address.house_number

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
    else:
        for column_obj in COLUMN_LIST:
            if column_obj["is_owner_col"]:
                setattr(landlord, column_obj["db_column"], row[column_obj["csv_column"]])

    db.session.flush()
    landlords[row["Owner_1"]] = landlord.id


def get_clean_value(row, column_obj):
    clean_value = None if row[column_obj["csv_column"]] == "" else row[column_obj["csv_column"]]
    if column_obj["db_column"] == "code_violations_count":
        clean_value = get_adjusted_code_violations(row)
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
    parser.add_argument('--filename', type=str, help='Filename to import from')

    args = parser.parse_args()

    if args.group:
        add_property_group_column(args.filename)
    elif args.populate:
        populate_empty_db(args.filename)
    elif args.update:
        update_database(args.filename)
    elif args.generate:
        generate_parsed_address_columns()
    elif args.rop:
        generate_code_violations_columns(args.filename)
