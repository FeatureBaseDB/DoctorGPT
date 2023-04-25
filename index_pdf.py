import time
import sys
import os

import PyPDF2
from pdf2image import convert_from_path

import nltk

# tokenizer
nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
print("Tokenizer loaded...")

from lib.ai import ai

from lib.database import featurebase_query

# create FeatureBase database
fb_table = "doc_keyterms"
fb_query = featurebase_query(
	{
		"sql": "CREATE TABLE %s (_id string, filename string, uuids stringset, page_num idset);" % fb_table
	}
)

# check status
if fb_query.get('error'):
	if "exists" in fb_query.get('error'):
		print("FeatureBase database `%s` already exists." % fb_table)
	else:
		print("FeatureBase returned an error. Check your credentials!")
else:
	print("Created `%s` database on FeatureBase Cloud." % fb_table)

from lib.database import weaviate_schema, weaviate_query, weaviate_update

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
		# Save pages as images in the pdf
		images[i].save(f'{new_dir_path}/page'+ str(i) +'.jpg', 'JPEG')

# extract text
from google.cloud import vision
import io
client = vision.ImageAnnotatorClient()

# loop through pages
start_page = 0
for num_page in range(start_page, num_pages):
	# open image
	with io.open(f'{new_dir_path}/page%s.jpg' % num_page, 'rb') as image_file:
		content = image_file.read()

	# extract text
	image = vision.Image(content=content)
	response = client.text_detection(image=image)
	texts = response.text_annotations

	print("Reading page number %s." % num_page)
	
	# use the first extraction only (others are single words)
	for text in texts:
		_text = '\n"{}"'.format(text.description)

		words = ""
		for i, entry in enumerate(tokenizer.tokenize(_text)):
			if entry == "":
				continue

			words = words + " " + entry.replace("\n", " ")
			if len(words) > 512:
				ai_keywords = ai("gpt_keywords", {"words": words})

				time.sleep(1)
				document = {
					"filename": filename,
					"page_number": num_page,
					"fragment": words.strip()
				}

				# handle 500s from weaviate (probably due to openai limits)
				for x in range(5):
					try:
						uuid = weaviate_update(document, "PDFs")
						break
					except Exception as ex:
						print(ex)
						print(document)
						time.sleep(5)

				for keyterm in ai_keywords:
					if keyterm != "error":
						query = "INSERT INTO %s VALUES('%s', '%s', ['%s'], [%s]);" % (fb_table, keyterm.lower(), filename, uuid, num_page)
						featurebase_query({"sql": query})

				words = ""

		if words != "" and len(words) > 23:
			ai_doc = ai("gpt_keywords", {"words": words})

			time.sleep(1)
			document = {
				"filename": filename,
				"page_number": num_page,
				"fragment": words.strip()
			}

			# handle 500s from weaviate (probably due to openai limits)
			for x in range(5):
				try:
					uuid = weaviate_update(document, "PDFs")
					break
				except Exception as ex:
					print(ex)
					print(document)
					time.sleep(5)

			for keyterm in ai_doc:
				if keyterm != "error":
					query = "INSERT INTO %s VALUES('%s', '%s', ['%s'], [%s]);" % (fb_table, keyterm.lower(), filename, uuid, num_page)
					featurebase_query({"sql": query})

			words = ""

		# don't use the single extracted words
		break
