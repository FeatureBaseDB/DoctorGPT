# DocGPT | Document Organization for GPT | 💻📚💡
DocGPT implements advanced LLM prompting for organizing and discussing PDFs. The repository uses tools such as [PyPDF2](https://pypi.org/project/PyPDF2/) and [pdf2image](https://pypi.org/project/pdf2image/) for PDF processing, [Google Vision](https://cloud.google.com/vision) for text extraction from images, [nltk](https://www.nltk.org/) for text fragment/chunk extraction, [Weaviate](https://weaviate.io/) for dense vector search and embedding handling, and [FeatureBase](https://featurebase.com/) for back of the book indexing and graph traversal of questions.

The project is installed, configured and run locally from the command line. You will need a [Google Cloud](https://cloud.google.com/) account with [Vision enabled](https://cloud.google.com/vision/docs/before-you-begin), an [OpenAI account](https://openai.com), a [FeatureBase cloud](https://cloud.featurebase.com) account and a [Weaviate cloud](https://console.weaviate.cloud/) account to run the code.

![Doc Brown](https://github.com/FeatureBaseDB/DocGPT/blob/main/doc.jpg)

## Theory of Operation
The process of indexing a document is divided into three main steps:

1. A PDF is processed into images. These images are then used for text extraction with the help of Google Vision. Early concepts of this idea have been previously implemented at [Mitta.us](https://mitta.us/).
2. The extracted text is chunked by nltk and stored in Weaviate, which handles the [ada-002 embeddings](https://platform.openai.com/docs/guides/embeddings) using OpenAI's APIs. During this indexing step, a [back-of-the-book index](https://en.wikipedia.org/wiki/Index_(publishing)) is also created, and the keyterms are stored in an inverted index in FeatureBase along with the text chunk's UUIDs from Weaviate and the page numbers.
3. During interactions with the LLM, Weaviate and FeatureBase are used together to determine the most relevant text to use for building prompts. Texts are passed around as documents and augmented with queries to the LLM as well as use of any documents that are related through the inverted index in FeatureBase.

## Create a Config File
Copy the `config.py.example` file to `config.py`. Use this file to store the various strings and tokens for the services utilized by this project.

## Cloud Setup
To use Weaviate and FeatureBase with DocGPT, you will need to signup for their free cloud offerings. Follow the instructions below to get started.

### Weaviate Cloud
Go to [Weaviate Cloud](https://console.weaviate.cloud/dashboard) and sign up for an account.

After signup, naviate to the dashboard. Click on the "Create Cluster" button to create a new cluster. Name the cluster and ensure authentication is enabled.

After the cluster is created, click on "Details" and click on the cluster URL to copy the cluster address. Paste this address into the value for the `weaviate_cluster` variable in the config file.

Next, click on the key next to "Enabled Authentication" to copy the Weaviate token. Paste this into the config file for the `weaviate_token` variable.

Your Weaviate Cloud config will be complete. This sandbox cluster will expire in 14 days.

### FeatureBase Cloud
Go to [FeatureBase Cloud](https://cloud.featurebase.com/) and sign up for an account.

Once you have signed up, you will be taken to the dashboard. Click on "Databases" to the left. Click on "NEW DATABASE". Select the 8GB database option and create the database, naming it `doc_gpt`

On the Databases page, click on your new database. Copy the `Query endpoint` by clicking on the URL. Paste the URL into the `config.py` file mentioned above and DELETE the `/query/sql` path on the end, leaving a URL without a `/` on the end.

Your FeatureBase Cloud config will be complete. You have $300 of credits to use on this free trial.

### Google Compute
Go to [Google Cloud](https://console.cloud.google.com/) and signup for a cloud account. If you don't have a Google Cloud account, you will get a free credit for trying out the service.

This project uses the Vision APIs to extract text from images, which are created from the PDF. Not all PDFs have embedded text in them, so this step ensures you can index any PDF.

Create a project for your Google cloud account, if you don't have one already.

Navigate to the [Google Vision API product overview](https://console.cloud.google.com/apis/library/vision.googleapis.com). Click "Enable" to enable this API for your account.

Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) on your computer. Follow the instructions for your particular OS.

Once the SDK is installed, open a terminal (Powershell will work for Windows) and enter the following:

`gcloud auth application-default login`

A `.json` authentication file will be downloaded, which will be used to authenticate the project to your Google Cloud Vision API endpoints.

### Checkout the Code
To check out the code from Github, run the following command from a terminal window (we recommend using [GitBash](https://git-scm.com/downloads) on Windows to do this step):

`git clone https://github.com/FeatureBaseDB/DocGPT.git`

Change into the directory to prepare for installing the packages required to run the project:

`cd ~/<path_to_code>/DocGPT`

On Windows, you'll want to do this step in Powershell.

