import weaviate
import config
import pprint
import sys

from lib.database import weaviate_query, featurebase_query
from lib.ai import ai

client = weaviate.Client(
    url=config.weaviate_endpoint,
    additional_headers={
        "X-OpenAI-Api-Key": config.openai_token,
        "Authorization": "Bearer %s" % config.weaviate_token 
    }
)

"""
x = 0
while True:
	all_objects = client.data_object.get(class_name="PDFs", offset=x)
	x = x + 25
	print(len(all_objects.get('objects')))
	print(x)
sys.exit()
"""
query = input("enter query: ")


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
  .get("PDFs", ["fragment", "filename"])
  .with_near_text(near_text_filter)
  .with_additional(
    (additional_clause, additional_setting)
  )
  .with_additional(["id", "distance"])
  .do()
)
print(query_result)
datas = query_result.get('data').get('Get').get('PDFs')
# print(datas)
content = ""
print("====================================")
burps = []
for i, data in enumerate(datas):
	content = content + " " + data.get('fragment')
	burps.append((data.get('_additional').get('distance'), data.get('_additional').get('id'), data.get('_additional').get('featureProjection').get('vector')[0], data.get('fragment')[:1000]))
	#print("======================================")
	# print(data.get('fragment'), data.get('gpt_fragment'))
	if False:
		document = {"plain": query, "content": content}
		#print(ai("quantum", document).get('answer', "None"))
		break


foo = sorted(burps)
for fo in foo:
	if fo[0] < 0.30:
		print(fo)

print("ending interaction")
sys.exit()

xs = []
ys = []
texts = []

for data in datas:
	print(data.get('sentence')[:100], data.get("_additional").get('featureProjection').get('vector'))
	# xs.append(data.get("_additional").get('featureProjection').get('vector')[0])
	# ys.append(data.get("_additional").get('featureProjection').get('vector')[1])
	# texts.append(data.get('title')[:20])

sys.exit()

import plotly.express as px
fig = px.scatter(x=xs, y=ys, text=texts)

fig.show()

"""
all_objects = client.data_object.get(class_name="Support")
print(all_objects)

import sys
sys.exit()

schema = client.schema.get()
for classe in schema.get('classes'):
	print(classe.get('class'))
"""

document = {"plain": query}
collection = "Docs"
fields = ["url", "title", "sentence"]
records = weaviate_query([query], collection, fields)

for i, record in enumerate(records):
	if i > 2:
		break
	print(record)

"""
for doc in documents:
	nearText = {
	  "concepts": [doc.get('plain')],
	  "distance": 0.7,
	}
	print("=========================================")
	print("========", doc.get('plain'))
	result = (
	  client.query
	  .get("Slothbot", ["table","plain","sql"])
	  .with_additional(["certainty", "distance"])
	  .with_near_text(nearText)
	  .do()
	)

	for record in result.get('data').get('Get').get('Slothbot'):
		print(record.get('_additional').get('certainty'), "|", record.get('_additional').get('distance'), "|", record.get('table'), "|", record.get('sql'))

documents = [
	{"plain": "select from planets"}
]
for doc in documents:
	nearText = {
	  "concepts": [doc.get('plain')],
	  "distance": 0.2,
	}
	print("=========================================")
	print("========", doc.get('plain'))
	result = (
	  client.query
	  .get("Slothbot", ["plain"])
	  .with_additional(["certainty", "distance", "id"])
	  .with_near_text(nearText)
	  .do()
	)

	for record in result.get('data').get('Get').get('Slothbot'):
		print(record.get('_additional').get('certainty'), "|", record.get('_additional').get('distance'), "|", record.get('table'), "|", record.get('sql'))


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
"""
