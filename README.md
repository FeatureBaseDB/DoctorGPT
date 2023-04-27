# DoktorGPT | Advanced LLM Prompting for PDFs | 💻📚💡
DoktorGPT implements LLM prompting for discussing PDFs. The repository uses various tools such as [PyPDF2](https://pypi.org/project/PyPDF2/) and [pdf2image](https://pypi.org/project/pdf2image/) for PDF processing, [Google Vision](https://cloud.google.com/vision) for text extraction from images, [nltk](https://www.nltk.org/) for text fragment/chunk extraction, [Weaviate](https://weaviate.io/) for dense vector search and embedding handling, and [FeatureBase](https://featurebase.com/) for extracted back of the book indexing and graph traversal.

The project is installed, configured and run locally from the command line. You will need a [Google Cloud](https://cloud.google.com/) account with [Vision enabled](https://cloud.google.com/vision/docs/before-you-begin), an [OpenAI account](https://openai.com), a [FeatureBase cloud](https://cloud.featurebase.com) account and a [Weaviate cloud](https://console.weaviate.cloud/) account to run the code.

![Doc Brown](https://github.com/FeatureBaseDB/DocGPT/blob/main/doc.jpg)

## Theory of Operation
The process of indexing a document is divided into three main steps:

1. A PDF (and later webpages) are processed into images. These images are then used for text extraction with the help of Google Vision. Early concepts of this idea have been previously implemented at [Mitta.us](https://mitta.us/).
2. The extracted text is chunked by nltk and stored in Weaviate, which handles the [ada-002 embeddings](https://platform.openai.com/docs/guides/embeddings) using OpenAI's APIs. During this indexing step, a [back-of-the-book index](https://en.wikipedia.org/wiki/Index_(publishing)) is also created, and the keyterms are stored in an inverted index in FeatureBase along with the text chunk's UUIDs from Weaviate and the page numbers.
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
