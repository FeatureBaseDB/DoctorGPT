# DocGPT | Document Organization for GPT | 💻📚💡
DocGPT implements advanced LLM prompting for organizing and discussing PDFs, and does so without using any type of prompt processing frameworks, like Langchain. The project aims to provide a referencable solution for building intelligent prompting systems from scratch.

The repository uses tools such as [PyPDF2](https://pypi.org/project/PyPDF2/) and [pdf2image](https://pypi.org/project/pdf2image/) for PDF processing, [Google Vision](https://cloud.google.com/vision) for text extraction from images, [nltk](https://www.nltk.org/) for text fragment/chunk extraction, [Weaviate](https://weaviate.io/) for dense vector search and embedding handling, and [FeatureBase](https://featurebase.com/) for back of the book indexing and graph traversal of terms and questions.

The project is installed, configured and run locally from the command line. You will need a [Google Cloud](https://cloud.google.com/) account with [Vision enabled](https://cloud.google.com/vision/docs/before-you-begin), an [OpenAI account](https://openai.com), a [FeatureBase cloud](https://cloud.featurebase.com) account and a [Weaviate cloud](https://console.weaviate.cloud/) account to run the code.

![Doc Brown](https://github.com/FeatureBaseDB/DocGPT/blob/main/doc.jpg)

## Theory of Operation
The process of indexing a document is divided into three main steps:

1. A PDF is processed into images. These images are then used for text extraction with the help of Google Vision. Early concepts of this idea have been previously implemented at [Mitta.us](https://mitta.us/).
2. The extracted text is chunked by nltk and stored in Weaviate, which handles the [ada-002 embeddings](https://platform.openai.com/docs/guides/embeddings) using OpenAI's APIs. During this indexing step, a [back-of-the-book index](https://en.wikipedia.org/wiki/Index_(publishing)) is also created, and the keyterms are stored in an inverted index in FeatureBase along with the text chunk's UUIDs from Weaviate and the page numbers.
3. During interactions with the LLM, Weaviate and FeatureBase are used together to determine the most relevant text to use for building prompts. Texts are passed around as documents and augmented with queries to the LLM as well as use of any documents that are related through the inverted index in FeatureBase.

## Checkout the Code
To check out the code from Github, run the following command from a terminal window (we recommend using [GitBash](https://git-scm.com/downloads) on Windows to do this step):

`git clone https://github.com/FeatureBaseDB/DocGPT.git`

Change into the directory to prepare for installing the packages required to run the project:

`cd ~/<path_to_code>/DocGPT`

On Windows, you'll want to do this last part in Powershell.
### Create a Config File
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

Your FeatureBase Cloud config will be completed below when you grab a token. You have $300 of credits to use on this free trial.

### Google Compute
Go to [Google Cloud](https://console.cloud.google.com/) and signup for a cloud account. If you don't have a Google Cloud account, you will get a free credit for trying out the service.

This project uses the Vision APIs to extract text from images, which are created from the PDF. Not all PDFs have embedded text in them, so this step ensures you can index any PDF.

Create a project for your Google cloud account, if you don't have one already.

Navigate to the [Google Vision API product overview](https://console.cloud.google.com/apis/library/vision.googleapis.com). Click "Enable" to enable this API for your account.

Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) on your computer. Follow the instructions for your particular OS.

Once the SDK is installed, open a terminal (Powershell will work for Windows) and enter the following:

`gcloud auth application-default login`

A `.json` authentication file will be downloaded, which will be used automatically to authenticate the project to your Google Cloud Vision API endpoints. No configuration is needed beyond this step.

## Continued Setup
You'll need to grab an auth token for GPT-X from OpenAI, the token for FeatureBase, and install the required packages for Python to run the code.

### OpenAI Auth
Go to [OpenAI](https://openai.com/) and signup or login. Navigate to the [getting started page](https://platform.openai.com/) and click on your user profile at the top right. 

Select "view API keys" and then create a new API key. Copy this key and put it in the `config.py` file under the `openai_token` variable.

### Install Requirements
There are many packages used for this project that are required for execution. You may inspect the packages by looking at the `requirements.txt` file in the root directory of the project.

To install the required packages, ensure you have Python 3.10.11 or greater installed. It may be possible to use a lower version of Python, but this package has only been tested on Python 3.10.x, so your mileage may vary. It is left up to the user to determine the best way to update Python, but you may want to ask [ChatGTP](https://chat.openai.com) about it.

Run the following to install the required packages, use the `pip` package for Python:

`pip install -r requirements.txt`

If you are installing on Windows, you will like need to install the `python-poppler` package manually. To do this, follow the instructions below.

#### Installing Poppler with MSYS2
##### Install MSYS2

1. Download the MSYS2 installer from the [MSYS2 website](https://www.msys2.org/).
1. Run the installer and follow the installation instructions.

##### Update MSYS2

1. Open the MSYS2 terminal (the "MSYS2 MinGW 64-bit" shortcut).
2. Execute the following command to update the package database and core packages:
```
pacman -Syu
```
 
##### Install Poppler
1. In the MSYS2 terminal, run the following command to install Poppler:
```
pacman -S mingw-w64-x86_64-poppler
```
2. Open a regular command prompt or terminal (use Powershell).
3. Run the following command to add the Poppler binaries to your system's PATH:
```
set PATH=C:\msys64\mingw64\bin;%PATH%
```
Replace `C:\msys64` with the installation path of MSYS2 if it differs.

##### Verify the Installation

Open a new command prompt or terminal and run the following command to check if Poppler is installed:
```
pdftotext --version
```

If the command displays the Poppler version information, the installation was successful.

### FeatureBase Token
Keeping in mind your username/password you used for FeatureBase, open a terminal and 
