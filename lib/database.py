import os
import sys
import weaviate
import random
import string

import requests
from string import Template

import config

# parse helper
def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""


# random strings
def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


###############
# FeatureBase #
###############
def apply_schema(list_of_lists, schema):
	result = []
	for row in list_of_lists:
		dict_row = {}
		for i, val in enumerate(row):
			dict_row[schema[i]] = val
		result.append(dict_row)
	return result

# "sql" key in document should have a valid query
def featurebase_query(document):
	# try to run the query
	try:
		sql = document.get("sql")
		# print(sql)

		result = requests.post(
			config.featurebase_endpoint+"/query/sql",
			data=sql.encode('utf-8'),
			headers={
				'Content-Type': 'text/plain',
				'X-API-Key': '%s' % config.featurebase_token,
			}
		).json()

	except Exception as ex:
		# bad query?
		exc_type, exc_obj, exc_tb = sys.exc_info()
		document['error'] = "%s: %s" % (exc_tb.tb_lineno, ex)
		return document

	if result.get('error', ""):
		# featurebase reports and error
		document['explain'] = "Error returned by FeatureBase: %s" % result.get('error')
		document['error'] = result.get('error')
		document['data'] = result.get('data')

	elif result.get('data', []):
		# got some data back from featurebase
		document['data'] = result.get('data')
		document['schema'] = result.get('schema')

		field_names = []

		for field in result.get('schema').get('fields'):
			field_names.append(field.get('name'))

		document['results'] = apply_schema(result.get('data'), field_names)
	
	else:
		document['explain'] = "Query was successful, but returned no data."

	return document


############
# Weaviate #
############

def weaviate_schema(schema="none"):
	# connect to weaviate
	weaviate_client = weaviate.Client(
		url = config.weaviate_endpoint,
		additional_headers = {
			"X-OpenAI-Api-Key": config.openai_token,
			"Authorization": "Bearer %s" % config.weaviate_token 
		}
	)

	# connect to weaviate and ensure schema exists
	try:
		schema = weaviate_client.schema.get(schema)
	
	except Exception as ex:
		print("Trying to create schema: %s" % schema)
		try:
			# show vector database connection error
			dir_path = os.path.dirname(os.path.realpath(__file__))
			schema_file = os.path.join(dir_path, "schema/%s.json" % schema)
			weaviate_client.schema.create(schema_file)
			schema = weaviate_client.schema.get(schema)
		except Exception as ex:
			print(ex)
			schema = {"error": "no schema"}

	return schema

# send a document to a class/collection
def weaviate_update(document, collection):
	# connect to weaviate
	weaviate_client = weaviate.Client(
		url = config.weaviate_endpoint,
		additional_headers = {
			"X-OpenAI-Api-Key": config.openai_token,
			"Authorization": "Bearer %s" % config.weaviate_token 
		}
	)

	data_uuid = weaviate_client.data_object.create(document, collection)

	return data_uuid


def weaviate_object(uuid, collection):
	# connect to weaviate
	weaviate_client = weaviate.Client(
		url = config.weaviate_endpoint,
		additional_headers = {
			"X-OpenAI-Api-Key": config.openai_token,
			"Authorization": "Bearer %s" % config.weaviate_token 
		}
	)
	document = weaviate_client.data_object.get_by_id(
	  uuid,
	  class_name=collection,
	  consistency_level=weaviate.data.replication.ConsistencyLevel.ONE
	)

	return(document)

# query weaviate for matches
def weaviate_query(concepts, collection, fields, move_tos=[], filename=""):
	# connect to weaviate
	weaviate_client = weaviate.Client(
		url = config.weaviate_endpoint,
		additional_headers = {
			"X-OpenAI-Api-Key": config.openai_token,
			"Authorization": "Bearer %s" % config.weaviate_token 
		}
	)

	where_filter = {
		"path": ["filename"],
		"operator": "Equal",
		"valueString": filename,
	}

	nearText = {
	  "concepts": concepts,
	  "moveTo": {
	  	"concepts": move_tos,
	  	"force": 0.5
	  }
	}

	if filename == "":
		# fetch result and fields
		result = (
			weaviate_client.query
			.get(collection, fields)
			.with_near_text(nearText)
			.with_additional(["certainty", "distance", "id"])
			.with_limit(2000)
			.do()
		)
	else:
		# fetch result and fields
		result = (
			weaviate_client.query
			.get(collection, fields)
			.with_near_text(nearText)
			.with_additional(["certainty", "distance", "id"])
			.with_limit(20)
			.with_where(where_filter)
			.do()
		)

	_records = []

	try:
		results = result.get('data').get('Get').get(collection)
		for record in results:
			_records.append(record)

	except Exception as ex:
		print("likely no records for %s" % collection)
		print("================")
		print(ex)
		print("================")

	# print(_records)
	return _records


def weaviate_delete_schema(collection):
	# connect to weaviate
	weaviate_client = weaviate.Client(
		url = config.weaviate_endpoint,
		additional_headers = {
			"X-OpenAI-Api-Key": config.openai_token,
			"Authorization": "Bearer %s" % config.weaviate_token
		}
	)

	if collection == "force_all":
		weaviate_client.schema.delete_all()
	else:
		try:
			weaviate_client.schema.delete_class(collection)
		except Exception as ex:
			print(ex)

	return


# delete a document from weaviate
def weaviate_delete_document(uuid, collection):
	# connect to weaviate
	weaviate_client = weaviate.Client(
		url = config.weaviate_endpoint,
		additional_headers = {
			"X-OpenAI-Api-Key": config.openai_token,
			"Authorization": "Bearer %s" % config.weaviate_token
		}
	)

	try:
		weaviate_client.data_object.delete(uuid, collection)
	except Exception as ex:
		print(ex)

	return

