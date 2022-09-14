from flask import Flask, render_template, flash, request, redirect
from sqlalchemy.sql import func
from models import db, Landlord, Property
from forms import LandlordSearchForm
from decimal import Decimal
import os
import math


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)


GRADE_COLORS = {
  'A': "2cba00",
  'B': "2cba00",
  'C': "ffa700",
  'D': "ffa700",
  'F': "ff0000",
}


LANDLORD_SIZES = [
    (10, {"size": "Very Large (More than 10 properties owned)", "color": "ff0000"}),
    (4, {"size": "Large (Between 5 and 10 properties owned)", "color": "ff0000"}),
    (1, {"size": "Medium (Between 1 and 4 properties owned)", "color": "ffa700"}),
    (0, {"size": "Small (One property owned)", "color": "2cba00"}),
]

GRADE_A = {"grade":"A", "value":4, "color":GRADE_COLORS["A"]}
GRADE_B = {"grade":"B", "value":3, "color":GRADE_COLORS["B"]}
GRADE_C = {"grade":"C", "value":2, "color":GRADE_COLORS["C"]}
GRADE_D = {"grade":"D", "value":1, "color":GRADE_COLORS["D"]}
GRADE_F = {"grade":"F", "value":0, "color":GRADE_COLORS["F"]}


GRADE_COMPONENTS = [
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
        stats["{}_grade_value".format(component)] = grade_and_color["value"]


def replace_none_with_zero(some_dict):
    return { k: (0 if v is None else v) for k, v in some_dict.items() }


def get_std_devs(value, average, std_dev):
    return (average - value) / std_dev


def get_grade_and_color_from_std_devs(std_devs):
    if std_devs <= -2:
        return GRADE_F
    elif std_devs <= -1:
        return GRADE_D
    elif std_devs >= 2:
        return GRADE_A
    elif std_devs >= 1:
        return GRADE_B
    else:
        return GRADE_C


def get_letter_grade_and_color(value):
    base = math.floor(value)
    if base == 0:
        letter = "F"
    elif base == 1:
        letter = "D"
    elif base == 2:
        letter = "C"
    elif base == 3:
        letter = "B"
    else:
        letter = "A"

    remainder = value - base
    if remainder < (1.0/3.0):
        modifier = "-"
    elif remainder > (2.0/3.0):
        modifier = "+"
    else:
        modifier = ""

    # No modifiers for F or A
    if letter == "F" or letter == "A":
        modifier = ""

    return {"grade": "{}{}".format(letter, modifier), "color":GRADE_COLORS[letter]}

def calculate_landlord_score(stats):
    total_score = 0
    for component in GRADE_COMPONENTS:
        total_score = total_score + stats["{}_grade_value".format(component)]

    grade_score = float(total_score) / len(GRADE_COMPONENTS) 

    return get_letter_grade_and_color(grade_score)



def get_stats_grade_and_color(value, average, std_dev):
    if value == 0:
        return GRADE_A

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


# This function sets the property count to whichever is higher between the reported property count and the properties associated
def adjust_landlord_property_count(landlord, properties):
    properties_associated = len(properties)
    if properties_associated > landlord["property_count"]:
        landlord["property_count"] = properties_associated

    return landlord


def add_landlord_size(landlord):
    for (size, attributes) in LANDLORD_SIZES:
        if landlord["property_count"] > size:
            landlord["size"] = attributes["size"]
            landlord["size_color"] = attributes["color"]
            break

    return landlord


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

    landlord = dict(landlord)

    properties_list = []
    for prop in Property.query.filter_by(owner_id=id):
        properties_list.append(prop.as_dict())

    landlord = adjust_landlord_property_count(landlord, properties_list)
    landlord = add_scaled_landlord_stats(landlord)
    landlord = add_landlord_size(landlord)
    landlord = replace_none_with_zero(landlord)

    add_grade_and_color(stats, landlord)
    landlord_score = calculate_landlord_score(stats)

    return render_template('landlord.html', landlord=landlord, properties=properties_list, 
        stats=stats, landlord_score=landlord_score)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    landlord = Landlord.query.filter_by(id=property.owner_id).first()
    return render_template('property.html', property=property, landlord=landlord)
