import os
import sys
import datetime
import random
import string
import requests

import openai

import traceback

from string import Template

from bs4 import BeautifulSoup

from lib.database import weaviate_schema, weaviate_query, weaviate_update
from lib.database import featurebase_query

import config

# AI model call by method name
models = {}
model = lambda f: models.setdefault(f.__name__, f)

def ai(model_name="none", document={}):
	# get the user's API token	
	openai_token = config.openai_token

	if not openai_token:
		# rewrite to match document flow
		document['error'] = "model %s errors with no token." % (model_name)
		document['explain'] = "I encountered an error talking with OpenAI."
		document['template_file'] = "eject_document"
		return document
	else:
		# set token for model to use
		document['openai_token'] = openai_token

	# call the model
	try:
		document = models[model_name](document)
		return document

	except Exception as ex:
		if config.dev == "True":
			print(traceback.format_exc())

		document['error'] = "model *%s* errors with %s." % (model_name, ex)
		document['explain'] = "I encountered an error talking with my AI handler."
		document['template_file'] = "eject_document"
		return document


# helper functions
# ================

# load template
def load_template(name="default"):
	# file path
	lib_path = os.path.dirname(__file__)
	file_path = "%s/templates/%s.txt" % (lib_path, name)

	try:
		with open(file_path, 'r') as f:
			template = Template(f.read())
	except Exception as ex:
		print(ex)
		print("exception in loading template")
		template = None

	return template


# random strings
def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


# gpt3 dense vectors
def gpt3_embedding(content, engine='text-similarity-ada-001'):
	content = content.encode(encoding='ASCII',errors='ignore').decode()
	response = openai.Embedding.create(input=content,engine=engine)
	vector = response['data'][0]['embedding']  # this is a normal list
	return vector


# gptchat
def gpt_chat_keywords(words):
	try:
		completion = openai.ChatCompletion.create(
		  model="gpt-4",
		  messages = [
			{"role": "system", "content": "You complete python lists from a fragment of a document. Don't create numeric keywords or use URLs for keywords. Don't use stopwords or words that aren't relevant to the document."},
			{"role": "user", "content": "fragment: '''"+words+"'''\n# create a python list of ten (10) keyterms for a back of book index\nkeyterms = ["}
		  ]
		)
		answer = completion.choices[0].message

	except Exception as ex:
		print(ex)
		answer = "Call to OpenAI chat failed: %s" % ex

	return answer


# completion
def gpt3_completion(prompt, temperature=0.95, max_tokens=256, top_p=1, fp=0, pp=0):
	try:
		# call to OpenAI completions
		response = openai.Completion.create(
		  model = "text-davinci-003",
		  prompt = prompt,
		  temperature = temperature,
		  max_tokens = max_tokens,
		  top_p = top_p,
		  frequency_penalty = fp,
		  presence_penalty = pp,
		  timeout = 20
		)

		answer = response['choices'][0]['text']
	except Exception as ex:
		answer = "Call to OpenAI completion failed: %s" % ex

	return answer

def gpt3_dict_completion(prompt, temperature=0.90, max_tokens=256, top_p=1, fp=0, pp=0):
	answer = gpt3_completion(prompt, temperature, max_tokens, top_p, fp, pp)
	
	try:
		print(answer.replace('\n', ""))
		python_dict = eval('{%s' % answer.replace('\n', ""))
	except Exception as ex:
		python_dict = {}
		python_dict['error'] = "Call to OpenAI completion failed: %s" % ex
		python_dict['dict_string'] = answer
		python_dict['answer'] = "An error occurred talking to OpenAI. Try again in a minute."

	return python_dict


# model functions
# ===============

# mirror text for indexing
@model
def gpt_keywords(document):
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	for attempt in range(4):
		try:
			answer = gpt_chat_keywords(document.get('words')).get('content', "").replace('\n', "")
			python_array = eval("[%s" % answer)
			break
		except Exception as ex:
			print("Forcing GPT to output a valid Python array...")
			python_array = ['error']

	return python_array


@model
def ask_gpt(document):
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	# substitute things
	template = load_template("chat")
	prompt = template.substitute(document)

	answer = gpt3_completion(prompt).strip('\n').strip('"')
	document['answer'] = answer

	return document