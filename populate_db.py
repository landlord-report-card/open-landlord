import sys
import csv
from models import db, Landlord, Property
from app import app


COLUMN_LIST = [
    {"csv_column": "Parcel ID", "db_column": "parcel_id", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Tenant Complaint - Count by Source", "db_column": "tenant_complaints", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Health Violation - Count", "db_column": "health_violation_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner_1", "db_column": "name", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Eviction Probability", "db_column": "eviction_probability", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Court Case", "db_column": "court_case_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Calls for Service - Count", "db_column": "service_call_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Deferred Maintenance Probability", "db_column": "deferred_maintenance_probability", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Zip Code", "db_column": "zip_code", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Public Owner", "db_column": "public_owner", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Address", "db_column": "address", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Housing Instability Probability", "db_column": "housing_instability_probability", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Code Violations - Count", "db_column": "code_violations_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner Occupied", "db_column": "owner_occupied", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Rental Code Cases", "db_column": "rental_code_cases", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Rental Registry - Count by Rental Units & Status", "db_column": "rental_registry_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "OwnAddr_1", "db_column": "address", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Is Business", "db_column": "is_business", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Business Entity Type", "db_column": "business_entity_type", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner Property Count", "db_column": "property_count", "column_type":"STRING", "is_owner_col": True},
    {"csv_column": "Rent Plan Probability", "db_column": "rent_plan_probability", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Inspection - Count", "db_column": "inspection_count", "column_type":"STRING", "is_owner_col": False},
    {"csv_column": "Owner Location", "db_column": "location", "column_type":"STRING", "is_owner_col": True},
]


filename = sys.argv[1]


def process_property(row, landlords, db):
    # Hack to ignore "address unknown"
    if "Address Unknown" in row["Address"]:
        return

    property_dict = {}
    for column_obj in COLUMN_LIST:
        if not column_obj["is_owner_col"]:

            # Parse empty strings as nulls
            clean_value = None if row[column_obj["csv_column"]] == "" else row[column_obj["csv_column"]]
            property_dict[column_obj["db_column"]] = clean_value

    # Include mapping to landlord table
    property_dict["owner_id"] = landlords[row["Owner_1"]]
    # print(landlords[row["Owner_1"]])

    # if "parcel_id" not in property_dict:
    #     print(property_dict)
    #     print(row)

    if property_dict["parcel_id"] is not None:
        property_obj = Property(**property_dict)
        db.session.add(property_obj)

def process_landlord(row, landlords, db):
    # If we've already processed this landlord, return
    if row["Owner_1"] in landlords:
        return

    landlord_dict = {}
    for column_obj in COLUMN_LIST:
        if column_obj["is_owner_col"]:
            landlord_dict[column_obj["db_column"]] = row[column_obj["csv_column"]]
    landlord_obj = Landlord(**landlord_dict)
    db.session.add(landlord_obj)
    db.session.flush()
    landlords[row["Owner_1"]] = landlord_obj.id


with app.app_context():
    db.create_all()
    landlords = {}
    # For convenience, we process all landlords first, store their IDs, then process properties
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            process_landlord(row, landlords, db)
    db.session.flush()

    print(landlords)

    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            process_property(row, landlords, db)


    db.session.commit()



# with app.app_context():
#     db.create_all()
# l1 = Landlord(name='Joe Smith', address='Fifth Avenue, New York, NY', location="In State", property_count=3, service_call_count=5)
# l2 = Landlord(name='Bob Jones', address='Second Avenue, Albany, NY', location="In Albany", property_count=1, service_call_count=8)
# l3 = Landlord(name='Mike Smith', address='Third Avenue, New York, NY', location="In State", property_count=12, service_call_count=2)
# db.session.add(guest)
# db.session.commit()