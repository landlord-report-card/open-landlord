from flask import Flask, render_template
from models import db, Landlord
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['LANDLORD_DATABASE_URI']
db.init_app(app)

@app.route("/")
def home():
    landlords = Landlord.query.all()
    return render_template('landlord.html', landlords=landlords)


@app.route('/landlord/<id>')
def show_user_profile(id):
    landlord = Landlord.query.filter_by(id=id).first()
    return "<p>{} has {} properties.</p>".format(landlord.name, landlord.property_count)
