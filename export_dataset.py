import sys
import json
import os

import config

from lib.database import featurebase_query, create_database
from lib.util import embeddings
from lib.ai import ai

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

write_file = "./training/"+filename.split('.')[0]+"_train.jsonl"
if os.path.exists(write_file):
	os.remove(write_file)

# itterate over questions
for question in fb_questions:
	# check if we have the answer
	sql = f"SELECT * FROM doc_answers WHERE _id = '{question.get('_id')}';"
	answer = featurebase_query({"sql": sql}).get('results')[0]

	# get the fragment
	sql = f"SELECT * FROM doc_fragments WHERE _id = '{question.get('_id')}';"
	fragment = featurebase_query({"sql": sql}).get('results')[0]

	with open(f'{write_file}', 'a') as file:
		file.write(json.dumps({"context": fragment.get('fragment'), "question": question.get('question'), "answers": {"text": [answer.get('answer')], "answer_start": [answer.get('answer_location')]}}))
		file.write("\n")
