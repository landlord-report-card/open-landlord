from flask import Flask, render_template, flash, request, redirect
from sqlalchemy.sql import func
from models import db, Landlord, Property
from forms import LandlordSearchForm
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)


PROGRESS_RED = "ff0000"
PROGRESS_ORANGE = "ffa700"
PROGRESS_YELLOW = "fff400"
PROGRESS_LIGHT_GREEN = "a3ff00"
PROGRESS_DARK_GREEN = "2cba00"


GRADE_COMPONENTS = [
    "property_count",
    "tenant_complaints",
    "code_violations",
    "police_incidents",
]

def add_coloring(stats, landlord):
    for component in GRADE_COMPONENTS:
        stats["{}_color".format(component)] = get_stats_color(landlord[component], stats["average_{}".format(component)], stats["{}_std_dev".format(component)])


def replace_none_with_zero(some_dict):
    return { k: (0 if v is None else v) for k, v in some_dict.items() }


def get_std_devs(value, average, std_dev):
    return (average - value) / std_dev


def get_net_std_devs(stats, landlord):
    total = 0
    for component in GRADE_COMPONENTS:
        total = total + get_std_devs(landlord[component], stats["average_{}".format(component)], stats["{}_std_dev".format(component)])
    return total


def calculate_landlord_score(stats, landlord):
    std_devs = get_net_std_devs(stats, landlord)

    if std_devs <= 2:
        return {"grade":"F", "color":PROGRESS_RED}
    elif std_devs <= 1:
        return {"grade":"D", "color":PROGRESS_ORANGE}
    elif std_devs >= 2:
        return {"grade":"A", "color":PROGRESS_DARK_GREEN}
    elif std_devs >= 1:
        return {"grade":"B", "color":PROGRESS_LIGHT_GREEN}
    else:
        return {"grade":"C", "color":PROGRESS_YELLOW}


def get_stats_color(value, average, std_dev):
    if value is 0:
        return PROGRESS_DARK_GREEN

    if (average - value) < (-2 * std_dev):
        return PROGRESS_RED
    elif (average - value) < (-1 * std_dev):
        return PROGRESS_ORANGE
    elif (average - value) > (2 * std_dev):
        return PROGRESS_DARK_GREEN
    elif (average - value) > (1 * std_dev):
        return PROGRESS_LIGHT_GREEN
    else:
        return PROGRESS_ORANGE

def get_stats():
    ll_stats = get_landlord_stats()
    property_stats = get_property_stats()
    ll_stats.update(property_stats)
    return ll_stats

def get_landlord_stats():
    stats_row = Landlord.query.with_entities(
        func.avg(Landlord.property_count).label('average_property_count'),
        func.stddev(Landlord.property_count).label('property_count_std_dev'),
    ).first()

    stats = dict(stats_row)
    return stats


def get_property_stats():
    stats_row = Landlord.query.with_entities(
        func.avg(Property.tenant_complaints).label('average_tenant_complaints'),
        func.avg(Property.code_violations_count).label('average_code_violations'),
        func.avg(Property.police_incidents_count).label('average_police_incidents'),
        func.stddev(Property.tenant_complaints).label('tenant_complaints_std_dev'),
        func.stddev(Property.code_violations_count).label('code_violations_std_dev'),
        func.stddev(Property.police_incidents_count).label('police_incidents_std_dev'),
    ).first()

    stats = dict(stats_row)
    return stats


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
    stats = get_stats()

    landlord = Landlord.query.filter_by(id=id).with_entities(
        func.sum(Property.service_call_count).label('service_call_count'),
        func.sum(Property.code_violations_count).label('code_violations'),
        func.sum(Property.tenant_complaints).label('tenant_complaints'),
        func.sum(Property.health_violation_count).label('health_violation_count'),
        func.sum(Property.police_incidents_count).label('police_incidents'), 
        *group_by_properties).join(Property, Landlord.id==Property.owner_id).group_by(*group_by_properties).first()
    properties = Property.query.filter_by(owner_id=id)

    landlord = replace_none_with_zero(dict(landlord))

    add_coloring(stats, landlord)
    landlord_score = calculate_landlord_score(stats, landlord)

    return render_template('landlord.html', landlord=landlord, properties=properties, 
        stats=stats, landlord_score=landlord_score)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    return render_template('property.html', property=property)
