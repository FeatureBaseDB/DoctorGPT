import weaviate
import config
import pprint
import sys
import json
import os
import time

from lib.util import random_string

from lib.database import weaviate_schema, weaviate_query, weaviate_update, weaviate_object, featurebase_query
from lib.ai import ai

# create Weaviate schema
weaviate_schema = weaviate_schema("QandAs")

# user
username = random_string(4)

def output_fragments(object, str):
	for item in object:
		print(str, "===============================================================================")
		print(item.get('_additional').get("distance"))
		print(str, "===============================================================================")
		print(item.get('fragment'))
		print(str, "===============================================================================")

from collections import defaultdict

def extract_keyterms(data):
	# Create a dictionary to store keyterms and their relevance count
	relevance_count = defaultdict(int)
	uuids_dict = defaultdict(set)

	# Iterate over the data
	for item in data:
		uuids = item['uuids']
		page_ids = item['page_ids']
		keyterm = item['_id']

		# Increment relevance count for each keyterm based on UUIDs and page IDs
		for other_item in data:
			if other_item is not item:
				other_uuids = other_item['uuids']
				other_page_ids = other_item['page_ids']

				# Check if there are similar UUIDs or page IDs
				if set(uuids) & set(other_uuids) or set(page_ids) & set(other_page_ids):
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

from sklearn.cluster import KMeans
import numpy as np

def cluster_questions(qanda_results, num_clusters):
	# Extract the distances from qanda_results
	distances = [result['distance'] for result in qanda_results]

	# Convert distances to a numpy array
	distances_array = np.array(distances).reshape(-1, 1)

	# Perform K-means clustering
	kmeans = KMeans(n_clusters=num_clusters)
	kmeans.fit(distances_array)

	# Assign cluster labels to each question
	for i, result in enumerate(qanda_results):
		result['cluster_label'] = kmeans.labels_[i]

	# Sort the qanda_results by cluster label
	qanda_results.sort(key=lambda x: x['distance'])

	return qanda_results

import random

def select_two_random_entries(my_list):
	if len(my_list) < 2:
		raise ValueError("The list must contain at least two elements.")

	first_entry = random.choice(my_list)
	second_entry = random.choice([entry for entry in my_list if entry != first_entry])

	return first_entry, second_entry


print("Entering broad conversation with all indexed documents. Use ctrl-C to end interaction.")
while True:
	# get a question from the user

	try:
		question = input("user-%s[%s]> " % (username, "broad"))
	except KeyboardInterrupt:
		print()
		print("bot>", "Bye!")
		sys.exit()

	start_time = time.time()
	# lookup matches from weaviate's QandAs
	weaviate_results = weaviate_query([question], "QandAs", ["question", "answer", "origin_id", "filename"])

	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried Weaviate for questions in:", elapsed_time, "seconds")

	# results arrays
	qanda_results = []
	fragment_uuids = []

	# get questions from weaviate and the fragment UUIDs that go with them
	for _result in weaviate_results:
		qanda_results.append({"question": _result.get('question'), "answer": _result.get('answer'), "origin_id": _result.get('origin_id'), "distance": _result.get('_additional').get("distance"), "filename": _result.get('filename'), "vector": _result.get('_additional').get('featureProjection').get('vector')})

		if _result.get('origin_id') not in fragment_uuids:
			fragment_uuids.append(_result.get('origin_id'))

	# cluster the questions by distance
	results = cluster_questions(qanda_results, 7)

	for item in results:
		print(item.get('cluster_label'), item.get('filename'), item.get('distance'), item.get('question'))
	sys.exit()

	"""
	old_label = ""
	for result in results:
		if result.get('cluster_label') != old_label:
			print(result.get('cluster_label'), result.get('question'), result.get('filename'))
			old_label = result.get('cluster_label')
	"""

	# no docs
	if len(fragment_uuids) == 0:
		print("bot> You need to index this document before we discuss it.")
		sys.exit()

	# grab the document fragments from FeatureBase
	fragments = ""
	keyterms = []
	title = ""

	start_time = time.time()
	# select all the keyterms that match the UUIDs we got from the questions vector store
	sql = "SELECT * FROM doc_keyterms WHERE "
	for i, uuid in enumerate(fragment_uuids):
		sql = sql + "SETCONTAINS (uuids, '%s')" % uuid
		if i < len(fragment_uuids) - 1:
			sql = sql + " OR "

	keyterm_results = featurebase_query({"sql": sql}).get('results')
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried FeatureBase for keyterms in:", elapsed_time, "seconds")

	# extract the relevant ones
	relevant_keyterms = extract_keyterms(keyterm_results)

	# build the list of keyterms to move toward in weaviate (and used later in the prompt)
	for keyterm in relevant_keyterms[:40]:
		print(keyterm[0])
		keyterms.append(keyterm[0])


	min_distance = 2
	max_distance = 0
	min_average_distance = 1

	for i in range(40):
		entries = select_two_random_entries(keyterms)
		print("=====================")
		print(question)
		print([entries[0], entries[1]])

		weaviate_results = weaviate_query([question], "QandAs", ["question", "answer", "origin_id", "filename"], [entries[0], entries[1]])

		_total_distance = 0
		loops = 10
		for j, _results in enumerate(weaviate_results):
			if j > loops:
				break
			sql = "SELECT * FROM doc_fragments WHERE _id = '%s'" % _results.get('origin_id')
			fragment_results = featurebase_query({"sql": sql}).get('results')
			if min_distance > _results.get('_additional').get('distance'):
				print("setting min_distance")
				min_distance = _results.get('_additional').get('distance')
			if max_distance < _results.get('_additional').get('distance'):
				print("setting max_distance")
				max_distance = _results.get('_additional').get('distance')
			_total_distance = _total_distance + _results.get('_additional').get('distance')
			# print(_results.get('_additional').get('distance'), _results.get('filename'))

		average_distance = _total_distance/loops
		print("avg_distance:", average_distance)
		if min_average_distance > average_distance:
			min_average_distance = average_distance

		print("min_distance:", min_distance)
		print("max_distance:", max_distance)
