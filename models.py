from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Landlord(db.Model):
    __tablename__ = "landlord"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(250))
    location = db.Column(db.String(250))
    property_count = db.Column(db.Integer)


    def __repr__(self):
        return '<Landlord %r>' % self.name


class Property(db.Model):
    __tablename__ = "property"
    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    zip_code = db.Column(db.String(10))
    property_type = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey("landlord.id"))
    owner = db.relationship("Landlord", backref="properties")
    service_call_count = db.Column(db.Integer)
    tenant_complaints = db.Column(db.Integer)
    health_violation_count = db.Column(db.Integer)
    eviction_probability = db.Column(db.Float)
    court_case_count = db.Column(db.Integer)
    deferred_maintenance_probability = db.Column(db.Float)
    owner_occupied = db.Column(db.String(250))
    rental_registry_count = db.Column(db.Integer)
    inspection_count = db.Column(db.Integer)
    rental_code_cases = db.Column(db.Integer)
    code_violations_count = db.Column(db.Integer)
    rent_plan_probability = db.Column(db.Float)
    is_business = db.Column(db.String(250))
    public_owner = db.Column(db.String(250))
    business_entity_type = db.Column(db.String(250))
    housing_instability_probability = db.Column(db.Float)


    def __repr__(self):
        return '<Property %r>' % self.address


