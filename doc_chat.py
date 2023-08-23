import random
import sys
import json
import os
import time

import config

from lib.util import random_string, embeddings

from lib.database import featurebase_query
from lib.ai import ai

from collections import Counter

def get_top_ranked_uuids(uuid_list):
    # Calculate the frequency of each UUID
    uuid_counts = Counter(uuid_list)
    
    # Sort UUIDs based on frequency in descending order
    sorted_uuids = sorted(uuid_counts, key=lambda uuid: uuid_counts[uuid], reverse=True)
    
    # Return the top 8 ranked UUIDs
    top_ranked_uuids = sorted_uuids[:8]
    return top_ranked_uuids

# select the file
from lib.util import get_pdf_filename
filename = get_pdf_filename()
if filename:
    print("Selected PDF:", filename)

# user
username = random_string(4)

# build history and session
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

history = FileHistory(".DoctorGPT")
session = PromptSession(history=history)

print("Entering conversation with %s. Use ctrl-C to end interaction." % filename)

while True:
	# get a query from the user
	try:
		query = session.prompt("human-%s[%s]> " % (username, filename))
		if query == "" or query.strip() == "":
			continue

	except KeyboardInterrupt:
		print("system>", random.choice(["Bye!", "Later!", "Nice working with you."]))
		sys.exit()

	# related uuids and keyterms
	related_uuids = []
	related_keyterms = []

	# vector for the query
	print("system> Embedding the query...")
	start_time = time.time()
	query_embedding = embeddings([query])[0]
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Embedded the query (locally) in:", elapsed_time, "seconds.")

	# query using the query embedding, to get related questions
	start_time = time.time()
	sql = f"SELECT _id, question, keyterms, cosine_distance({query_embedding.get('embedding')}, question_embedding) AS distance FROM doc_questions ORDER BY distance ASC;"
	results = featurebase_query({"sql": sql}).get('results')
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried FeatureBase for related questions in:", elapsed_time, "seconds")

	for i, result in enumerate(results):
		related_uuids.append(result.get('_id'))
		for keyterm in result.get('keyterms'):
			if keyterm not in related_keyterms:
				related_keyterms.append(keyterm)
		if i > 4: # just grab 5
			break

	# query using the query embedding, to get related answers
	start_time = time.time()
	sql = f"SELECT _id, answer, keyterms, cosine_distance({query_embedding.get('embedding')}, answer_embedding) AS distance FROM doc_answers ORDER BY distance ASC;"
	print(sql)
	results = featurebase_query({"sql": sql}).get('results')
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried FeatureBase for related answers in:", elapsed_time, "seconds")

	for i, result in enumerate(results):
		related_uuids.append(result.get('_id'))
		for keyterm in result.get('keyterms'):
			if keyterm not in related_keyterms:
				related_keyterms.append(keyterm)
		if i > 4: # just grab 5
			break

	start_time = time.time()
	sql = f"SELECT uuids, tanimoto_coefficient({related_uuids}, uuids) AS distance FROM doc_keyterms ORDER BY distance;"
	results = featurebase_query({"sql": sql}).get('results')
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried FeatureBase for related documents by keyterms in:", elapsed_time, "seconds")	

	for i, result in enumerate(results):
		for uuid in result.get('uuids'):
			related_uuids.append(uuid)
		if i > 2: # just do a few
			break
	
	start_time = time.time()
	sql = f"SELECT _id, fragment, cosine_distance({query_embedding.get('embedding')}, fragment_embedding) AS distance FROM doc_fragments ORDER BY distance ASC;"
	results = featurebase_query({"sql": sql}).get('results')
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried FeatureBase for related documents in:", elapsed_time, "seconds")	


	for i, result in enumerate(results):
		related_uuids.append(result.get('_id'))
		if i > 4: # just do a few
			break

	top_referenced_uuids = get_top_ranked_uuids(related_uuids)


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
		if len(fragments) < 7779:
			fragments = fragments + " " + result.get('fragment')

	# indicate we're calling the AI
	start_time = time.time()
	print("bot> Querying GPT...")

	# build the document for the AI calls
	document = {"question": query, "text": fragments, "keyterms": related_keyterms, "title": title}

	# call the AI
	document = ai("ask_gptchat", document)
	

	# print the answer
	print("bot> " + document.get('answer'))
	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried GPTChat for completion in:", elapsed_time, "seconds")

	"""
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
		if uuid != "FAILED":
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
	"""