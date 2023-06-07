import time
import sys
import os
import hashlib

# pdf handling libs
import PyPDF2
from pdf2image import convert_from_path

# tokenizer for parsing things
import nltk
nltk.download('punkt')
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
print("Tokenizer loaded...")

# import AI prompt handling functions
from lib.ai import ai

# import database methods
from lib.database import featurebase_query
from lib.database import weaviate_schema, weaviate_query, weaviate_update

# create featurebase databases
from lib.util import create_databases
create_databases()

# create a Weaviate schema
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

# operate on the PDF
#
# prompt for file to index
file_number = input("Enter the number of the file to index: ")
filename = files[int(file_number)]

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
#
# end operating on PDF

# extract text from images
from google.cloud import vision
import io
client = vision.ImageAnnotatorClient()

# start with page 1
start_page = 1
prev_uuid = "FIRST_BAG" # used for creating a linked list in FeatureBase

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
	print("Reading page number %s of %s." % (page_num, num_pages))
	
	# use the first extraction only (other entries in the list are single words)
	try:
		text = texts[0]
	except:
		print("error in detection")

	# get title from the first page if we don't have it
	if title is None and page_num == 1:
		# create a document for the AI to operate on
		document = {"text": text.description[:512]} # use the first 512 characters of the page
		
		if not document.get('title', None):
			# call the AI to get the title
			title = ai("get_title", document).get('title')
			if not title:
				title = input("Couldn't find a title. Enter a title for the PDF: ")

	# clean up the text on which to operate
	_text = text.description.replace("'", "").replace("\n", " ")

	# create a decently cleaned up string of words of a given length
	words = ""

	# loop over the tokenized text
	for i, entry in enumerate(tokenizer.tokenize(_text)):
		# continue if entry is empty
		if entry == "":
			continue

		# build up the words string
		words = words + " " + entry.replace("\n", " ")

		# process words if the chunk is > 512 characters or we are on the last chunk
		if len(words) > 512 or i == len(tokenizer.tokenize(_text)) - 1:
			# create a document to send to weaviate
			document = {
				"filename": filename,
				"page_number": page_num,
				"fragment": words.strip()
			}

			# handle 500s from weaviate with a sleep and retry
			# occurs for unknown reason...
			for x in range(5):
				try:
					uuid = weaviate_update(document, "PDFs")
					break
				except Exception as ex:
					print(ex)
					time.sleep(5)

			# build a page_id for the page fragment
			page_id = "%s_%s" % (page_num, hashlib.md5(filename.encode()).hexdigest()[:8])

			# update featurebase doc_pages table
			sql = "INSERT INTO doc_pages VALUES('%s', '%s', '%s', ['%s']);" % (page_id, filename, title.replace("'", ""), uuid)
			featurebase_query({"sql": sql})

			# update featurebase doc_fragments
			sql = "INSERT INTO doc_fragments VALUES('%s', '%s', '%s', %s, '%s', %s, '%s', '%s');" % (uuid, filename, title.replace("'", ""), page_num, page_id, fragment_num, prev_uuid, words.replace("'", ""))
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

print("Done indexing PDF!")