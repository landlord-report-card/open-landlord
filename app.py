from flask import Flask, render_template, flash, request, redirect
from sqlalchemy.sql import func
from models import db, Landlord, Property
from forms import LandlordSearchForm
from decimal import Decimal
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)


GRADE_COLORS = {
  'A': "2cba00",
  'B': "a3ff00",
  'C': "fff400",
  'D': "ffa700",
  'F': "ff0000",
}

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

STATS_TO_SCALE = [
    "tenant_complaints",
    "code_violations",
    "police_incidents",
]

def add_grade_and_color(stats, landlord):
    for component in GRADE_COMPONENTS:
        grade_and_color = get_stats_grade_and_color(landlord[component],
                                                    stats["average_{}".format(component)], 
                                                    stats["{}_std_dev".format(component)])
        stats["{}_color".format(component)] = grade_and_color["color"]
        stats["{}_grade".format(component)] = grade_and_color["grade"]


def replace_none_with_zero(some_dict):
    return { k: (0 if v is None else v) for k, v in some_dict.items() }


def get_std_devs(value, average, std_dev):
    return (average - value) / std_dev


def get_net_std_devs(stats, landlord):
    total = 0
    for component in GRADE_COMPONENTS:
        total = total + get_std_devs(landlord[component], 
                                     stats["average_{}".format(component)], 
                                     stats["{}_std_dev".format(component)])
    return total


def get_grade_and_color_from_std_devs(std_devs):
    if std_devs <= -2:
        return {"grade":"F", "color":GRADE_COLORS["F"]}
    elif std_devs <= -1:
        return {"grade":"D", "color":GRADE_COLORS["D"]}
    elif std_devs >= 2:
        return {"grade":"A", "color":GRADE_COLORS["A"]}
    elif std_devs >= 1:
        return {"grade":"B", "color":GRADE_COLORS["B"]}
    else:
        return {"grade":"C", "color":GRADE_COLORS["C"]}


def calculate_landlord_score(stats, landlord):
    std_devs = get_net_std_devs(stats, landlord)
    return get_grade_and_color_from_std_devs(std_devs)


def get_stats_grade_and_color(value, average, std_dev):
    if value is 0:
        return {"grade":"A", "color":GRADE_COLORS["A"]}

    std_devs = get_std_devs(value, average, std_dev)
    grade_and_color = get_grade_and_color_from_std_devs(std_devs)
    return grade_and_color


def add_scaled_landlord_stats(stats):
    for stat in STATS_TO_SCALE:
        total_stat = stats["{}_total".format(stat)]
        if total_stat is None:
            stats[stat] = total_stat
        else:
            stats[stat] = Decimal(float(total_stat) / float(stats["property_count"]))
    return stats


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
        func.sum(Property.code_violations_count).label('code_violations_total'),
        func.sum(Property.tenant_complaints).label('tenant_complaints_total'),
        func.sum(Property.health_violation_count).label('health_violation_count'),
        func.sum(Property.police_incidents_count).label('police_incidents_total'), 
        *group_by_properties).join(Property, Landlord.id==Property.owner_id).group_by(*group_by_properties).first()

    landlord = add_scaled_landlord_stats(dict(landlord))
    properties = Property.query.filter_by(owner_id=id)

    landlord = replace_none_with_zero(landlord)

    add_grade_and_color(stats, landlord)
    landlord_score = calculate_landlord_score(stats, landlord)

    return render_template('landlord.html', landlord=landlord, properties=properties, 
        stats=stats, landlord_score=landlord_score)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    return render_template('property.html', property=property)
