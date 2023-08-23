import sys
import json
import os

import config

from lib.database import featurebase_query, create_database
from lib.util import embeddings
from lib.ai import ai

# create the databases
databases = []
databases.append({"name": "doc_answers", "schema": "(_id string, filename string, title string, answer string, keyterms stringset, page_id string, answer_embedding vector(768));"})
for database in databases:
	create_database(database.get('name'), database.get('schema'))

# select the file
from lib.util import get_pdf_filename
filename = get_pdf_filename()
if filename:
    print("Selected PDF:", filename)

# select current questions
sql = f"SELECT * FROM doc_questions WHERE filename = '{filename}';"
fb_questions = featurebase_query({"sql": sql}).get('results')

if not fb_questions:
	print("Please run `python3 index_tandqs.py` first to extract for `%s`." % filename)
	sys.exit()

# itterate over questions
for question in fb_questions:
	# add cleanup for bad data
	"""
	if question.get('question') == "None" or question.get('question') == "null":
		print("Removing empty question.")
		remove_uuid = question.get('_id')
		sql = "DELETE FROM doc_questions WHERE _id = '%s'" % remove_uuid
		featurebase_query({"sql": sql})
	"""

	if question.get('answer', "null") == "null" or question.get('answer', "None") == "None" or question.get('answer') == None or question.get('answer') == '':
		print("system>", question.get('question'))
		
		# get question's original text fragment
		uuid = question.get('_id')
		keyterms = question.get('keyterms')

		# get the middle fragment
		sql = "SELECT * FROM doc_fragments WHERE _id = '%s'" % uuid
		middle_fragment = featurebase_query({"sql": sql}).get('results')[0] # get just one entry
		
		# get next fragment having prev_uuid the same as the middle fragment's uuid
		sql = "SELECT * FROM doc_fragments WHERE prev_id = '%s'" % uuid
		try:
			next_fragment = featurebase_query({"sql": sql}).get('results')[0] # get just one entry
		except:
			# probably the last fragment
			next_fragment = {"fragment": ""}
		
		# get prev fragment having its _id equal to the middle fragment's previous uuid
		try:
			sql = "SELECT * FROM doc_fragments WHERE _id = '%s'" % middle_fragment.get('prev_id')
			prev_fragment = featurebase_query({"sql": sql}).get('results')[0] # get just one entry
		except:
			# probably the first fragment
			prev_fragment = {"fragment": ""}

		# add half the previous fragment, the middle fragment and half the next fragment to concepts
		fragment_string = prev_fragment.get('fragment')[:int(len(prev_fragment.get('fragment'))/2)] + " " + middle_fragment.get('fragment') + " " + next_fragment.get('fragment')[:int(len(next_fragment.get('fragment'))/2)]

		# get related fragments
		related_uuids = []

		# tanmoto query on keyterms in doc_questions
		sql = f"SELECT *, tanimoto_coefficient(keyterms, (SELECT keyterms FROM doc_questions WHERE _id = '{uuid}')) AS distance FROM doc_questions ORDER BY distance DESC;))"
		results = featurebase_query({"sql": sql}).get('results')

		for i, result in enumerate(results):
			if result.get('_id') not in related_uuids and result.get('_id') != uuid:
				related_uuids.append(result.get('_id'))
			if i > 4: # just grab 5
				break

		# vector embedding for the question's fragment
		qf_embedding = embeddings([middle_fragment.get('fragment')])[0] # send one fragment (the middle one) and return one embedding

		# query using the question's fragment embeddings, to get other related questions
		sql = f"SELECT _id, question, cosine_distance({qf_embedding.get('embedding')}, question_embedding) AS distance FROM doc_questions ORDER BY distance ASC;"
		results = featurebase_query({"sql": sql}).get('results')

		for i, result in enumerate(results):
			if result.get('_id') not in related_uuids and result.get('_id') != uuid:
				related_uuids.append(result.get('_id'))
			if i > 4: # just grab 5
				break

		# print(related_uuids)

		for _uuid in related_uuids:
			if len(fragment_string) < 2048:
				sql = f"SELECT fragment FROM doc_fragments WHERE _id = '{_uuid}';"
				results = featurebase_query({"sql": sql}).get('results')
				fragment_string = fragment_string + results[0].get('fragment')

		# print(fragment_string)

		# build a document for sending to the ai
		document = {"origin_id": uuid, "question": question.get('question'), "text": fragment_string.strip(), "title": question.get('title'), "filename": question.get('filename'), "page_id": question.get('page_id')}
		document = ai("answer_question", document)

		# update if we have a good answer
		if document.get('error') == None:
			# print our results
			print("bot>", document.get('answer'))

			# embed the answer
			answer_embedding = embeddings([document.get('answer')])[0]

			# insert if we have a good answer and vector
			if len(answer_embedding.get('embedding')) == 768:
				# write to doc_answers
				sql = f"INSERT INTO doc_answers VALUES('{uuid}', '{question.get('filename')}', '{question.get('title')}', '{document.get('answer')}', {keyterms}, '{question.get('page_id')}', {answer_embedding.get('embedding')});"

				featurebase_query({"sql": sql})
			else:
				print("System> Got a bad vector size for the embedding.")
		else:
			print("bot> ", document.get('error'), document.get('answer'))
			print("bot> ")

