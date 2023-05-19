import weaviate
import config
import pprint
import sys
import json
import os

from lib.database import weaviate_schema, weaviate_update, weaviate_query, weaviate_object, featurebase_query
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
file_number = input("Enter the number of the file to process: ")
filename = files[int(file_number)]

# select current questions
sql = "SELECT * FROM doc_questions WHERE filename = '%s';" % filename
fb_questions = featurebase_query({"sql": sql}).get('results')

if not fb_questions:
	print("Please run `python3 index_tandqs.py` first to extract for `%s`." % filename)
	sys.exit()

# itterate over questions
for question in fb_questions:
	if question.get('question') == "None" or question.get('question') == "null":
		print("Removing empty question.")
		remove_uuid = question.get('_id')
		sql = "DELETE FROM doc_questions WHERE _id = '%s'" % remove_uuid
		featurebase_query({"sql": sql})

	if question.get('answer', "null") == "null" or question.get('answer', "None") == "None" or question.get('answer') == None:
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
		concepts = prev_fragment.get('fragment')[:int(len(prev_fragment.get('fragment'))/2)] + " " + middle_fragment.get('fragment') + " " + next_fragment.get('fragment')[:int(len(next_fragment.get('fragment'))/2)]

		# get related fragments to the concepts while moving toward existing keyterms
		weaviate_fragments = weaviate_query([concepts], "PDFs", ["fragment", "filename"], keyterms, filename)

		# base fragment string
		fragment_string = prev_fragment.get('fragment') + " " + middle_fragment.get('fragment') + " " + next_fragment.get('fragment')

		# operate over the fragments coming back from weaviate
		for fragment in weaviate_fragments:
			fragment_id = fragment.get("_additional").get('id')
			if fragment.get('filename') == filename and fragment_id != question.get('_id') and fragment_id != prev_fragment.get('_id') and fragment_id != next_fragment.get('_id'):
				if fragment.get("_additional").get('distance') < 0.15:
					if len(fragment_string) < 2048:
						fragment_string = fragment_string + "\nADDITIONAL CONTEXT:\n " + fragment.get('fragment')
					else:
						break

		# build a document for sending to the ai
		document = {"origin_id": uuid, "question": question.get('question'), "text": fragment_string.strip(), "title": question.get('title'), "filename": question.get('filename'), "page_number": question.get('page_num')}
		document = ai("answer_question", document)

		# get the probability and dimensionality
		document = ai("measure_probdim", document)

		# update if we have a good answer
		if document.get('error') == None:
			# print our results
			print("bot>", document.get('answer'))
			# print("bot>", document.get('probability'), document.get('dimensionality'))
			print("bot>", document.get('probability'))

			# update weaviate with query and answer information
			_uuid = weaviate_update(document, "QandAs")

			# update featurebase doc_questions
			sql = "INSERT INTO doc_questions VALUES('%s', '%s', '%s', '%s', %s, %s, '%s', '%s')" % (uuid, question.get('filename'), question.get('title'), question.get('question'), keyterms, question.get('page_num'), document.get('answer').replace("'", ""), document.get('probability'))
			featurebase_query({"sql": sql})
		else:
			print("bot> ", document.get('error'), document.get('answer'))
			print("bot> ")

