from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Landlord(db.Model):
    __tablename__ = "landlord"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(250))
    location = db.Column(db.String(250))


    def __repr__(self):
        return '<Landlord %r>' % self.name


class Property(db.Model):
    __tablename__ = "property"
    id = db.Column(db.Integer, primary_key=True)
    parcel_id = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    property_type = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey("landlord.id"))
    owner = db.relationship("Landlord", backref="properties")
    service_call_count = db.Column(db.Integer)


    def __repr__(self):
        return '<Property %r>' % self.address

