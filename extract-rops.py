import requests
import json
import time
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from models import db, CodeCase
from app import app

REQUEST_BODY_FILE = './rop-request-formatted.json'
CODE_SEARCH_URL = 'https://albanyny-energovpub.tylerhost.net/apps/selfservice/api/energov/search/search'
CUSTOM_FIELDS_URL = 'https://albanyny-energovpub.tylerhost.net/apps/selfservice/api/energov/customfields/data/'
HISTORICAL_START_YEAR = 1900
HISTORICAL_END_YEAR = 2014

CUSTOM_FIELDS_REQUEST_TEMPLATE = {"EntityId":"","ModuleId":3,"LayoutId":"13521345-000d-47f0-9a55-83489ead05d7","OnlineLayoutId":"cb89531e-b1fc-d4ca-c403-4b673d90ac57"}

HEADERS = {
	"tenantId": "1",
	"tenantName": "AlbanyNY",
}

def get_custom_fields(rop_entity_id):
	request_body = CUSTOM_FIELDS_REQUEST_TEMPLATE
	request_body["EntityId"] = rop_entity_id
	r = requests.post(CUSTOM_FIELDS_URL, json=request_body, headers=HEADERS)
	if "Success" not in r.json():
		logging.error(r.json())
		logging.error(rop_entity_id)
		exit(0)

	results = r.json()
	time.sleep(2)
	return results["Result"]["CustomGroups"][0]["CustomFields"]

def get_results_one_year(year):
	return get_results_year_range(year, year)

# CAUTION: If we have too many results here, the API will fail. We can handle pulling up until 2014.
def get_results_year_range(from_year, to_year):
	return get_code_case_results("{from_year}-01-01T05:00:00.000Z", "{to_year}-12-31T05:00:00.000Z")

def get_code_case_results(from_datetime, to_datetime):
	with open(REQUEST_BODY_FILE) as f:
		request_body = json.load(f) 
		request_body["CodeCaseCriteria"]["OpenedDateFrom"] = from_datetime
		request_body["CodeCaseCriteria"]["OpenedDateTo"] = to_datetime

		r = requests.post(CODE_SEARCH_URL, json=request_body, headers=HEADERS)
		if not r.json()["Success"]:
			logging.error(r.json())
			exit(0)

		codeCaseResults = r.json()["Result"]["EntityResults"]
		return codeCaseResults

def build_full_code_case_results():
	cumulativeResults = get_results_year_range(HISTORICAL_START_YEAR, HISTORICAL_END_YEAR)

	for year in range(HISTORICAL_END_YEAR + 1, datetime.now().year + 1):
		annualResults = get_results_one_year(year)
		cumulativeResults = cumulativeResults + annualResults
		time.sleep(2)

	return cumulativeResults


def handle_custom_fields(code_case):
	custom_fields_to_return = {
		"number_of_residential_units_in_building": None,
		"number_of_units_to_receive_rops": None,
		"units_to_receive_an_rop": None,
		"issue_rops": None
	}

	if code_case["FinalDate"] is None or code_case["CaseType"] != "ROP":
		return custom_fields_to_return

	final_datetime = datetime.strptime(code_case["FinalDate"][:19], '%Y-%m-%dT%H:%M:%S')
	rop_validity = datetime.now() - relativedelta(years=2)

	if final_datetime > rop_validity:
		custom_fields_for_case = get_custom_fields(code_case["CaseId"])

		for field in custom_fields_for_case:
			if field["FieldName"] == "NumberofResidentialUnitsinbuilding":
				custom_fields_to_return["number_of_residential_units_in_building"] = field["Value"]
			elif field["FieldName"] == "NumberofUnitstoReceiveROPs":
				custom_fields_to_return["number_of_units_to_receive_rops"] = field["Value"]
			elif field["FieldName"] == "UnitstoReceiveanROP":
				custom_fields_to_return["units_to_receive_an_rop"] = field["Value"]
			elif field["FieldName"] == "ISSUEROPS":
				custom_fields_to_return["issue_rops"] = field["Value"]
	   
	return custom_fields_to_return


def create_code_violations_table():
	json_results = build_full_code_case_results()
	code_case_objects = []
	for code_case in json_results:

		custom_fields = handle_custom_fields(code_case)
		
		address1 = "" if code_case["Address"] is None else code_case["Address"]["AddressLine1"]
		address2 = "" if code_case["Address"] is None else code_case["Address"]["AddressLine2"]
		postal_code = "" if code_case["Address"] is None else code_case["Address"]["PostalCode"]
		code_case_json = {
			"case_id": code_case["CaseId"],
			"case_number": code_case["CaseNumber"],
			"case_type": code_case["CaseType"],
			"case_status": code_case["CaseStatus"],
			"apply_date": code_case["ApplyDate"],
			"final_date": code_case["FinalDate"],
			"address_line_1": address1,
			"address_line_2": address2,
			"postal_code": postal_code,
			"parcel_id": code_case["MainParcel"],
			"number_of_residential_units_in_building": custom_fields["number_of_residential_units_in_building"],
			"number_of_units_to_receive_rops": custom_fields["number_of_units_to_receive_rops"],
			"units_to_receive_an_rop": custom_fields["units_to_receive_an_rop"],
			"issue_rops": custom_fields["issue_rops"]
		}

		code_case_objects.append(CodeCase(**code_case_json))

	with app.app_context():
		# First, delete existing Code Cases, then create, then commit
		db.session.query(CodeCase).delete()
		db.session.bulk_save_objects(code_case_objects)
		db.session.commit()

def main():
	create_code_violations_table()

if __name__ == "__main__":
	main()

