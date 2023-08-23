import time
import sys
import os
import hashlib

# pdf handling libs
import PyPDF2
from pdf2image import convert_from_path

# embeddings
from lib.util import embeddings

# tokenizer for parsing things
import nltk
nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
print("Tokenizer loaded...")

# import AI prompt handling functions
from lib.ai import ai

# import database methods
from lib.database import featurebase_query, create_database

# create the databases
databases = []
databases.append({"name": "doc_pages", "schema": "(_id string, filename string, title string, uuids stringset)"})
databases.append({"name": "doc_fragments", "schema": "(_id string, filename string, title string, page_num int, page_id string, fragment_num int, prev_id string, fragment string, fragment_embedding vector(768))"})
for database in databases:
	create_database(database.get('name'), database.get('schema'))

# select the file
from lib.util import get_pdf_filename
filename = get_pdf_filename()
if filename:
    print("Selected PDF:", filename)

# create a pdf file object
pdfFileObj = open("documents/%s" % filename, 'rb')

# create a pdf reader object 
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
    print(f"system> Directory 'images' created successfully!")
else:
    print(f"system> Directory 'images' already exists.")

# convert PDF
images = convert_from_path('documents/%s' % filename)

# Path of the new directory to be created for images
new_dir_path = os.path.join('images', filename.split(".")[0])

# Create the new directory if it doesn't already exist
if not os.path.exists(new_dir_path):
    os.mkdir(new_dir_path)
    print(f"system> Directory {new_dir_path} created successfully.")
else:
    print(f"system> Directory {new_dir_path} already exists.")

if os.path.exists(f"{new_dir_path}/page" + str(num_pages-1) + '.jpg'):
	print("system> Found existing images for PDF.")
else:
	print("system> Exporting images for PDF.")
	for i in range(len(images)):
		# Save pages as images in the pdf (add 1 to the page index to ensure we match pages)
		images[i].save(f'{new_dir_path}/page'+ str(i+1) +'.jpg', 'JPEG')
#
# end operating on PDF

# extract text from images
from google.cloud import vision
import io
client = vision.ImageAnnotatorClient()

# start with last page or page 1
prev_uuid = "FIRST_BAG" # used for creating a linked list in FeatureBase
try:
	sql = f"SELECT max(page_num) AS max_page, filename, title FROM doc_fragments WHERE filename = '{filename}' GROUP BY filename, title ORDER BY max_page DESC;"
	results = featurebase_query({"sql": sql}).get('results')
	start_page = results[0].get('max_page') - 1
	title = results[0].get('title')
	print(f"system> Found existing pages for '{title}'. Starting at page {start_page}.")
except Exception as ex:
	start_page = 1

# stash errant characters from previous page
word_stash = ""

# loop through the pages
for page_num in range(start_page, num_pages+1):
	fragment_num = 1

	# open image for the page
	with io.open(f'{new_dir_path}/page%s.jpg' % page_num, 'rb') as image_file:
		content = image_file.read()

	# extract the text using Google Vision
	image = vision.Image(content=content)
	response = client.text_detection(image=image)
	texts = response.text_annotations

	# output completion status
	print("system> Reading page number %s of %s." % (page_num, num_pages))
	
	# use the first extraction only (other entries in the list are single words)
	try:
		text = texts[0]
	except:
		print("system> Error in detection, likely due to a blank page.")
		continue

	# get title from the first page if we don't have it
	if title is None and page_num == 1:
		# create a document for the AI to operate on
		document = {"text": text.description[:512]} # use the first 512 characters of the page
		
		if not document.get('title', None):
			# call the AI to get the title
			title = ai("get_title", document).get('title')
			if not title:
				title = input("system> Couldn't find a title. Enter a title for the PDF: ")

	# clean up the text on which to operate
	_text = text.description.replace("'", "").replace("\n", " ")

	# create a decently cleaned up string of words of a given length
	words = word_stash

	# loop over the tokenized text
	for i, entry in enumerate(tokenizer.tokenize(_text)):
		# continue if entry is empty
		if entry == "":
			continue

		# build up the words string
		words = words + " " + entry.replace("\n", " ")

		# process words if the chunk is > 512 characters or we are on the last chunk
		if i == len(tokenizer.tokenize(_text)) - 1 and len(words) < 20:
			word_stash = words
			print("system> Stashing words for next page.")
			continue # exit loop over tokenized text
		else:
			word_stash = ""
		
		if len(words) > 512 or i == len(tokenizer.tokenize(_text)) - 1:
			# build a page_id for the page fragment
			page_id = "%s_%s" % (page_num, hashlib.md5(filename.encode()).hexdigest()[:8])

			# embed (goodbye to weaviate retries)
			_embeddings = embeddings([words.strip()])[0]
			uuid = _embeddings.get('uuid')

			# update featurebase doc_pages table
			sql = "INSERT INTO doc_pages VALUES('%s', '%s', '%s', ['%s']);" % (page_id, filename, title.replace("'", ""), uuid)
			featurebase_query({"sql": sql})

			# update featurebase doc_fragments
			sql = "INSERT INTO doc_fragments VALUES('%s', '%s', '%s', %s, '%s', %s, '%s', '%s', %s);" % (uuid, filename, title.replace("'", ""), page_num, page_id, fragment_num, prev_uuid, words.replace("'", ""), _embeddings.get('embedding'))
			featurebase_query({"sql": sql})

			# track the previous UUID for the linked list
			prev_uuid = uuid

			# which fragment we are on
			fragment_num = fragment_num + 1

			# wipe the words
			words = ""

	# end loop over tokenized text


# close the file
pdfFileObj.close()

print("system> Done indexing PDF!")