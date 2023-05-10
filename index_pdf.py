import time
import sys
import os
import hashlib

import PyPDF2
from pdf2image import convert_from_path

import nltk


# tokenizer
nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
print("Tokenizer loaded...")

from lib.ai import ai
from lib.database import featurebase_query
from lib.database import weaviate_schema, weaviate_query, weaviate_update
from lib.util import create_databases

# create featurebase databases
create_databases()

# create Weaviate schema
weaviate_schema = weaviate_schema("PDFs")

if weaviate_schema.get("error"):
	print("Weaviate returned an error. Check your credentials!")
	sys.exit()
else:
	print("Found Weaviate schema with class name: %s" % weaviate_schema.get('class'))	

# get files to index
dir_path = "./documents/"
files = os.listdir(dir_path)
print("\nDocuments Directory\n===================")
for i, file in enumerate(files):
    print("%s." % i, file)

# prompt for file entry
file_number = input("Enter the number of the file to index: ")
filename = files[int(file_number)]

# creating a pdf file object
pdfFileObj = open("documents/%s" % filename, 'rb')

# creating a pdf reader object 
pdfReader = PyPDF2.PdfReader(pdfFileObj)

# get or set title
if pdfReader.metadata.get('title', None):
	title = pdfReader.metadata.get('title')
else:
	title = None

# number of pages in pdf file 
num_pages = len(pdfReader.pages)

# images directory
if not os.path.exists("images"):
    os.makedirs("images")
    print(f"Directory 'images' created successfully!")
else:
    print(f"Directory 'images' already exists.")

# convert PDF
images = convert_from_path('documents/%s' % filename)

# Path of the new directory to be created for images
new_dir_path = os.path.join('images', filename.split(".")[0])

# Create the new directory if it doesn't already exist
if not os.path.exists(new_dir_path):
    os.mkdir(new_dir_path)
    print(f"Directory {new_dir_path} created successfully.")
else:
    print(f"Directory {new_dir_path} already exists.")

if os.path.exists(f"{new_dir_path}/page" + str(num_pages-1) + '.jpg'):
	print("Found existing images for PDF.")
else:
	print("Exporting images for PDF.")
	for i in range(len(images)):
		# Save pages as images in the pdf (add 1 to the page index to ensure we match pages)
		images[i].save(f'{new_dir_path}/page'+ str(i+1) +'.jpg', 'JPEG')

# extract text
from google.cloud import vision
import io
client = vision.ImageAnnotatorClient()

# loop through pages
start_page = 1
prev_uuid = "FIRST_BAG"
next_uuid = "LAST_BAG"

for page_num in range(start_page, num_pages+1):
	fragment_num = 1

	# open image
	with io.open(f'{new_dir_path}/page%s.jpg' % page_num, 'rb') as image_file:
		content = image_file.read()

	# extract text
	image = vision.Image(content=content)
	response = client.text_detection(image=image)
	texts = response.text_annotations

	print("Reading page number %s." % page_num)
	
	# use the first extraction only (others are single words)
	for text in texts:
		# get title if we don't have it
		if title is None and page_num == 1:
			# use the first page and AI to try to get it
			document = {"text": text.description[:512]}
			if not document.get('title', None):
				title = ai("get_title", document).get('title')
				if not title:
					title = input("Couldn't find a title. Enter a title for the PDF: ")

		_text = '\n"{}"'.format(text.description)

		words = ""
		for i, entry in enumerate(tokenizer.tokenize(_text)):
			if entry == "":
				continue

			words = words + " " + entry.replace("\n", " ")
			if len(words) > 512:
				document = {
					"filename": filename,
					"page_number": page_num,
					"fragment": words.strip()
				}

				# handle 500s from weaviate (probably due to openai limits)
				for x in range(5):
					try:
						uuid = weaviate_update(document, "PDFs")
						break
					except Exception as ex:
						print("Error with Weaviate ", x)
						print(ex)
						print(document)
						time.sleep(5)

				# update featurebase doc_pages page string id
				page_id = "%s_%s" % (page_num, hashlib.md5(filename.encode()).hexdigest()[:8])
				query = "INSERT INTO doc_pages VALUES('%s', '%s', '%s', ['%s']);" % (page_id, filename, title, uuid)
				featurebase_query({"sql": query})

				# update featurebase doc_fragments
				query = "INSERT INTO doc_fragments VALUES('%s', '%s', '%s', %s, %s, '%s', '%s');" % (uuid, filename, title, page_num, fragment_num, prev_uuid, words.replace("'", ""))

				featurebase_query({"sql": query})

				# uuid tracking
				prev_uuid = uuid

				fragment_num = fragment_num + 1
				words = ""

		if words != "" and len(words) > 3:
			document = {
				"filename": filename,
				"page_number": page_num,
				"fragment": words.strip()
			}

			# handle 500s from weaviate (probably due to openai limits)
			for x in range(5):
				try:
					uuid = weaviate_update(document, "PDFs")
					break
				except Exception as ex:
					print("try ", x)					
					print(ex)
					print(document)
					time.sleep(5)

			# update featurebase doc_pages page string id
			page_id = "%s_%s" % (page_num, hashlib.md5(filename.encode()).hexdigest()[:8])
			query = "INSERT INTO doc_pages VALUES('%s', '%s', '%s', ['%s']);" % (page_id, filename, title, uuid)
			featurebase_query({"sql": query})

			# update featurebase doc_fragments
			query = "INSERT INTO doc_fragments VALUES('%s', '%s', '%s', %s, %s, '%s', '%s');" % (uuid, filename, title, page_num, fragment_num, prev_uuid, words.replace("'", ""))
			featurebase_query({"sql": query})
			
			# uuid tracking
			prev_uuid = uuid

			fragment_num = fragment_num + 1
			words = ""

		# don't use the single extracted words
		break


# close the file
pdfFileObj.close()

print("Done indexing PDF!")