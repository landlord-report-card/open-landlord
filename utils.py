from decimal import Decimal
from datetime import date, timedelta
from models import db, Landlord, Property, Alias, Eviction, CodeCase
from sqlalchemy.sql import func
from sqlalchemy import or_
from num2words import num2words
import usaddress
import re
import constants
import math
import utils
import statistics


class PaginatedResults:
    def __init__(self, items, total):
        self.items = items
        self.total = total


def get_landlord(landlord_id):
    return Landlord.query.filter_by(id=landlord_id).first()


def get_all_aliases(landlord_id):
    return Alias.query.filter_by(landlord_id=landlord_id).all()

def get_all_properties_dict(landlord_id):
    properties = Property.query.filter(Property.owner_id == landlord_id).all()
    return [prop.as_dict() for prop in properties]


def get_landlord_stats(landlord_id, properties_list, city_average_stats):
    landlord_stats = Landlord.query.get(landlord_id)

    landlord_stats = landlord_stats.as_dict()
    landlord_stats = add_grade_and_color(landlord_stats, city_average_stats)
    landlord_stats = replace_none_with_zero(landlord_stats)

    return landlord_stats


def get_enriched_landlord(landlord_id):
    landlord = get_landlord(landlord_id).as_dict()
    landlord = replace_none_with_zero(landlord)
    return landlord

def add_grade_and_color(landlord_stats, average_stats):
    for component in constants.GRADE_COMPONENTS:
        grade_and_color = get_stats_grade_and_color(landlord_stats[f"{component}_per_unit"],
                                                    average_stats[f"mean_{component}_per_unit"], 
                                                    average_stats[f"std_dev_{component}"])

        landlord_stats["{}_color".format(component)] = grade_and_color["color"]
        landlord_stats["{}_grade".format(component)] = grade_and_color["grade"]
        landlord_stats["{}_grade_value".format(component)] = grade_and_color["value"]
    return landlord_stats


def replace_none_with_zero(some_dict):
    return { k: (0 if v is None else v) for k, v in some_dict.items() }


def get_std_devs(value, average, std_dev):
    if value is None:
        value = 0.0
    return (average - value) / std_dev


def get_grade_and_color_from_std_devs(std_devs):
    if std_devs <= -1.5:
        return constants.GRADE_F
    elif std_devs <= -.5:
        return constants.GRADE_D
    elif std_devs >= 1.5:
        return constants.GRADE_A
    elif std_devs >= 0.5:
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

def landlords_with_unit_count_query():
    two_years_ago = date.today() - timedelta(days=730) 
    return CodeCase.query\
        .with_entities(Property.group_id, func.sum(CodeCase.number_of_units_to_receive_rops).label('units_with_rop'))\
        .outerjoin(Property, Property.parcel_id==CodeCase.parcel_id)\
        .filter(CodeCase.final_date >= two_years_ago)\
        .filter(CodeCase.case_type == constants.ROP_TYPE)\
        .filter(CodeCase.case_status == 'Closed')\
        .filter(CodeCase.number_of_units_to_receive_rops != None)\
        .group_by(Property.group_id)


def get_landlord_unit_count(group_id):
    value = landlords_with_unit_count_query().filter_by(group_id=group_id).first()
    if value is None:
        return None
    return value[1]

def get_all_landlords_with_unit_count():
    landlords_and_count = landlords_with_unit_count_query().all()
    return {group_id: unitcount for group_id, unitcount in landlords_and_count}


def evictions_query():
    one_year_ago = date.today() - timedelta(days=365) 
    return Eviction.query\
        .with_entities(Alias.group_id, func.count(Eviction.id).label('eviction_count'))\
        .filter(Eviction.case_date >= one_year_ago)\
        .join(Alias, Eviction.matched_name==Alias.name)\
        .group_by(Alias.group_id)

def get_all_evictions_by_group_id():
    return evictions_query().all()

def get_evictions_for_group(group_id):
    value = evictions_query().filter_by(group_id=group_id).first()
    if value is None:
        return 0
    return value[1]


def code_violations_query():
    one_year_ago = date.today() - timedelta(days=365) 
    return CodeCase.query\
        .with_entities(Property.group_id, func.count(CodeCase.case_id).label('code_violation_count'))\
        .filter(CodeCase.apply_date >= one_year_ago)\
        .filter(CodeCase.case_type == constants.CODE_VIOLATIONS_TYPE)\
        .join(Property, Property.parcel_id==CodeCase.parcel_id)\
        .group_by(Property.group_id)

def get_all_code_violations_by_group_id():
    return code_violations_query().all()

def get_code_violations_for_group(group_id):
    value = code_violations_query().filter_by(group_id=group_id).first()
    if value is None:
        return 0
    return value[1]

def get_landlord_stats(group_id):
    units_for_group = get_landlord_unit_count(group_id)
    total_evictions = get_evictions_for_group(group_id)
    total_code_violations = get_code_violations_for_group(group_id)

    denominator = 1 if units_for_group is None else units_for_group

    return {
        "unit_count": units_for_group,
        "evictions_count": total_evictions,
        "code_violations_count": total_code_violations,
        "evictions_per_unit":  total_evictions / denominator,
        "code_violations_per_unit":  total_code_violations / denominator
    }

def get_city_average_stats():
    one_year_ago = date.today() - timedelta(days=365) 
    total_eviction_count = Eviction.query.filter(Eviction.case_date >= one_year_ago).count()
    total_code_violation_count = CodeCase.query.filter(CodeCase.apply_date >= one_year_ago).filter(CodeCase.case_type == constants.CODE_VIOLATIONS_TYPE).count()
    landlords_with_counts = get_all_landlords_with_unit_count()
    total_unit_count = sum(landlords_with_counts.values())

    evictions_by_group = get_all_evictions_by_group_id()

    eviction_counts_per_unit = []
    for group_id, eviction_count in evictions_by_group:
        if group_id in landlords_with_counts:
            eviction_counts_per_unit.append(eviction_count/landlords_with_counts[group_id])
        else:
            eviction_counts_per_unit.append(eviction_count)
    stddev_eviction_counts = statistics.stdev(eviction_counts_per_unit)

    code_violations_by_group = get_all_code_violations_by_group_id()

    code_violations_per_unit = []
    for group_id, code_violation_count in code_violations_by_group:
        if group_id in landlords_with_counts and landlords_with_counts[group_id] > 0:
            code_violations_per_unit.append(code_violation_count/landlords_with_counts[group_id])
        else:
            code_violations_per_unit.append(code_violation_count)

    stddev_code_violation_counts = statistics.stdev(code_violations_per_unit)

    return {
        "mean_evictions_per_unit": total_eviction_count / total_unit_count,
        "mean_code_violations_per_unit": total_code_violation_count / total_unit_count,
        "std_dev_evictions": stddev_eviction_counts,
        "std_dev_code_violations": stddev_code_violation_counts,
    }


def replace_ordinals(text):
    match = re.search('((\d+)(st|nd|rd|th))', text) 
    
    if match != None: 
        number = int(match.group(2))
        ordinalAsString = num2words(number, ordinal=True)
        text = text.replace(match.group(1), ordinalAsString)

    return text


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
    filter_criteria = Alias.name.ilike("%{}%".format(search_string))
    return filter_criteria


def perform_search(text, max_results):
    filter_criteria = get_address_filter_criteria(text) | get_landlord_filter_criteria(text)

    results = Property.query.filter(filter_criteria).join(Alias, Alias.group_id==Property.group_id).order_by(Property.address).limit(max_results)
    return results


def get_unsafe_unfit_properties(landlord_id):
    return Property.query.filter(Property.owner_id == landlord_id).filter(Property.unsafe_unfit_count > 0).all()


def sort_landlords_by_grade(sort_direction, page_number, page_size):
    landlord_list = []
    landlord_objects = Landlord.query.all()
    city_stats = utils.get_city_average_stats()

    for landlord in landlord_objects:
        landlord = landlord.as_dict()
        grades = utils.add_grade_and_color(landlord, city_stats)
        grades.update(utils.calculate_landlord_score(grades))

        landlord["grade"] = grades["grade"]
        landlord_list.append(landlord)

    reverse = False if sort_direction == "asc" else True
    landlord_list.sort(key=lambda x: x["grade"], reverse=reverse)

    first_result = (page_number-1) * page_size
    return PaginatedResults(landlord_list[first_result:first_result + page_size], len(landlord_list))


# TODO: Fix this function
def get_ranked_landlords(sort_by, sort_direction, page_number, page_size):
    if sort_by == "grade":
        return sort_landlords_by_grade(sort_direction, page_number, page_size)

    ranking_criteria = getattr(Landlord, sort_by)
    if sort_direction == "asc":
        results = Landlord.query.order_by(ranking_criteria.is_(None), ranking_criteria.asc()).paginate(page_number, page_size)
    else:
        results = Landlord.query.order_by(ranking_criteria.is_(None), ranking_criteria.desc()).paginate(page_number, page_size)
    landlord_list = []
    city_stats = utils.get_city_average_stats()
    for landlord in results.items:
        landlord = landlord.as_dict()
        grades = utils.add_grade_and_color(landlord, city_stats)
        grades.update(utils.calculate_landlord_score(grades))

        landlord["grade"] = grades["grade"]
        landlord_list.append(landlord)

    return PaginatedResults(landlord_list, results.total)
