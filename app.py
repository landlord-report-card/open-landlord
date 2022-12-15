from flask import Flask, render_template, flash, request, redirect
from flask_marshmallow import Marshmallow
from models import db, Landlord, Property
from forms import LandlordSearchForm
import os
import utils


app = Flask(__name__)
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)


# Schema API initializations 
class LandlordSchema(ma.Schema):
    class Meta:
        fields = ("name", "address", "property_count")


class PropertySchema(ma.Schema):
    class Meta:
        fields = ("parcel_id", "address", "latitude", "longitude")


LANDLORD_SCHEMA = LandlordSchema()
LANDLORDS_SCHEMA = LandlordSchema(many=True)
PROPERTY_SCHEMA = PropertySchema()
PROPERTIES_SCHEMA = PropertySchema(many=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    search = LandlordSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('index.html', form=search, autocomplete_prompts=utils.get_autocomplete_prompts())


@app.route('/results')
def search_results(search):
    results = utils.perform_search(search.data['search'])
    return render_template('index.html', results=results, form=search, autocomplete_prompts=utils.get_autocomplete_prompts())


@app.route('/landlord/<id>')
def landlord(id):
    properties_list = utils.get_all_properties_dict(id)
    aliases = utils.get_all_aliases(id)
    landlord = utils.get_enriched_landlord(id, properties_list)
    city_average_stats = utils.get_city_average_stats()
    landlord_stats = utils.get_landlord_stats(id, properties_list, city_average_stats)
    landlord_score = utils.calculate_landlord_score(landlord_stats)
    unsafe_unfit_list = utils.get_unsafe_unfit_properties(id)

    return render_template('landlord.html', landlord=landlord, properties=properties_list, landlord_stats=landlord_stats, 
        city_average_stats=city_average_stats, landlord_score=landlord_score, aliases=aliases, unsafe_unfit_list=unsafe_unfit_list)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    landlord = Landlord.query.filter_by(id=property.owner_id).first()
    return render_template('property.html', property=property.as_dict(), landlord=landlord.as_dict())


@app.route('/faq/')
def faq():
    return render_template('faq.html')

@app.route('/action/')
def action():
    return render_template('action.html')


@app.route('/about/')
def about():
    return render_template('about.html')


# API Definitions
def get_biggest_landlords(limit):
    landlords = Landlord.query.order_by(Landlord.property_count.desc()).limit(limit).all()
    return landlords


@app.route('/api/landlords/top/', methods=['GET'])
def get_top_landlords():
    max_results = 50
    if request.args.get('max_results'):
        max_results = request.args.get('max_results')

    landlords = get_biggest_landlords(max_results)
    return LANDLORDS_SCHEMA.jsonify(landlords)


@app.route('/api/landlords/<id>', methods=['GET'])
def get_landlord(id):
    return LANDLORD_SCHEMA.jsonify(Landlord.query.get(id))


@app.route('/api/properties/<id>', methods=['GET'])
def get_property(id):
    return PROPERTY_SCHEMA.jsonify(Property.query.get(id))
