import weaviate
import config
import pprint
import sys
import json

from lib.database import weaviate_query, featurebase_query
from lib.ai import ai

query = input("enter query: ")


result = weaviate_query([query], "PDFs", ["fragment"])
print(result[0].get('fragment'), result[1].get('fragment'), result[2].get('fragment'), result[3].get('fragment'))