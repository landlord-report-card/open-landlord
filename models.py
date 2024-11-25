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


class CodeCase(db.Model):
    __tablename__ = "codecase"
    case_id = db.Column(db.String(80), primary_key=True)
    case_number = db.Column(db.String(256))
    case_type = db.Column(db.String(256))
    case_status = db.Column(db.String(256))
    apply_date = db.Column(db.DateTime())
    final_date = db.Column(db.DateTime())
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) #generated
    name = db.Column(db.String(80), unique=True, nullable=False) #Owner_1
    address = db.Column(db.String(250)) #OwnAddr_1
    location = db.Column(db.String(250)) #Owner Location
    group_id = db.Column(db.String(256)) #partly generated partly from grouping file
    property_count = db.Column(db.Integer) #calculated from property list
    unit_count = db.Column(db.Integer) #calculated from codecase data
    unsafe_unfit_count = db.Column(db.Integer) ######  #calculated from codecase data
    eviction_count = db.Column(db.Integer) #calculated from evictions data
    tenant_complaints_count = db.Column(db.Integer) ###### #to be removed
    code_violations_count = db.Column(db.Integer) ###### #calculated from codecase data
    police_incidents_count = db.Column(db.Integer) ###### #to be removed


    @hybrid_property
    def code_violations_count_per_property(self):
        if self.code_violations_count and self.property_count:
            return self.code_violations_count / self.property_count
        return None


    @hybrid_property
    def police_incidents_count_per_property(self):
        if self.police_incidents_count and self.property_count:
            return self.police_incidents_count / self.property_count
        return None


    @hybrid_property
    def tenant_complaints_count_per_property(self):
        if self.tenant_complaints_count and self.property_count:
            return self.tenant_complaints_count / self.property_count
        return None


    @hybrid_property
    def eviction_count_per_property(self):
        if self.eviction_count and self.property_count:
            return self.eviction_count / self.property_count
        return None


    @hybrid_property
    def code_violations_count_per_unit(self):
        if self.code_violations_count and self.unit_count:
            return self.code_violations_count / self.unit_count
        return None


    @hybrid_property
    def police_incidents_count_per_unit(self):
        if self.police_incidents_count and self.unit_count:
            return self.police_incidents_count / self.unit_count
        return None


    @hybrid_property
    def tenant_complaints_count_per_unit(self):
        if self.tenant_complaints_count and self.unit_count:
            return self.tenant_complaints_count / self.unit_count
        return None


    @hybrid_property
    def eviction_count_per_unit(self):
        if self.eviction_count and self.unit_count:
            return self.eviction_count / self.unit_count
        return None

    def __repr__(self):
        return '<Landlord %r>' % self.name

    def as_dict(self) -> {}:
        dict_ = {}
        for key in self.__mapper__.c.keys():
            if not key.startswith('_'):
                dict_[key] = getattr(self, key)

        for key, prop in inspect(self.__class__).all_orm_descriptors.items():
            if isinstance(prop, hybrid_property):
                dict_[key] = getattr(self, key)
        return dict_


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
    police_incidents_count = db.Column(db.Integer) ######
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    unsafe_unfit_count = db.Column(db.Integer) ######
    group_id = db.Column(db.String(50), db.ForeignKey("staging_landlord.group_id"))
    unit_count = db.Column(db.Integer)
    has_rop = db.Column(db.Boolean)
    

    def __repr__(self):
        return '<Property %r>' % self.address

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

