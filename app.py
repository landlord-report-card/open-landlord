from flask import Flask, render_template, flash, request, redirect
from models import db, Landlord, Property
from forms import LandlordSearchForm
import os
import utils


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)


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


@app.route('/about/')
def about():
    return render_template('about.html')
