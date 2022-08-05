from flask import Flask, render_template
from models import db, Landlord, Property
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)

@app.route("/")
def home():
    landlords = Landlord.query.all()
    return render_template('all_landlords.html', landlords=landlords)


@app.route('/landlord/<id>')
def landlord(id):
    landlord = Landlord.query.filter_by(id=id).first()
    properties = Property.query.filter_by(owner_id=id)
    return render_template('landlord.html', landlord=landlord, properties=properties)


@app.route('/property/<id>')
def property(id):
    property = Property.query.filter_by(id=id).first()
    return render_template('property.html', property=property)
