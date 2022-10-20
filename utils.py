from decimal import Decimal
from models import db, Landlord, Property
from sqlalchemy.sql import func
from sqlalchemy import or_
from num2words import num2words
import usaddress
import re
import constants
import math
import utils


def get_landlord(landlord_id):
    return Landlord.query.filter_by(id=landlord_id).first()


def get_group_id(landlord_id):
    current_landlord = Landlord.query.filter_by(id=landlord_id).first()
    return current_landlord.group_id


def get_all_landlords(landlord_id):
    group_id = get_group_id(landlord_id)
    if group_id is not None:
        return Landlord.query.filter(or_(Landlord.id==landlord_id, Landlord.group_id==group_id)).all()
    return Landlord.query.filter(Landlord.id==landlord_id).all()


def get_all_aliases(landlord_id):
    landlords = get_all_landlords(landlord_id)
    aliases = []
    
    for landlord in landlords:
        if int(landlord.id) != int(landlord_id):
            aliases.append(landlord.name)

    return aliases


def get_all_evictions(landlord_id):
    landlords = get_all_landlords(landlord_id)
    landlord_ids = [landlord.id for landlord in landlords]
    evictions_query = Landlord.query.filter(Landlord.id.in_(landlord_ids)).with_entities(
        func.sum(Landlord.eviction_count).label('total_eviction_count')).first()

    return evictions_query["total_eviction_count"]


def get_all_properties(landlord_id):
    landlords = get_all_landlords(landlord_id)
    landlord_ids = [landlord.id for landlord in landlords]
    return Property.query.filter(Property.owner_id.in_(landlord_ids)).all()


def get_all_properties_dict(landlord_id):
    properties = get_all_properties(landlord_id)
    return [prop.as_dict() for prop in properties]


def get_landlord_stats(landlord_id, properties_list, city_average_stats):
    property_ids = [prop["id"] for prop in properties_list]
    landlord_stats = Property.query.filter(Property.id.in_(property_ids)).with_entities(
            func.sum(Property.service_call_count).label('service_call_count'),
            func.sum(Property.code_violations_count).label('code_violations_total'),
            func.sum(Property.tenant_complaints).label('tenant_complaints_total'),
            func.sum(Property.health_violation_count).label('health_violation_count'),
            func.sum(Property.police_incidents_count).label('police_incidents_total')).first()

    landlord_stats = dict(landlord_stats)
    landlord_stats["eviction_count_total"] = get_all_evictions(landlord_id)
    landlord_stats = add_scaled_landlord_stats(landlord_stats, len(properties_list))
    landlord_stats = add_grade_and_color(landlord_stats, city_average_stats)
    landlord_stats = replace_none_with_zero(landlord_stats)

    return landlord_stats


def get_enriched_landlord(landlord_id, properties_list):
    landlord = get_landlord(landlord_id).as_dict()
    landlord = adjust_landlord_property_count(landlord, properties_list)
    landlord = add_landlord_size(landlord)
    landlord = replace_none_with_zero(landlord)
    return landlord

def add_grade_and_color(landlord_stats, average_stats):
    for component in constants.GRADE_COMPONENTS:
        grade_and_color = get_stats_grade_and_color(landlord_stats[component],
                                                    average_stats["average_{}".format(component)], 
                                                    average_stats["{}_std_dev".format(component)])

        landlord_stats["{}_color".format(component)] = grade_and_color["color"]
        landlord_stats["{}_grade".format(component)] = grade_and_color["grade"]
        landlord_stats["{}_grade_value".format(component)] = grade_and_color["value"]
    return landlord_stats


def replace_none_with_zero(some_dict):
    return { k: (0 if v is None else v) for k, v in some_dict.items() }


def get_std_devs(value, average, std_dev):
    if value is None:
        value = Decimal(0)
    return (average - value) / std_dev


def get_grade_and_color_from_std_devs(std_devs):
    if std_devs <= -2:
        return constants.GRADE_F
    elif std_devs <= -1:
        return constants.GRADE_D
    elif std_devs >= 2:
        return constants.GRADE_A
    elif std_devs >= 1:
        return constants.GRADE_B
    else:
        return constants.GRADE_C


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

    return {"grade": "{}{}".format(letter, modifier), "color":constants.GRADE_COLORS[letter]}

def calculate_landlord_score(stats):
    total_score = 0
    has_failing_grade = False
    for component in constants.GRADE_COMPONENTS:
        component_score = stats["{}_grade_value".format(component)]
        total_score = total_score + component_score
        if component_score < 2:
            has_failing_grade = True

    grade_score = float(total_score) / len(constants.GRADE_COMPONENTS)

    # If there is a failing component (e.g. a D or F), then the max overall grade should be C
    if has_failing_grade and grade_score >= 3.0:
        grade_score = 2.5

    return get_letter_grade_and_color(grade_score)



def get_stats_grade_and_color(value, average, std_dev):
    if value == 0 or value is None:
        return constants.GRADE_A

    std_devs = get_std_devs(value, average, std_dev)
    grade_and_color = get_grade_and_color_from_std_devs(std_devs)
    return grade_and_color



def add_scaled_landlord_stats(stats, property_count):
    for stat in constants.STATS_TO_SCALE:
        total_stat = stats["{}_total".format(stat)]
        if total_stat is None:
            stats[stat] = total_stat
        else:
            stats[stat] = Decimal(float(total_stat) / float(property_count))
    return stats


def get_city_average_stats():
    property_stats_row = Property.query.with_entities(
        func.avg(Property.tenant_complaints).label('average_tenant_complaints'),
        func.avg(Property.code_violations_count).label('average_code_violations'),
        func.avg(Property.police_incidents_count).label('average_police_incidents'),
        func.stddev(Property.tenant_complaints).label('tenant_complaints_std_dev'),
        func.stddev(Property.code_violations_count).label('code_violations_std_dev'),
        func.stddev(Property.police_incidents_count).label('police_incidents_std_dev'),
    ).first()

    landlord_stats_row = Landlord.query.with_entities(
        func.avg(Landlord.eviction_count).label('average_eviction_count'),
        # Note: This is a workaround, not a bug. We can't calculate standard deviation in the same way here, because
        # we don't have per property eviction data. So we use the citywide average as our "standard deviation", because
        # it will assign a D to anyone worse than citywide average, and F to anyone double citywide average.
        func.avg(Landlord.eviction_count).label('eviction_count_std_dev'),
    ).first()

    property_stats = dict(property_stats_row)
    landlord_stats = dict(landlord_stats_row)
    property_stats.update(landlord_stats)

    return property_stats


# This function sets the property count to whichever is higher between the reported property count and the properties associated
def adjust_landlord_property_count(landlord, properties):
    properties_associated = len(properties)
    if properties_associated > landlord["property_count"]:
        landlord["property_count"] = properties_associated

    return landlord


def add_landlord_size(landlord):
    for (size, attributes) in constants.LANDLORD_SIZES:
        if landlord["property_count"] > size:
            landlord["size"] = attributes["size"]
            landlord["size_color"] = attributes["color"]
            break

    return landlord


def replace_ordinals(text):
    match = re.search('((\d+)(st|nd|rd|th))', text) 
    
    if match != None: 
        number = int(match.group(2))
        ordinalAsString = num2words(number, ordinal=True)
        text = text.replace(match.group(1), ordinalAsString)

    return text


def get_autocomplete_prompts():
    properties = Property.query.all()
    landlords = Landlord.query.all()

    autocomplete_prompts = []

    for prop in properties:
        autocomplete_prompts.append(prop.address)

    for landlord in landlords:
        autocomplete_prompts.append(landlord.name)

    return autocomplete_prompts


def get_address_dict(parsed_address_tuple_list):
    address_dict = {}
    for value, field in parsed_address_tuple_list:
        address_dict[field] = value
    return address_dict


def get_address_filter_criteria(search_string):
    search_string = utils.replace_ordinals(search_string)
    parsed_address_tuple_list = usaddress.parse(search_string)
    parsed_address = get_address_dict(parsed_address_tuple_list)
    if "AddressNumber" in parsed_address and "StreetName" in parsed_address:
        filter_criteria = Property.house_number.ilike("{}".format(parsed_address["AddressNumber"])) & Property.address.ilike("%{}%".format(parsed_address["StreetName"]))
    elif "StreetName" in parsed_address:
        filter_criteria = Property.address.ilike("%{}%".format(parsed_address["StreetName"]))
    else:
        filter_criteria = Property.address.ilike("%{}%".format(search_string))

    return filter_criteria


def get_landlord_filter_criteria(search_string):
    filter_criteria = Landlord.name.ilike("%{}%".format(search_string))
    return filter_criteria


def perform_search(text):
    filter_criteria = get_address_filter_criteria(text) | get_landlord_filter_criteria(text)

    results = Property.query.filter(filter_criteria).join(Landlord, Landlord.id==Property.owner_id).add_columns(Landlord.name).order_by(Property.address)
    return results


def has_unsafe_unfit(landlord_id):
    landlords = get_all_landlords(landlord_id)
    landlord_ids = [landlord.id for landlord in landlords]
    query = Property.query.filter(Property.owner_id.in_(landlord_ids)).with_entities(
        func.sum(Property.unsafe_unfit_count).label('total_unsafe_unfit_count')).first()

    if query["total_unsafe_unfit_count"] > 0:
        return True
    return False


