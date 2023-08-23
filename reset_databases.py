from lib.database import drop_database
for name in ["doc_pages", "doc_keyterms", "doc_questions", "doc_fragments"]:
	drop_database(name)