from lib.util import drop_databases;
drop_databases()

from lib.database import weaviate_delete_schema
weaviate_delete_schema("PDFs")
weaviate_delete_schema("QandAs")
