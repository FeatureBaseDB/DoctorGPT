import os
import string
import random
import uuid
import contextlib
import torch

from InstructorEmbedding import INSTRUCTOR

from lib.database import featurebase_query

import warnings
warnings.filterwarnings("ignore")

def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


def embeddings(string_array):

	# idiots be idioting
	# supress or handle the parallel errors from HF tokenizers
	# Set the environment variable
	os.environ["TOKENIZERS_PARALLELISM"] = "true"

	# supresses 'load INSTRUCTOR_Transformer' & 'max_seq_length 512' outputs
	with contextlib.redirect_stdout(None):

		# load the model
		model = INSTRUCTOR('hkunlp/instructor-large')

		# encode the strings
		embeddings = model.encode(string_array, output_value="sentence_embedding").tolist()

		# build results list
		results = []

		# add to the results
		for i, embedding in enumerate(embeddings):
			_uuid = uuid.uuid4()
			processed_embedding = [float("{:.15f}".format(number)) for number in embedding]

			results.append({"uuid": str(_uuid), "string": string_array[i], "embedding": processed_embedding})

	return results

def get_pdf_filename():
    dir_path = "./documents/"
    files = os.listdir(dir_path)

    pdf_files = [file for file in files if file.lower().endswith(".pdf")]

    print("\nPDF Documents\n===================")
    for i, file in enumerate(pdf_files):
        print("%s. %s" % (i, file))

    try:
        index = int(input("Enter the index number of the document: "))
        if 0 <= index < len(pdf_files):
            return pdf_files[index]
        else:
            print("Invalid index number.")
            return None
    except ValueError:
        print("Invalid input. Please enter a valid index number.")
        return None