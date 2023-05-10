import time
import sys
import os

from lib.ai import ai

from lib.database import featurebase_query
from lib.util import create_databases

# create FeatureBase databases
create_databases()

# get files to index
dir_path = "./documents/"
files = os.listdir(dir_path)
print("\nDocuments Directory\n===================")
for i, file in enumerate(files):
    print("%s." % i, file)

# prompt for file entry
file_number = input("Enter the number of the file to process: ")
filename = files[int(file_number)]

# read the pages in from the PDF
fb_result = featurebase_query(
	{
		"sql": "SELECT * FROM doc_pages WHERE filename = '%s';"  % filename
	}
).get('data')

if not fb_result:
	print("Please run `python3 index_pdfs.py` first to index `%s`." % filename)
	sys.exit()

for item in fb_result:
	for uuid in item[3]:
		sql = "SELECT * FROM doc_fragments WHERE _id = '%s';"  % uuid
		try:
			fb_result = featurebase_query(
				{
					"sql": sql
				}
			).get('results')[0] # first and only result
		except Exception as ex:
			print(ex)
			print(sql)
			continue

		# fragment words from doc_fragments
		words = fb_result.get('fragment')

		page_num = item[0].split("_")[0]
		filename = item[1]
		title = item[2]
		print("Extracting for page %s of %s." % (page_num, filename))

		# handle completion errors
		for x in range(5):
			document = ai("gpt_keyterms", {"words": words})
			if not document.get('error', None):
				break
			else:
				print(document.get('error'))
				print("Sleeping for 5 seconds and then trying again.")
				time.sleep(5)

		if not document.get('error', None):
			for keyterm in document.get('keyterms'):
				query = "INSERT INTO doc_keyterms VALUES('%s', '%s', '%s', ['%s'], [%s]);" % (keyterm.lower(), filename, title, uuid, page_num)
				featurebase_query({"sql": query})
			query = "INSERT INTO doc_questions VALUES('%s', '%s', '%s', '%s', %s, %s, '', '', '')" % (uuid, filename, title, document.get('question'), document.get('keyterms'), page_num)
			featurebase_query({"sql": query})

