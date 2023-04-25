import weaviate
import config
import pprint
import sys
import json

from lib.database import weaviate_query, weaviate_object, featurebase_query
from lib.ai import ai

# query featurebase for popular keyterms
sql = "SELECT * FROM doc_keyterms"
fb_result = featurebase_query({"sql": sql}).get('data')

keyterms = []
for item in fb_result:
	keyterm = item[0]
	filename = item[1]
	uuids = item[2]
	page_nums = item[3]

	if len(page_nums) > 5:
		keyterms.append(keyterm)
		print(keyterm)
		print("===============================")
		for uuid in uuids:
			print(weaviate_object(uuid, "PDFs").get('properties').get('fragment'))

		"""
		if len(keyterms) > 5:
			print(keyterms)

			weave_text = ""
			for x in range(5):
				try:
					weave_result = weaviate_query(keyterms, "PDFs", ['fragment'])
					break
				except:
					continue

			for result in weave_result:
				if len(weave_text) < 1500:
					weave_text = weave_text + " " + result.get('fragment')
				else:
					break

			print(weave_text)

			keyterms = []
		"""