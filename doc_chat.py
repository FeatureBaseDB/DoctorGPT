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

# user
username = random_string(4)

from collections import defaultdict

def extract_keyterms(data):
	# Create a dictionary to store keyterms and their relevance count
	relevance_count = defaultdict(int)
	uuids_dict = defaultdict(set)

	# Iterate over the data
	for item in data:
		uuids = item['uuids']
		page_nums = item['page_num']
		keyterm = item['_id']

		# Increment relevance count for each keyterm based on UUIDs and page numbers
		for other_item in data:
			if other_item is not item:
				other_uuids = other_item['uuids']
				other_page_nums = other_item['page_num']

				# Check if there are similar UUIDs or page numbers
				if set(uuids) & set(other_uuids) or set(page_nums) & set(other_page_nums):
					relevance_count[keyterm] += 1
					uuids_dict[keyterm].update(uuids)

	# Sort keyterms based on relevance count in descending order
	sorted_keyterms = sorted(relevance_count.items(), key=lambda x: x[1], reverse=True)

	# Sort UUIDs for each keyterm based on reference count
	sorted_uuids_dict = {keyterm: sorted(list(uuids), key=lambda x: len(uuids_dict[keyterm]), reverse=True) for keyterm, uuids in uuids_dict.items()}

	# Return relevant keyterms and sorted UUIDs
	return [(keyterm, sorted_uuids_dict[keyterm]) for keyterm, _ in sorted_keyterms]

def extract_most_referenced_uuids(relevant_keyterms, num_uuids=10):
	# Create a dictionary to store the reference count for each UUID
	uuid_count = defaultdict(int)

	# Iterate over the relevant keyterms
	for _, uuids in relevant_keyterms:
		for uuid in uuids:
			uuid_count[uuid] += 1

	# Sort UUIDs based on their reference count in descending order
	sorted_uuids = sorted(uuid_count.items(), key=lambda x: x[1], reverse=True)

	# Retrieve the top N most referenced UUIDs
	top_uuids = [uuid for uuid, _ in sorted_uuids[:num_uuids]]
	return top_uuids

print("Entering conversation with %s. Use ctrl-C to end interaction." % filename)
while True:
	# get a question from the user

	try:
		question = input("user-%s[%s]> " % (username, filename))
	except KeyboardInterrupt:
		print()
		print("bot>", "Bye!")
		sys.exit()

	# lookup matches from weaviate's QandAs
	weaviate_results = weaviate_query([question], "QandAs", ["question", "answer", "origin_id", "filename"], filename=filename)

	qanda_results = []
	fragment_uuids = []

	# filter results by filename
	# TODO figure out issue with Weaviate not filtering
	for _result in weaviate_results:
		qanda_results.append({"question": _result.get('question'), "answer": _result.get('answer'), "origin_id": _result.get('origin_id'), "distance": _result.get('_additional').get("distance")})
		if _result.get('origin_id') not in fragment_uuids:
			fragment_uuids.append(_result.get('origin_id'))

	if len(fragment_uuids) == 0:
		print("bot> You need to index this document before we discuss it.")
		sys.exit()

	# grab the document fragments from FeatureBase
	fragments = ""
	keyterms = []
	title = ""

	sql = "SELECT * FROM doc_keyterms WHERE "
	for i, uuid in enumerate(fragment_uuids):
		sql = sql + "SETCONTAINS (uuids, '%s')" % uuid
		if i < len(fragment_uuids) - 1:
			sql = sql + " OR "
	keyterm_results = featurebase_query({"sql": sql}).get('results')

	relevant_keyterms = extract_keyterms(keyterm_results)

	for keyterm in relevant_keyterms:
		keyterms.append(keyterm[0])

	top_referenced_uuids = extract_most_referenced_uuids(relevant_keyterms, num_uuids=10)

	sql = "SELECT * FROM doc_fragments WHERE "
	for i, uuid in enumerate(top_referenced_uuids):
		sql = sql + "_id = '%s'" % uuid
		if i < len(top_referenced_uuids) - 1:
			sql = sql + " OR "

	fragment_results = featurebase_query({"sql": sql}).get('results')
	fragments = ""
	for result in fragment_results:
		title = result.get('title')
		fragments = fragments + " " + result.get('fragment')

	print("bot> Querying GPT...")

	document = {"question": question, "text": fragments, "keyterms": keyterms, "title": title}

	document = ai("ask_gptchat", document)
	
	print("bot> " + document.get('answer'))
