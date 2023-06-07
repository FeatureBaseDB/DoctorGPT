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

# user
username = random_string(4)

# get files to process
dir_path = "./documents/"
files = os.listdir(dir_path)
print("\nDocuments Directory\n===================")
for i, file in enumerate(files):
	print("%s." % i, file)

# prompt for file entry
file_number = input("Enter the number of the file to chat with: ")
filename = files[int(file_number)]

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
	weaviate_results = weaviate_query([question], "PDFs", ["filename", "page_id", "fragment"], filename=filename)

	end_time = time.time()
	elapsed_time = end_time - start_time
	print("system> Queried Weaviate for questions in:", elapsed_time, "seconds")
	print("system> %s results found." % len(weaviate_results))
	print(weaviate_results[0])
	print(weaviate_results[0].get('fragment'))

