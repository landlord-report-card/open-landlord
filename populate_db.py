import sys
import csv
from models import db, Landlord, Property
from app import app


filename = sys.argv[1]

with app.app_context():
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        landlords = {}
        for row in reader:
            parcel_id = row['Parcel ID']
            address = row['Address']
            property_type = row['Property Type']
            if row['Calls for Service - Count'] == "":
                service_call_count = None
            else:
                service_call_count = row['Calls for Service - Count']
            owner_location = row['Owner Location']
            owner_name = row['Owner_1']
            owner_address = row['OwnAddr_1']

            if owner_name not in landlords:
                landlord_obj = Landlord(name=owner_name, address=owner_address, location=owner_location)
                db.session.add(landlord_obj)
                db.session.flush()
                landlords[owner_name] = landlord_obj.id
        
            property_obj = Property(parcel_id=parcel_id, address=address, property_type=property_type, owner_id=landlords[owner_name], service_call_count=service_call_count)
            db.session.add(property_obj)

        db.session.commit()



# with app.app_context():
#     db.create_all()
# l1 = Landlord(name='Joe Smith', address='Fifth Avenue, New York, NY', location="In State", property_count=3, service_call_count=5)
# l2 = Landlord(name='Bob Jones', address='Second Avenue, Albany, NY', location="In Albany", property_count=1, service_call_count=8)
# l3 = Landlord(name='Mike Smith', address='Third Avenue, New York, NY', location="In State", property_count=12, service_call_count=2)
# db.session.add(guest)
# db.session.commit()