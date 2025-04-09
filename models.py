from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case, inspect
from sqlalchemy.sql import func, select


db = SQLAlchemy()


class Alias(db.Model):
    __tablename__ = "staging_alias"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    group_id = db.Column(db.String(256), unique=False, nullable=True)


class Eviction(db.Model):
    __tablename__ = "eviction"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    caseid = db.Column(db.String(256), unique=True, nullable=True)
    case_date = db.Column(db.DateTime())
    petitioner = db.Column(db.String(256), unique=False, nullable=True)
    matched_name = db.Column(db.String(256), unique=False, nullable=True)


class CodeCase(db.Model):
    __tablename__ = "codecase"
    case_id = db.Column(db.String(80), primary_key=True)
    case_number = db.Column(db.String(256))
    case_type = db.Column(db.String(256))
    case_status = db.Column(db.String(256))
    apply_date = db.Column(db.DateTime())
    final_date = db.Column(db.DateTime())
    description = db.Column(db.Text)
    address_line_1 = db.Column(db.String(256))
    address_line_2 = db.Column(db.String(256))
    postal_code = db.Column(db.String(80))
    parcel_id = db.Column(db.String(80))
    number_of_residential_units_in_building = db.Column(db.Integer)
    number_of_units_to_receive_rops = db.Column(db.Integer)
    units_to_receive_an_rop = db.Column(db.String())
    issue_rops = db.Column(db.Boolean)


class Landlord(db.Model):
    __tablename__ = "staging_landlord"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(250))
    location = db.Column(db.String(250))
    group_id = db.Column(db.String(256))

    def __repr__(self):
        return '<Landlord %r>' % self.name

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Property(db.Model):
    __tablename__ = "staging_property"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parcel_id = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    house_number = db.Column(db.Integer)
    street_name = db.Column(db.String(250))
    zip_code = db.Column(db.String(10))
    tenant_complaints_count = db.Column(db.Integer) ######
    owner_occupied = db.Column(db.String(250))
    code_violations_count = db.Column(db.Integer) ######
    is_business = db.Column(db.String(250))
    public_owner = db.Column(db.String(250))
    business_entity_type = db.Column(db.String(250))
    current_use = db.Column(db.String(250))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    group_id = db.Column(db.String(50), db.ForeignKey("staging_landlord.group_id"))


    def __repr__(self):
        return '<Property %r>' % self.address

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

