import requests
from models import db, Landlord, Property
from app import app
import time


def geocode():
	with app.app_context():
		properties = Property.query.filter(Property.latitude.is_(None)).order_by(Property.id.desc())

		for property in properties:
			url = 'https://nominatim.openstreetmap.org/search/' + property.address +'?format=json'
			response = requests.get(url, verify=False).json()
			if not response:
				continue
			print('Latitude: '+response[0]['lat']+', Longitude: '+response[0]['lon'])
			property.latitude = response[0]['lat']
			property.longitude= response[0]['lon']
			db.session.commit()
			time.sleep(.5)


geocode()