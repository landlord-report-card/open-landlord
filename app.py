from flask import Flask, render_template, flash, request, redirect
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
    landlord = Landlord.query.filter_by(id=id).first()
    properties = Property.query.filter_by(owner_id=id)
    return render_template('landlord.html', landlord=landlord, properties=properties)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    return render_template('property.html', property=property)
