import weaviate
import config
import pprint
import sys
import json
import os
import time

from lib.database import weaviate_schema, weaviate_update, weaviate_query, weaviate_object, featurebase_query
from lib.ai import ai

# get files to index
dir_path = "./documents/"
files = os.listdir(dir_path)
print("\nDocuments Directory\n===================")
for i, file in enumerate(files):
    print("%s." % i, file)

# prompt for file entry
file_number = input("Enter the number of the file to process: ")
filename = files[int(file_number)]

# select current keyterms
sql = "SELECT * FROM doc_keyterms WHERE filename = '%s';" % filename
fb_keyterms = featurebase_query({"sql": sql}).get('results')

if not fb_keyterms:
	print("Please run `python3 index_tandqs.py` first to extract for `%s`." % filename)
	sys.exit()

max_keyterms = 0
max_keyterm = ""
max_uuids = []

for keyterm in fb_keyterms:
	if len(keyterm.get('uuids')) > max_keyterms:
		max_keyterms = len(keyterm.get('uuids'))
		max_keyterm = keyterm.get('_id')
		print(max_keyterm)
		max_uuids = keyterm.get('uuids')
		print(len(max_uuids))

"""
for uuid in max_uuids:
	start_time = time.time()
	print(weaviate_object(uuid, "PDFs"))
	end_time = time.time()
	delta_time = end_time - start_time
	print(f"Time taken: {delta_time} seconds")
"""

print(max_keyterm, max_uuids)



