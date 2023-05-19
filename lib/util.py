import string
import random

from lib.database import featurebase_query

def random_string(size=6, chars=string.ascii_letters + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def drop_databases():
	# create FeatureBase database
	fb_query = featurebase_query(
		{
			"sql": "DROP TABLE doc_pages;"
		}
	)
	# create FeatureBase database
	fb_query = featurebase_query(
		{
			"sql": "DROP TABLE doc_keyterms;"
		}
	)
	# create FeatureBase database
	fb_query = featurebase_query(
		{
			"sql": "DROP TABLE doc_questions;"
		}
	)
	# create FeatureBase database
	fb_query = featurebase_query(
		{
			"sql": "DROP TABLE doc_fragments;"
		}
	)
def create_databases():
	# create FeatureBase database
	fb_table = "doc_pages"
	fb_query = featurebase_query(
		{
			"sql": "CREATE TABLE %s (_id string, filename string, title string, uuids stringset);" % fb_table
		}
	)

	# check status
	if fb_query.get('error'):
		if "exists" in fb_query.get('error'):
			print("FeatureBase database `%s` already exists." % fb_table)
		else:
			print(fb_query.get("explain"))
			print("FeatureBase returned an error. Check your credentials or create statement!")
			sys.exit()
	else:
		print("Created `%s` database on FeatureBase Cloud." % fb_table)

	# create FeatureBase database
	fb_table = "doc_keyterms"
	fb_query = featurebase_query(
		{
			"sql": "CREATE TABLE %s (_id string, filename string, title string, uuids stringset, page_num idset);" % fb_table
		}
	)

	# check status
	if fb_query.get('error'):
		if "exists" in fb_query.get('error'):
			print("FeatureBase database `%s` already exists." % fb_table)
		else:
			print(fb_query.get("explain"))
			print("FeatureBase returned an error. Check your credentials or create statement!")
			sys.exit()
	else:
		print("Created `%s` database on FeatureBase Cloud." % fb_table)

	# create FeatureBase database
	fb_table = "doc_questions"
	fb_query = featurebase_query(
		{
			"sql": "CREATE TABLE %s (_id string, filename string, title string, question string, keyterms stringset, page_num int, answer string, probability string);" % fb_table
		}
	)

	# check status
	if fb_query.get('error'):
		if "exists" in fb_query.get('error'):
			print("FeatureBase database `%s` already exists." % fb_table)
		else:
			print(fb_query.get("explain"))
			print("FeatureBase returned an error. Check your credentials or create statement!")
			sys.exit()
	else:
		print("Created `%s` database on FeatureBase Cloud." % fb_table)

	# create FeatureBase database
	fb_table = "doc_fragments"
	fb_query = featurebase_query(
		{
			"sql": "CREATE TABLE %s (_id string, filename string, title string, page_num int, fragment_num int, prev_id string, fragment string);" % fb_table
		}
	)

	# check status
	if fb_query.get('error'):
		if "exists" in fb_query.get('error'):
			print("FeatureBase database `%s` already exists." % fb_table)
		else:
			print(fb_query.get("explain"))
			print("FeatureBase returned an error. Check your credentials or create statement!")
			sys.exit()
	else:
		print("Created `%s` database on FeatureBase Cloud." % fb_table)

	# check status
	if fb_query.get('error'):
		if "exists" in fb_query.get('error'):
			print("FeatureBase database `%s` already exists." % fb_table)
		else:
			print(fb_query.get("explain"))
			print("FeatureBase returned an error. Check your credentials or create statement!")
			sys.exit()
	else:
		print("Created `%s` database on FeatureBase Cloud." % fb_table)


