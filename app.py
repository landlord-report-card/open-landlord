from flask import Flask, render_template, flash, request, redirect, send_from_directory, jsonify
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
from marshmallow import fields
from models import db, Landlord, Property, Alias, Review
from constants import SEARCH_DEFAULT_MAX_RESULTS
import os
import utils
import constants


app = Flask(__name__,static_folder='frontend/build',static_url_path='')
ma = Marshmallow(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)
CORS(app)


# Schema API initializations 
class LandlordSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Landlord
        include_fk = True
        include_relationships = True
        load_instance = True

    name = ma.auto_field()
    id = ma.auto_field()
    group_id = ma.auto_field()
    address = ma.auto_field()
    property_count = ma.auto_field()
    eviction_count = ma.auto_field()
    unit_count = ma.auto_field()
    eviction_count_per_property = fields.Float(dump_only=True)
    code_violations_count = ma.auto_field()
    code_violations_count_per_property = fields.Float(dump_only=True)
    police_incidents_count = ma.auto_field()
    police_incidents_count_per_property = fields.Float(dump_only=True)
    tenant_complaints_count = ma.auto_field()
    tenant_complaints_count_per_property = fields.Float(dump_only=True)


class PropertySchema(ma.Schema):
    class Meta:
        fields = (
            "parcel_id", 
            "address", 
            "latitude", 
            "longitude",
            "id",
            "property_type",
            "owner_id",
            "group_id",
            "tenant_complaints_count",
            "owner_occupied",
            "unsafe_unfit_count",
            "police_incidents_count",
            "current_use",
            "business_entity_type",
            "longitude",
            "code_violations_count",
            "owner_occupied",
            "business_entity_type",
            "unit_count",
            "has_rop",
        )


class AliasSchema(ma.Schema):
    class Meta:
        fields = ("name", "landlord_id")


class ReviewSchema(ma.Schema):
    class Meta:
        fields = ("id", "text", "timestamp", "landlord_alias_id", "is_approved")


LANDLORD_SCHEMA = LandlordSchema()
LANDLORDS_SCHEMA = LandlordSchema(many=True)
ALIAS_SCHEMA = AliasSchema()
ALIASES_SCHEMA = AliasSchema(many=True)
PROPERTY_SCHEMA = PropertySchema()
PROPERTIES_SCHEMA = PropertySchema(many=True)
REVIEW_SCHEMA = ReviewSchema()
REVIEWS_SCHEMA = ReviewSchema(many=True)


@app.route('/')
def serve():
    return app.send_static_file('index.html')


@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

# API Definitions


@app.route('/api/landlords/top/', methods=['GET'])
@cross_origin()
def get_top_landlords():
    pageSize = int(request.args.get('pageSize')) if request.args.get('pageSize') else constants.DEFAULT_PAGE_SIZE
    pageNumber = int(request.args.get('pageNumber')) if request.args.get('pageNumber') else constants.DEFAULT_PAGE_NUMBER
    sortBy = request.args.get('sortBy').lower() if request.args.get('sortBy') else constants.DEFAULT_SORT_BY
    sortDirection = request.args.get('sortDirection') if request.args.get('sortDirection') else constants.DEFAULT_SORT_DIRECTION

    landlords_paginated = utils.get_ranked_landlords(sortBy, sortDirection, pageNumber, pageSize)

    return jsonify({"total_results": landlords_paginated.total, "landlords": landlords_paginated.items})


@app.route('/api/landlords/<group_id>', methods=['GET'])
@cross_origin()
def get_landlord(group_id):
    return LANDLORD_SCHEMA.jsonify(Landlord.query.filter_by(group_id=group_id).first())


@app.route('/api/landlords/', methods=['POST'])
@cross_origin()
def get_landlords_bulk():
    response_json = request.get_json()
    landlord_ids = response_json["ids"] if "ids" in response_json else []
    landlords = Landlord.query.filter(Landlord.group_id.in_(landlord_ids)).all()
    aliases = Alias.query.filter(Alias.group_id.in_(landlord_ids)).all()
    landlord_map = {}
    for landlord in landlords:
        landlord_map[landlord.group_id] = landlord.as_dict()
        alias_names = ', '.join([alias.name for alias in aliases if alias.group_id == landlord.group_id and alias.name != landlord.name])
        landlord_map[landlord.group_id]["aliases"] = alias_names

    return jsonify(landlord_map)


@app.route('/api/landlords/<group_id>/aliases', methods=['GET'])
@cross_origin()
def get_landlord_aliases(group_id):
    aliases = Alias.query.filter_by(group_id=group_id).all()
    return ALIASES_SCHEMA.jsonify(aliases)


@app.route('/api/landlords/<group_id>/grades', methods=['GET'])
@cross_origin()
def get_landlord_grades(group_id):
    landlord = Landlord.query.filter_by(group_id=group_id).first().as_dict()
    stats = utils.get_city_average_stats()
    grades = utils.add_grade_and_color(landlord, stats)
    grades.update(utils.calculate_landlord_score(grades))
    return jsonify(grades)


@app.route('/api/landlords/<group_id>/properties', methods=['GET'])
@cross_origin()
def get_landlord_properties(group_id):
    properties = Property.query.filter_by(group_id=group_id).all()
    return PROPERTIES_SCHEMA.jsonify(properties)


@app.route('/api/landlords/<group_id>/unsafe_unfit', methods=['GET'])
@cross_origin()
def get_landlord_unsafe_unfit_properties(group_id):
    properties = Property.query.filter(Property.group_id == group_id).filter(Property.unsafe_unfit_count > 0).all()
    return PROPERTIES_SCHEMA.jsonify(properties)


@app.route('/api/reviews/landlord/<group_id>', methods=['GET'])
@cross_origin()
def get_landlord_reviews(group_id):
    aliases = Alias.query.filter_by(group_id=group_id).all()
    group_ids = [alias.group_id for alias in aliases]
    reviews = Review.query.filter(Landlord.group_id.in_(group_ids)).all()
    return REVIEWS_SCHEMA.jsonify(reviews)


@app.route('/api/reviews/alias', methods=['POST'])
@cross_origin()
def create_landlord_review():
    try:
        data = request.get_json()
        print(data)
        db.session.add(Review(**data))
        db.session.commit()
        db.session.close()

        return jsonify({'message': 'Object created successfully.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/stats', methods=['GET'])
@cross_origin()
def get_city_stats():
    stats = utils.get_city_average_stats()
    return stats


@app.route('/api/search', methods=['GET'])
@cross_origin()
def get_search_results():
    max_results = request.args.get('max_results') if request.args.get('max_results') else SEARCH_DEFAULT_MAX_RESULTS
    search_string = request.args.get('query') if request.args.get('query') else ""
    return PROPERTIES_SCHEMA.jsonify(utils.perform_search(search_string, max_results).all())
    

@app.route('/api/properties/<id>', methods=['GET'])
@cross_origin()
def get_property(id):
    return PROPERTY_SCHEMA.jsonify(Property.query.get(id))


if __name__ == '__main__':
    app.run(host='0.0.0.0')