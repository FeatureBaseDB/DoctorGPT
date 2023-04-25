import weaviate
import config
import pprint
import sys
import json

from lib.database import weaviate_query, featurebase_query
from lib.ai import ai

client = weaviate.Client(
    url=config.weaviate_url,
    additional_headers={
        "X-OpenAI-Api-Key": config.openai_token
    }
)

query = input("enter query: ")

# try to query featurebase for it
# select uuids, count(*) from keyterm_uuid_set where _id in ('merkle tree', 'trust') group by uuids having count(*) > 0;
fb_query = "SELECT uuids, COUNT(*) FROM keyterm_uuid_set WHERE _id IN ('%s') group by uuids having count(*) > 0;" % query.lower()

fb_result = featurebase_query({"sql": fb_query}).get('data')

keyterms = []

# keyterm found directly
if fb_result and len(fb_result) > 0:
	keyterms.append(query)
	for item in fb_result:
		fb_query = "SELECT _id FROM keyterm_uuid_set WHERE SETCONTAINS(uuids, '%s')" % item[0]
		fb_terms = featurebase_query({"sql": fb_query}).get('data')
		for term in fb_terms:
			if term[0] not in keyterms:
				keyterms.append(term[0])
else:
	# ask weaviate for something
	near_text_filter = {
	  "concepts": [query]
	}
	additional_clause = {
	  "featureProjection": [
	    "vector"
	  ]
	}

	additional_setting = {
	  "dimensions": 1
	}

	query_result = (
	  client.query
	  .get("PDFs", ["fragment", "gpt_fragment"])
	  .with_near_text(near_text_filter)
	  .with_additional(
	    (additional_clause, additional_setting)
	  )
	  .with_additional(["id", "distance"])
	  .do()
	)

	datas = query_result.get('data').get('Get').get('PDFs')

	data = datas[0]

	fragment = data.get('fragment')

	ai_doc = ai("gpt_fragment", {"words": fragment})

	print("FeatureBase returned IDs:")

	for item in ai_doc:
		fb_query = "SELECT * FROM keyterm_uuid_set WHERE _id = '%s'" % item.lower()
		fb_uuids = featurebase_query({"sql": fb_query}).get('data')

		if fb_uuids:
			for uuid in fb_uuids[0][1]:
				fb_query_2 = "SELECT * FROM keyterm_uuid_set WHERE SETCONTAINS(uuids, '%s')" % uuid
				fb_uuid_result = featurebase_query({"sql": fb_query_2}).get('data')

				if fb_uuid_result:
					for uuid_2 in fb_uuid_result:
						if uuid_2[0] not in keyterms:
							keyterms.append(uuid_2[0])

query_string = ""

greatest_length = 0
_keyterms = []
for keyterm in keyterms:
	for keyterm2 in keyterms:
		fb_combined = "select uuids, count(*) from keyterm_uuid_set where _id in ('%s', '%s') group by uuids having count(*) > 1;" % (keyterm, keyterm2)
		fb_combined_result = featurebase_query({"sql": fb_combined}).get('data')
		try:
			if len(fb_combined_result) > greatest_length:
				greatest_length = len(fb_combined_result)
				print(fb_combined_result)
				print(keyterm, keyterm2)
		except:
			pass

greatest_length = 0
_keyterms = []
for keyterm in keyterms:
	for keyterm2 in keyterms:
		for keyterm3 in keyterms:
			fb_combined = "select uuids, count(*) from keyterm_uuid_set where _id in ('%s', '%s', '%s') group by uuids having count(*) > 2;" % (keyterm, keyterm2, keyterm3)
			fb_combined_result = featurebase_query({"sql": fb_combined}).get('data')
			try:
				if len(fb_combined_result) > greatest_length:
					greatest_length = len(fb_combined_result)
					print(fb_combined_result)
					print(keyterm, keyterm2, keyterm3)
			except:
				pass

	query_string = query_string + keyterm + " "
sys.exit()
query_string = query_string + " " + query

# ask weaviate for something
near_text_filter = {
  "concepts": [query_string]
}
additional_clause = {
  "featureProjection": [
    "vector"
  ]
}

additional_setting = {
  "dimensions": 1
}

query_result = (
  client.query
  .get("PDFs", ["fragment", "gpt_fragment"])
  .with_near_text(near_text_filter)
  .with_additional(
    (additional_clause, additional_setting)
  )
  .with_additional(["id", "distance"])
  .do()
)

datas = query_result.get('data').get('Get').get('PDFs')

prompt = ""
for data in datas:
	prompt = prompt + data.get('fragment') + " "
	if len(prompt) > 2000:
		break
print(prompt)
answer = ai("ask_gpt", {"plain": query, "prompt": prompt})
print(answer.get('plain'))
print(answer.get('answer'))