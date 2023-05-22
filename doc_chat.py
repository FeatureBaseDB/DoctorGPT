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

print("Entering conversation with %s. Use ctrl-C to end interaction." % filename)
while True:
	# get a question from the user

	try:
		question = input("user-%s[%s]> " % (username, filename))
	except KeyboardInterrupt:
		print()
		print("bot>", "Bye!")
		sys.exit()

	start_time = time.time()
	# lookup matches from weaviate's QandAs
	weaviate_results = weaviate_query([question], "QandAs", ["question", "answer", "origin_id", "filename"], filename=filename)

	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried Weaviate for questions in:", elapsed_time, "seconds")

	# results arrays
	qanda_results = []
	fragment_uuids = []

	# get questions from weaviate and the fragment UUIDs that go with them
	for _result in weaviate_results:
		qanda_results.append({"question": _result.get('question'), "answer": _result.get('answer'), "origin_id": _result.get('origin_id'), "distance": _result.get('_additional').get("distance")})
		if _result.get('origin_id') not in fragment_uuids:
			fragment_uuids.append(_result.get('origin_id'))

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
	for keyterm in relevant_keyterms:
		keyterms.append(keyterm[0])

	# get related fragments to the question concept while moving toward existing keyterms
	top_referenced_uuids = []
	start_time = time.time()
	weaviate_fragments = weaviate_query([question], "PDFs", ["fragment", "filename"], keyterms, filename)
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried Weaviate for fragments in:", elapsed_time, "seconds")

	for _fragment in weaviate_fragments:
		_uuid = _fragment.get('_additional').get('id')
		if _uuid not in top_referenced_uuids:
			top_referenced_uuids.append(_uuid)

	# get the top referenced UUIDs from keyterms in FeatureBase
	top_uuids = extract_most_referenced_uuids(relevant_keyterms, num_uuids=10)
	for _uuid in top_uuids:
		if _uuid not in top_referenced_uuids:
			top_referenced_uuids.append(_uuid)

	# get the fragments from FeatureBase for those UUIDs
	start_time = time.time()
	sql = "SELECT * FROM doc_fragments WHERE "
	for i, uuid in enumerate(top_referenced_uuids):
		sql = sql + "_id = '%s'" % uuid
		if i < len(top_referenced_uuids) - 1:
			sql = sql + " OR "

	fragment_results = featurebase_query({"sql": sql}).get('results')
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried FeatureBase for fragments in:", elapsed_time, "seconds")

	# build up a fragments string for sending to GPT
	fragments = ""

	for result in fragment_results:
		title = result.get('title')
		fragments = fragments + " " + result.get('fragment')

	# indicate we're calling the AI
	start_time = time.time()
	print("bot> Querying GPT...")

	# build the document for the AI calls
	document = {"question": question, "text": fragments, "keyterms": keyterms, "title": title}

	# call the AI
	document = ai("ask_gptchat", document)
	

	# print the answer
	print("bot> " + document.get('answer'))
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried GPTChat for completion in:", elapsed_time, "seconds")

	# get keyterms (and a related question)
	document_question = ai("gpt_keyterms", {"words": "user> %s\nbot> %s\n" % (question, document.get('answer'))})
	
	# if we don't have an error
	if not document_question.get('error', None):
		# build up document for weaviate PDFs store
		document_question.setdefault('filename', filename)
		document_question.setdefault('page_id',  "chat_%s" % username)
		document_question.setdefault('fragment', "This is a user added question, with the AI bot answering: user-%s> %s bot> %s" % (username, question, document.get('answer')))

		# insert the question into weaviate QandAs
		uuid = weaviate_update(document_question, "PDFs")

		# update featurebase doc_fragments
		sql = "INSERT INTO doc_fragments VALUES('%s', '%s', '%s', %s, 'user-%s', %s, '%s', '%s');" % (uuid, filename, title.replace("'", ""), 0, username, 0, "USER_CHAT", document_question.get('fragment').replace("'", "").replace("\n", "\\n"))
		featurebase_query({"sql": sql})

		if document_question.get('keyterms') and question:
			print("system> Keyterms linked: ", ", ".join(document_question.get('keyterms')))
			print("system> Inserting into FeatureBase...")
			for keyterm in document_question.get('keyterms'):
				sql = "INSERT INTO doc_keyterms VALUES('%s', ['%s'], ['%s'], ['%s'], ['%s']);" % (keyterm.lower(), filename, title, uuid, "chat_%s" % username)
				featurebase_query({"sql": sql})
			sql = "INSERT INTO doc_questions VALUES('%s', '%s', '%s', '%s', %s, '%s', '', '')" % (uuid, filename, title, document_question.get('question'), document_question.get('keyterms'), "chat_%s" % username)
			featurebase_query({"sql": sql})
