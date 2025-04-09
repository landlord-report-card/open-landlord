import csv
from models import db, Eviction
from app import app


def create_evictions_table(filename):
	eviction_objects = []
	seen_cases = set()
	with open(filename, 'r') as file:
		csv_reader = csv.DictReader(file)

		for eviction in csv_reader:
			if eviction["Caseid"] in seen_cases:
				continue

			seen_cases.add(eviction["Caseid"])

			eviction_date = None
			if eviction["Date"] != "#N/A":
				eviction_date = eviction["Date"]

			eviction_json = {
				"caseid": eviction["Caseid"],
				"petitioner": eviction["Petitioner"],
				"case_date": eviction_date,
				"matched_name": eviction["MatchedName"],
			}

			
			eviction_objects.append(Eviction(**eviction_json))

	with app.app_context():
		db.session.query(Eviction).delete()
		db.session.bulk_save_objects(eviction_objects)
		db.session.commit()


def main():
	create_evictions_table("/Users/akaier/Downloads/Albany Evictions Logger - Export Log.csv")

if __name__ == "__main__":
	main()
