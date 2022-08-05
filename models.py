from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Landlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(250))
    location = db.Column(db.String(250))
    property_count = db.Column(db.Integer)
    service_call_count = db.Column(db.Integer)

    def __repr__(self):
        return '<Landlord %r>' % self.name



# l1 = Landlord(name='Joe Smith', address='Fifth Avenue, New York, NY', location="In State", property_count=3, service_call_count=5)
# l2 = Landlord(name='Bob Jones', address='Second Avenue, Albany, NY', location="In Albany", property_count=1, service_call_count=8)
# l3 = Landlord(name='Mike Smith', address='Third Avenue, New York, NY', location="In State", property_count=12, service_call_count=2)
# db.session.add(guest)
# db.session.commit()