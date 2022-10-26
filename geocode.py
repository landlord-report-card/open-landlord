import requests
from models import db, Landlord, Property
from app import app
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


REPLACEMENTS = [
	("FIRST", "1st"),
	("SECOND", "2nd"),
	("THIRD", "3rd"),
	("FOURTH", "4th"),
]

def geocode():
	with app.app_context():
		properties = Property.query.filter(Property.latitude.is_(None)).order_by(Property.id.desc())

		for property in properties:
			address = property.address

			# Mapbox struggles with Fourth vs. 4th, etc.
			for replacement in REPLACEMENTS:
				address = address.replace(replacement[0], replacement[1])

			url = 'https://nominatim.openstreetmap.org/search/' + address +'?format=json'
			response = requests.get(url, verify=False).json()
			if not response:
				continue
			print('Latitude: '+response[0]['lat']+', Longitude: '+response[0]['lon'] +', Address: '+response[0]['display_name'])
			property.latitude = response[0]['lat']
			property.longitude= response[0]['lon']
			db.session.commit()
			time.sleep(.5)


geocode()