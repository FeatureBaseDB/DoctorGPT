# DoctorGPT | Document Organization & Chat | 💻📚💡
DoctorGPT implements advanced LLM prompting for organizing, indexing and discussing PDFs, and does so without using any type of opinionated prompt processing frameworks, like [Langchain](https://github.com/hwchase17/langchain). The project aims to provide a reference solution for scratch building intelligent prompting systems which use documents for source truth.

For those of you that expected this to act as a medical doctor, we can't recommend that but it would be possible if you fed it relevant medical documents. Keep in mind that there are also doctors of physics, philosophy and math, the later two of which may or may not have crazy hair.

```
Entering conversation with DoctorGPT.pdf. Use ctrl-C to end interaction.
user-P61W[DoctorGPT.pdf]> Briefly introduce yourself, DoctorGPT. It's OK if you pretend to be Doc Brown from Back to the Future.
bot> Querying GPT...
bot> My name is DoctorGPT and I'm an AI agent designed to help you organize and manage PDF documents. Just like Doc Brown, I'm here to help you navigate the future of PDFs.
```

The repository uses tools such as [PyPDF2](https://pypi.org/project/PyPDF2/) and [pdf2image](https://pypi.org/project/pdf2image/) for PDF processing, [Google Vision](https://cloud.google.com/vision) for text extraction from images, [nltk](https://www.nltk.org/) for text fragment/chunk extraction, [Weaviate](https://weaviate.io/) for dense vector search and embedding handling, and [FeatureBase](https://featurebase.com/) for back of the book indexing and graph traversal of terms, questions and document fragments.

The project is installed, configured and run locally from the command line. You will need a [Google Cloud](https://cloud.google.com/) account with [Vision enabled](https://cloud.google.com/vision/docs/before-you-begin), an [OpenAI account](https://openai.com), a [FeatureBase cloud](https://cloud.featurebase.com) account and a [Weaviate cloud](https://console.weaviate.cloud/) account to run the code.

![Doc Brown](https://github.com/FeatureBaseDB/DoctorGPT/blob/main/doc.jpg)

## Theory of Operation
The process of indexing a document is divided into three main steps:

1. A PDF is processed into images. These images are then used for text extraction with the help of Google Vision. Early concepts of this idea have been previously implemented at [Mitta.us](https://mitta.us/).
2. The extracted text is chunked by nltk and stored in Weaviate, which handles the [ada-002 embeddings](https://platform.openai.com/docs/guides/embeddings) using OpenAI's APIs. During this indexing step, a [back-of-the-book index](https://en.wikipedia.org/wiki/Index_(publishing)) is also created, and the keyterms are stored in an inverted index in FeatureBase along with the text chunk's UUIDs from Weaviate and the page numbers.
3. During interactions with the LLM, Weaviate and FeatureBase are used together to determine the most relevant text to use for building prompts. Texts are passed around as documents and augmented with queries to the LLM as well as use of any documents that are related through the inverted index in FeatureBase.

## Install Instructions
These instructions are long, so ensure you follow them carefully. It is suggested you use [ChatGPT](https://chat.openai.com/) to assist you with any errors. Simply paste in the entire content of this README into ChatGPT before asking your question about the install process.

### Checkout the Code
To check out the code from Github, run the following command from a terminal window (we recommend using [GitBash](https://git-scm.com/downloads) on Windows to do this step):

`git clone https://github.com/FeatureBaseDB/DoctorGPT.git`

Change into the directory to prepare for installing the packages required to run the project:

`cd ~/<path_to_code>/DoctorGPT`

On Windows, you'll want to do this last part in Powershell.
### Create a Config File
Copy the `config.py.example` file to `config.py`. Use this file to store the various strings and tokens for the services utilized by this project.

### Cloud Setup
To use Weaviate and FeatureBase with DoctorGPT, you will need to signup for their free cloud offerings. Follow the instructions below to get started.

#### Weaviate Cloud
Go to [Weaviate Cloud](https://console.weaviate.cloud/dashboard) and sign up for an account.

After signup, navigate to the dashboard. Click on the "Create Cluster" button to create a new cluster. Name the cluster and ensure authentication is enabled.

After the cluster is created, click on "Details" and click on the cluster URL to copy the cluster address. Paste this address into the value for the `weaviate_cluster` variable in the config file.

Next, click on the key next to "Enabled Authentication" to copy the Weaviate token. Paste this into the config file for the `weaviate_token` variable.

Your Weaviate Cloud config will be complete. This sandbox cluster will expire in 14 days.

#### FeatureBase Cloud
Go to [FeatureBase Cloud](https://cloud.featurebase.com/) and sign up for an account.

Once you have signed up, you will be taken to the dashboard. Click on "Databases" to the left. Click on "NEW DATABASE". Select the 8GB database option and create the database, naming it `doc_gpt`

On the Databases page, click on your new database. Copy the `Query endpoint` by clicking on the URL. Paste the URL into the `config.py` file mentioned above and DELETE the `/query/sql` path on the end, leaving a URL without a `/` on the end.

##### FeatureBase Token
Keeping in mind your username/password you used for FeatureBase, open a terminal and navigate into the repository's directory.

Run the following to obtain a token for FeatureBase:

`python fb_token.py`

You'll receive output that includes the FeatureBase token. Place this token in the `config.py` file under the `featurebase_token` variable.

*NOTE*: You may need to use `python3` instead of `python` on some Python installs.

#### Google Compute
Go to [Google Cloud](https://console.cloud.google.com/) and signup for a cloud account. If you don't have a Google Cloud account, you will get a free credit for trying out the service.

This project uses the Vision APIs to extract text from images, which are created from the PDF. Not all PDFs have embedded text in them, so this step ensures you can index any PDF.

Create a project for your Google cloud account, if you don't have one already.

Navigate to the [Google Vision API product overview](https://console.cloud.google.com/apis/library/vision.googleapis.com). Click "Enable" to enable this API for your account.

Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) on your computer. Follow the instructions for your particular OS.

Once the SDK is installed, open a terminal (Powershell will work for Windows) and enter the following:

`gcloud auth application-default login`

A `.json` authentication file will be downloaded, which will be used automatically to authenticate the project to your Google Cloud Vision API endpoints. No configuration is needed beyond this step.

## Continue Setup
You'll need to grab an auth token for GPT-X from OpenAI, and install the required packages for Python to run the code.

### OpenAI Auth
Go to [OpenAI](https://openai.com/) and signup or login. Navigate to the [getting started page](https://platform.openai.com/) and click on your user profile at the top right. 

Select "view API keys" and then create a new API key. Copy this key and put it in the `config.py` file under the `openai_token` variable.

### Install Requirements
There are many packages used for this project that are required for execution. You may inspect the packages by looking at the `requirements.txt` file in the root directory of the project.

To install the required packages, ensure you have Python 3.10.11 or greater installed. It may be possible to use a lower version of Python, but this package has only been tested on Python 3.10.x, so your mileage may vary. It is left up to the user to determine the best way to update Python, but you may want to ask [ChatGTP](https://chat.openai.com) about it.

Run the following to install the required packages, use the `pip` package for Python:

`pip install -r requirements.txt`

If you are installing on Windows, you will like need to install the `python-poppler` package manually. To do this, follow the instructions below.

#### Installing Poppler with MSYS2 (only required if using Windows)
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

## Running the Project
There is already one document in the `documents` directory. If you want to index another document, place the PDF in this directory before starting indexing.

Before running any of these steps on Windows, you will need to run something like the following in a Powershell window (replace the front part of the path to your poppler install path):

```
$env:Path = "C:\Users\kord\Desktop\poppler-23.05.0\Library\bin;" + $env:Path
```

There are three (3) steps involved in getting a document to the point it can be interacted with.

### Fragmenting and Indexing
To image, extract text, fragment and embed the document for searching, run the following:

```
python index_pdf.py
```

*NOTE*: You may need to use `python3` instead of `python` on some Python installs.

After the script installs the NLTK package `punkt`, and checks the databases are created, you will receive a menu that looks like this:

```
Documents Directory
===================
0. animate.pdf
Enter the number of the file to index: 0
```

Hit enter to start indexing the document. Once the document is done indexing, the script will exit.

### Extraction of Keyterms and Questions
The next step is to index the fragments for keyterms and questions, which are stored in the FeatureBase tables.

Run the following to begin extraction for the document:

```
python index_tandqs.py
```

You'll receive a similar menu to the one above. Again, select the document number you want to do extraction on and hit enter.

Extraction will iterate through pages at random, generating keyterms and questions as it goes.

### Answer the Questions Posed by the AI
The final step for preparing the document store is answering the questions posed by the AI during extraction.

Run the following:

```
python doc_questions.py
```

Again, you will be presented with a menu of the PDFs available for answering questions. The script will iterate through the questions and if the script exits for any reason, it can be rerun to answer any questions that weren't answered during the previous pass.

```
Documents Directory
===================
0. animate.pdf
Enter the number of the file to process: 0
system> How does a pseudo-living organism perceive its surroundings in a world where the second law of thermodynamics is regularly reversed?
bot> A pseudo-living organism perceives its surroundings as reversed in time, forming a sort of a time-mirror, which would produce the illusion of reversal, with the result that such a perception would show the organism itself as alive (not as a pseudo-living organism) and the surrounding world, which is really alive, as lifeless and as following the second law of thermodynamics.
bot>
```

### Interact with the Document
This is the step we've all been waiting for. In this step, you will interact directly with the document in a chat. Please note, for this particular release, the system does not recall previous questions. This will be addressed in an updated version soon.

To interact with your PDF, type the following:

```
python doc_chat.py
```

Once again, you will get a menu of the document you want to chat with. Here is an example output using the provided document `The Animate and the Inanimate` by William James Sidis, likely the smartest human to have ever walked the planet:

```
Documents Directory
===================
0. animate.pdf
Enter the number of the file to chat with: 0
Entering conversation with animate.pdf. Use ctrl-C to end interaction.
user-9l1s[animate.pdf]> What is the relation between imaginary quantities and the square root of -1?
bot> The quantity i is defined as the square root of -1, and any quantity except zero has two square roots, each the negative of the other, so it is with -1; and we thus get two quantities, i and -i. They are absolutely interchangeable.
```

Please open tickets for any issues you encounter and consider contributing to this repository with pull requests. It is only through open collaboration that the "existential threat" of Strong AI is mitigated.
