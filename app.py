from flask import Flask, render_template, flash, request, redirect
from sqlalchemy.sql import func
from models import db, Landlord, Property
from forms import LandlordSearchForm
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    search = LandlordSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)
    return render_template('index.html', form=search)


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']
    results = Property.query.filter(Property.address.ilike("%{}%".format(search_string))).join(Landlord, Landlord.id==Property.owner_id).add_columns(Landlord.name)
    return render_template('index.html', results=results, form=search)


@app.route('/landlord/<id>')
def landlord(id):
    group_by_properties = (Landlord.name, Landlord.address, Landlord.location, Landlord.property_count)
    landlord = Landlord.query.filter_by(id=id).with_entities(
        func.sum(Property.service_call_count).label('service_call_count'),
        func.sum(Property.code_violations_count).label('code_violations_count'),
        func.sum(Property.tenant_complaints).label('tenant_complaints'),
        func.sum(Property.health_violation_count).label('health_violation_count'),
        func.sum(Property.rental_registry_count).label('rental_registry_count'),
        func.sum(Property.rental_code_cases).label('rental_code_cases'), 
        *group_by_properties).join(Property, Landlord.id==Property.owner_id).group_by(*group_by_properties).first()
    properties = Property.query.filter_by(owner_id=id)
    return render_template('landlord.html', landlord=landlord, properties=properties)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    return render_template('property.html', property=property)
