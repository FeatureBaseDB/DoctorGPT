import weaviate
import config
import pprint
import sys
import json
import os

from lib.util import random_string

from lib.database import weaviate_schema, weaviate_query, weaviate_object, featurebase_query
from lib.ai import ai

# create Weaviate schema
weaviate_schema = weaviate_schema("QandAs")

# get files to index
dir_path = "./documents/"
files = os.listdir(dir_path)
print("\nDocuments Directory\n===================")
for i, file in enumerate(files):
    print("%s." % i, file)

# prompt for file entry
file_number = input("Enter the number of the file to chat with: ")
filename = files[int(file_number)]

print("Entering conversation with %s. Use ctrl-C to end interaction." % filename)
while True:
	# get a question from the user

	try:
		query = input("user-%s[%s]> " % (random_string(4), filename))
	except KeyboardInterrupt:
		print()
		print("bot>", "Bye!")
		sys.exit()

	# lookup matches from weaviate's QandAs
	weaviate_results = weaviate_query([query], "QandAs", ["query", "answer", "origin_id", "filename"])

	qanda_results = []
	fragment_uuids = []

	# filter results by filename
	# TODO figure out issue with Weaviate not filtering
	for _result in weaviate_results:
		if _result.get('filename') == filename:
			qanda_results.append({"query": _result.get('query'), "answer": _result.get('answer'), "origin_id": _result.get('origin_id'), "distance": _result.get('_additional').get("distance")})
			if _result.get('origin_id') not in fragment_uuids:
				fragment_uuids.append(_result.get('origin_id'))

	if len(fragment_uuids) == 0:
		print("bot> You need to index this document before we discuss it.")
		sys.exit()

	# grab the document fragments from FeatureBase
	fragments = ""
	keyterms = []
	title = ""
	for uuid in fragment_uuids:
		sql = "SELECT * FROM doc_keyterms WHERE SETCONTAINS(uuids, '%s')" % uuid
		keyterm_results = featurebase_query({"sql": sql}).get('results')

		for keyterm in keyterm_results:
			if keyterm.get('_id') not in keyterms:
				keyterms.append(keyterm.get('_id'))
			title = keyterm.get('title')

		sql = "SELECT fragment FROM doc_fragments WHERE _id = '%s'" % uuid
		fragment_results = featurebase_query({"sql": sql}).get('results')
		for fragment in fragment_results:
			if len(fragments) < 1500:
				fragments = fragments + fragment.get('fragment') + " "


	print("bot> Querying GPT...")

	document = {"query": query, "text": fragments, "keyterms": keyterms[10:], "title": title}
	document = ai("ask_gpt", document)
	print("bot>", document.get('answer').strip())
	print("bot>", document.get('probability'), document.get('dimensionality'))
	print("bot>")
"""

	keyterms = []
	for _id in vector_uuids:
		sql = "SELECT * FROM doc_keyterms WHERE SETCONTAINS(uuids, '%s')" % _id
		keyterm_results = featurebase_query({"sql": sql}).get('results')

		for keyterm in keyterm_results:
			keyterms.append(keyterm.get('_id'))

	from collections import Counter
	counts = Counter(keyterms)

	max_occurance = 0
	for k,v in counts.items():
		if v > max_occurance:
			max_occurance = v

	top_keyterms = []
	for k,v in counts.items():
		if v == max_occurance:
			if k not in top_keyterms:
				top_keyterms.append(k)

	# grab fragments from a weaviate vector search (applying keyterms to affect move tos)
	weaviate_results = weaviate_query([query], "PDFs", ["fragment", "filename", "page_number"], top_keyterms)
	
	vector_fragments = []
	# filter results by filename
	# TODO figure out issue with Weaviate not filtering
	for _result in weaviate_results:
		if _result.get('filename') == filename:
			if _result.get('_additional').get('id') not in vector_uuids:
				vector_fragments.append(_result.get('fragment'))

		if len(vector_fragments) > 4:
			break


	print(vector_fragments)

	title = item[2]
	query = item[3]
	keyterms = item[4]
	print(query)
	# create a result set
	vector_uuids = []

	# select the ids from featurebase
	for keyterm in keyterms:
		sql = "SELECT * FROM doc_keyterms WHERE _id = '%s';" % keyterm.lower()
		fb_result_keyterms = featurebase_query({"sql": sql}).get('data')
		for _uuid in fb_result_keyterms[0][3]:
			if _uuid not in vector_uuids:
				vector_uuids.append(_uuid)

	# append the vectors from weaviate to the array
	vector_results = []
	for uuid in vector_uuids:
		vector_results.append(weaviate_object(uuid, "PDFs").get('properties').get('fragment'))

	# grab fragments from weaviate
	weaviate_results = weaviate_query([query], "PDFs", ["fragment", "filename", "page_number"], keyterms)
	
	# filter results by filename
	# TODO figure out issue with Weaviate not filtering
	for _result in weaviate_results:
		if _result.get('filename') == filename:
			if _result.get('_additional').get('id') not in vector_uuids:
				vector_results.append(_result.get('fragment'))

		if len(vector_results) > 4:
			break

	_text = ""
	for result in vector_results:
		_text = _text + " " + result

	document = {"query": query, "text": _text.strip(), "title": title}
	print(ai("answer_question", document))
"""