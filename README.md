# DocGPT | Advanced LLM Prompting for PDFs | 📝💻🔍📚💡
DocGPT is a repository on Github that provides advanced LLM prompting for PDFs and webpages. The repository uses various tools such as PyPDF2 and pdf2image for PDF processing, Google Vision for text extraction from images, nltk for text fragment/chunk extraction, Weaviate for dense vector search and embedding handling, and FeatureBase for extracted back of the book indexing and graph traversal.

The project is installed, configured and run locally from the command line. You will need a Google Vision account, a FeatureBase cloud account and a Weaviate cloud account to run the code.

![Doc Brown](https://github.com/FeatureBaseDB/DocGPT/blob/main/doc.jpg)

## Theory of Operation
The process of indexing a document is divided into three main steps:

1. A PDF (and later webpages) are processed into images. These images are then used for text extraction with the help of Google Vision.
2. The extracted text is chunked by nltk and stored in Weaviate, which handles the ada-002 embeddings using OpenAI's APIs. During this indexing step, a back-of-the-book index is also created, and the keyterms are stored in an inverted index in FeatureBase along with the text chunk's UUIDs from Weaviate and the page numbers.
3. During interactions with the LLM, Weaviate and FeatureBase are used together to determine the most relevant text to use for building prompts. Texts are passed around as documents and augmented with queries to the LLM as well as use of any documents that are related through the inverted index in FeatureBase.

## Setup
To use Weaviate and FeatureBase with DocGPT, you will need to set up accounts with their respective cloud providers. Follow the instructions below to get started:

### Weaviate Cloud Setup
Go to the Weaviate Cloud website and sign up for an account.

Once you have signed up, you will be taken to the dashboard. Click on the "Create Weaviate Cluster" button to create a new cluster.

Follow the on-screen instructions to configure your cluster. You will need to choose a provider, region, and cluster size. You can also choose to enable backups and enable SSL.

Once your cluster is set up, you can access it from the dashboard.

### FeatureBase Cloud Setup
Go to the FeatureBase Cloud website and sign up for an account.

Once you have signed up, you will be taken to the dashboard. Click on the "Create FeatureBase Cluster" button to create a new cluster.

Follow the on-screen instructions to configure your cluster. You will need to choose a provider, region, and cluster size. You can also choose to enable backups and enable SSL.

Once your cluster is set up, you can access it from the dashboard.
