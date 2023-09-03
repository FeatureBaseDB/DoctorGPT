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

from lib.database import featurebase_query

import config

# supress OpenAI resource warnings for unclosed sockets
import warnings
warnings.filterwarnings("ignore")

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
		return document


# helper functions
# ================

# load template
def load_template(name="default"):
	# file path
	lib_path = os.path.dirname(__file__)
	file_path = "%s/templates/%s.txt" % (lib_path, name)

	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			template = Template(f.read())
	except Exception as ex:
		print(ex)
		print("exception in loading template")
		template = None

	return template


# random strings
def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))


# gptchat
def gpt_chat_keywords(words):
	try:
		completion = openai.ChatCompletion.create(
		  model = config.model,
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

# gptchat
def gpt_chat_complete(words, keyterms, title, question):
	try:
		messages = [
			{"role": "system", "content": "Answer questions from the document %s whose fragments are provided here, but only mention the document and do not refer to 'fragments'." % title},			
			{"role": "user", "content": "keyterms are: " + ", ".join(keyterms) + "\nfragment: '''"+words+"'''\n"+question}
		]

		completion = openai.ChatCompletion.create(
			model = config.model,
			messages = messages
		)

		answer = completion.choices[0].message.content

	except Exception as ex:
		print(ex)
		answer = "Call to OpenAI chat failed: %s" % ex

	return answer

# completion
def gpt3_completion(prompt, temperature=0.95, max_tokens=512, top_p=1, fp=0, pp=0):
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

def gpt3_dict_completion(prompt, temperature=0.90, max_tokens=512, top_p=1, fp=0, pp=0):
	answer = gpt3_completion(prompt, temperature, max_tokens, top_p, fp, pp)
	
	try:
		python_dict = eval('{%s' % answer.replace('\n', ""))
	except Exception as ex:
		python_dict = {}
		python_dict['error'] = "Call to OpenAI completion failed: %s" % ex
		python_dict['dict_string'] = answer
		python_dict['answer'] = "An error occurred talking to OpenAI. Try again in a minute."

	return python_dict


# model functions
# ===============

# keyterms and questions
@model
def gpt_keyterms(document):
	# load openai key then drop it from the document
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	# substitute things
	template = load_template("get_tandqs")
	prompt = template.substitute(document)
	
	ai_dict = gpt3_dict_completion(prompt)

	document.setdefault('keyterms', ai_dict.get('keyterms'))
	document.setdefault('question', ai_dict.get('question'))
	document.setdefault('error', ai_dict.get('error', None))

	return document

@model
def get_title(document):
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	# substitute things
	template = load_template("get_title")
	prompt = template.substitute(document)
	
	try:
		document.setdefault('title', gpt3_dict_completion(prompt).get('title'))
	except Exception as ex:
		document.setdefault('title', None)

	return document


@model
def answer_question(document):
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	# substitute things
	template = load_template("answer_question")
	prompt = template.substitute(document)

	gpt_document = gpt3_dict_completion(prompt)

	try:
		document.setdefault('answer', gpt_document.get('answer'))
	except Exception as ex:
		document.setdefault('answer', None)

	try:
		document.setdefault('word_lock_on', gpt_document.get('word_lock_on'))
	except Exception as ex:
		document.setdefault('word_lock_on', None)

	return document


@model
def ask_gpt(document):
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	# substitute things
	template = load_template("doc_convo")
	
	prompt = template.substitute(document)
	gpt_document = gpt3_dict_completion(prompt)

	try:
		document.setdefault('answer', gpt_document.get('answer'))
	except Exception as ex:
		document.setdefault('answer', None)

	try:
		# just grab 3 keyterms
		document.setdefault('keyterms', gpt_document.get('keyterms')[:5])
	except Exception as ex:
		document.setdefault('keyterms', [])

	return document

@model
def ask_gptchat(document):
	# load openai key then drop it from the document
	openai.api_key = document.get('openai_token')
	document.pop('openai_token', None)

	answer = gpt_chat_complete(document.get('text'), document.get('keyterms'), document.get('title'), document.get('question'))

	document.setdefault('answer', answer)
	return document