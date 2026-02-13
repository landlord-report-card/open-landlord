import requests
import json
import time
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from models import db, CodeCase, CodeViolation
from app import app

REQUEST_BODY_FILE = './rop-request-formatted.json'
CODE_SEARCH_URL = 'https://albanyny-energovpub.tylerhost.net/apps/selfservice/api/energov/search/search'
CUSTOM_FIELDS_URL = 'https://albanyny-energovpub.tylerhost.net/apps/selfservice/api/energov/customfields/data/'
VIOLATIONS_URL = 'https://albanyny-energovpub.tylerhost.net/apps/selfservice/api/energov/entity/violations/search'
HISTORICAL_START_YEAR = 1900
HISTORICAL_END_YEAR = 2014

CODE_ENFORCEMENT_CODE_CASE_TYPE_ID = '48e1603a-4b28-40be-89bc-61793ed7241b'

CUSTOM_FIELDS_REQUEST_TEMPLATE = {"EntityId":"","ModuleId":3,"LayoutId":"13521345-000d-47f0-9a55-83489ead05d7","OnlineLayoutId":"cb89531e-b1fc-d4ca-c403-4b673d90ac57"}

VIOLATIONS_REQUEST_TEMPLATE = {"PageNumber":1,"PageSize":10000,"SortField":"","IsSortedInAscendingOrder":True,"ModuleId":3,"EntityId":""}

HEADERS = {
	"tenantId": "1",
	"tenantName": "AlbanyNY",
}

def get_custom_fields(rop_entity_id):
	request_body = CUSTOM_FIELDS_REQUEST_TEMPLATE
	request_body["EntityId"] = rop_entity_id
	r = requests.post(CUSTOM_FIELDS_URL, json=request_body, headers=HEADERS)
	
	while "Success" not in r.json():
		logging.error(r.json())
		logging.error(rop_entity_id)
		logging.error("Request failed. Waiting and trying again.")
		time.sleep(30)
		r = requests.post(CUSTOM_FIELDS_URL, json=request_body, headers=HEADERS)

	results = r.json()
	time.sleep(2)
	return results["Result"]["CustomGroups"][0]["CustomFields"]

def get_results_one_year(year):
	return get_results_year_range(year, year)

# CAUTION: If we have too many results here, the API will fail. We can handle pulling up until 2014.
def get_results_year_range(from_year, to_year):
	return get_code_case_results(f"{from_year}-01-01T05:00:00.000Z", f"{to_year}-12-31T05:00:00.000Z")

def get_code_case_results(from_datetime, to_datetime):
	with open(REQUEST_BODY_FILE) as f:
		request_body = json.load(f) 
		request_body["CodeCaseCriteria"]["OpenedDateFrom"] = from_datetime
		request_body["CodeCaseCriteria"]["OpenedDateTo"] = to_datetime
		# print(request_body)

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
		logging.error(f"Fetching year {year}. This year size is {len(annualResults)}, cumulative is {len(cumulativeResults)}")
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


def populate_violations():
	with app.app_context():
		# Get all code cases of type code enforcement
		code_enforcement_cases = CodeCase.query.filter(CodeCase.case_type == 'CODE ENFORCEMENT')
		code_violations = []

		total = code_enforcement_cases.count()
		count = 0

		# for each, do a request and add an entry to code violations table
		for code_case in code_enforcement_cases:
			if count % 500 == 0:
				logging.error(f"Processing code case {count} of {total}...")
			count = count + 1
			request_body = VIOLATIONS_REQUEST_TEMPLATE
			request_body["EntityId"] = code_case.case_id
			r = requests.post(VIOLATIONS_URL, json=request_body, headers=HEADERS)
			results = r.json()
			if "Result" not in results:
				logging.error(f"No results found for {results}")
				continue

			if not results["Result"]:
				continue

			for violation in results["Result"]:
				violations_json = {
				    "code_violation_id": violation["EntityViolationId"],
				    "code_case_id": violation["EntityId"],
				    "code_number": violation["CodeNumber"],
				    "code_description": violation["CodeDescription"],
				    "code_text": violation["RevisionCodeText"],
				    "corrective_action": violation["CorrectiveAction"],
				    "category_name": violation["CategoryName"],
				    "status": violation["CodeStatus"],
				    "priority": violation["ViolationPriority"],
				    "issue_date": violation["CitationIssueDate"],
				    "compliance_date": violation["ComplianceDate"],
				    "resolve_date": violation["ResolveDate"],
				}
				code_violations.append(CodeViolation(**violations_json))

		# First, delete existing Code Cases, then create, then commit
		logging.error("Writing out code violations...")
		db.session.query(CodeViolation).delete()
		db.session.bulk_save_objects(code_violations)
		try:
			db.session.commit()
		except SQLAlchemyError as e:
		    logging.error(f"Error: {e}")
		    db.session.rollback() # Rollback the failed transaction
		finally:
		    db.session.close()



def populate_code_cases():
	json_results = build_full_code_case_results()
	code_case_objects = []
	total = len(json_results)
	count = 0
	for code_case in json_results:
		if count % 500 == 0:
			logging.error(f"Processing code case {count} of {total}...")
		count = count + 1

		custom_fields = handle_custom_fields(code_case)
		
		address1 = "" if code_case["Address"] is None else code_case["Address"]["AddressLine1"]
		address2 = "" if code_case["Address"] is None else code_case["Address"]["AddressLine2"]
		postal_code = "" if code_case["Address"] is None else code_case["Address"]["PostalCode"]
		code_case_json = {
			"case_id": code_case["CaseId"],
			"case_number": code_case["CaseNumber"],
			"case_type": code_case["CaseType"],
			"case_status": code_case["CaseStatus"],
			"description": code_case["Description"],
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
		try:
			db.session.commit()
		except SQLAlchemyError as e:
		    logging.error(f"Error: {e}")
		    db.session.rollback() # Rollback the failed transaction
		finally:
		    db.session.close()

def main():
	populate_code_cases()
	populate_violations()

if __name__ == "__main__":
	main()

