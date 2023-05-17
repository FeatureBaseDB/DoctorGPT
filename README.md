# DocGPT | Document Organization for GPT | 💻📚💡
DocGPT implements advanced LLM prompting for organizing and discussing PDFs. The repository uses tools such as [PyPDF2](https://pypi.org/project/PyPDF2/) and [pdf2image](https://pypi.org/project/pdf2image/) for PDF processing, [Google Vision](https://cloud.google.com/vision) for text extraction from images, [nltk](https://www.nltk.org/) for text fragment/chunk extraction, [Weaviate](https://weaviate.io/) for dense vector search and embedding handling, and [FeatureBase](https://featurebase.com/) for back of the book indexing and graph traversal of questions.

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

"""
system> How can Tile Encoder help in monitoring data when the distribution of the data changes?
bot> With the Tile encoder it is possible to quickly update the Product Quantization data when the data distribution changes, as the whole process is very cheap in terms of time.
bot> None None
bot>
system> What tools can be used to get started with Weaviate?
bot> Check out Getting Started with Weaviate, and begin building amazing apps with Weaviate. You can reach out to us on Slack or Twitter. Weaviate is open source, and you can follow the project on GitHub. Don't forget to give us a while you are there!
bot> None None
bot>
system> What data is needed to trigger the compress action for the Tile encoder?
bot> The distribution of your data is needed to trigger the compress action for the Tile encoder.
bot> None None
bot>
system> What are the pros and cons of using more memory for indexing at the moment?
bot> The pros of using more memory for indexing at the moment is that it can lead to faster indexing time and less memory for querying the server. The cons is that more memory is needed for the moment of indexing since all vectors need to be uncompressed and compressed at the same time.
bot> None None
bot>
system> How does knowing the data distribution in advance help with KMeans clustering?
bot> If we know the distribution of the data in advance, we might be able to produce the centroids without fitting the data with KMeans. All we need to do is to produce a tiling over the full range of values following the distribution of the data. Instead of using KMeans, we could generate the codes using the Cumulative Density Function (CDF) of the distribution of the data. The CDF produces values from zero to one. We want 256 codes but in general we might want to use any amount of codes (so we could use more, or less bits to encode). The code then could be calculated as code(x) = CDF(x) * c where c is the amount of codes to use.
bot> None None
bot>
system> How do centroids fit better the distribution of the data?
bot> Centroids fit better the distribution of the data as opposed to using independent segments for each dimension when using enough centroids.
bot> None None
bot>
system> How are the codes calculated using the Cumulative Density Function (CDF) of the data?
bot> The code is calculated as code(x) = CDF(x) * c where c is the amount of codes to use. The CDF produces values from zero to one.
bot> None None
bot>
system> How could the Tile encoder effectively monitor a situation with drifting data?
bot> The Tile encoder could effectively monitor a situation with drifting data by calculating the mean and standard deviation of the data incrementally and updating the product Quantization data over time since the process is very cheap in terms of time.
bot> None None
bot>
system> What is the code calculated as when using Cumulative Density Function to generate codes?
bot> The code is calculated as code(x) = CDF(x) * c where c is the amount of codes to use.
bot> None None
bot>
system> What does Figure 3 depict?
bot> Figure 3 depicts centroids generated by KMeans on the first segment including the first two dimensions. The encoder was fitted using 32 (above) and 256 (below) centroids, which fit better the distribution of the data as opposed to using independent segments for each dimension when using enough centroids.
bot> None None
bot>
system> How did the addition of 200,000 vectors using the normal HNSW algorithm and the remaining 800,000 vectors using compressed improve the experiment?
bot> The addition of 200,000 vectors using the normal HNSW algorithm and the remaining 800,000 vectors using compressed improved the experiment by reducing the latency and indexing time, resulting in higher recall scores.
bot> None None
bot>
system> What is the purpose of editing a research page?
bot> The purpose of editing a research page is to make sure the page is up to date with the latest research and to ensure accuracy and clarity of information.
bot> None None
bot>
system> What is the real advantage of using the Quantile function when we need to decompress data?
bot> The real advantage of using the Quantile function when we need to decompress data is that we no longer need to spend a long time to fit our data. We can calculate the mean and standard deviation (only parameters of the distribution) incrementally as the data is added and that is it. This also opens a good opportunity for easily updating the Product Quantization data over time since the whole process is very cheap in terms of time.
bot> None None
bot>
system> What is the cause for the difference in recall between the Tile and KMeans encoder?
bot> The cause for this difference has not yet been identified at the moment of writing this post. One significant difference is the vector size. It could be that independent errors for off distribution points on single dimensions are less significant on larger vectors since they will be absorbed by the rest of the dimensions.
bot> None None
bot>
system> What are the drawbacks of KMeans when compressing vectors?
bot> The drawbacks of KMeans when compressing vectors are that it is expensive to fit to data and when compressing vectors it needs to calculate distances to all centroids for each segment, resulting in long encoding and indexing times.
bot> None None
bot>
system> What are the differences in indexing times when compressing data with KMeans, Tile and HNSW?
bot> When compressing data with KMeans, the indexing time is longer compared to regular HNSW. However, when compressing data with Tile, indexing time remains unchanged compared to regular HNSW.
bot> None None
bot>
system> What performance results were observed with HNSW+PQ on the three databases?
bot> The performance results observed with HNSW+PQ on the three databases were a Recall (vertical axis) Vs Latency (in microseconds, on the horizontal axis) chart for Fig. 8, and a Recall (vertical axis) Vs Indexing time (in minutes, on the horizontal axis) chart for Fig. 9.
bot> None None
bot>
system> What is the consequence of the dimensions following a LogNormal distribution?
bot> The centroids clearly follow a LogNormal distribution. This is a consequence of the dimension values following the same distribution.
bot> None None
bot>
system> What is the advantage of using the Quantile function for calculating the mean and standard deviation when we need to decompress the data?
bot> The real advantage of this approach is that we no longer need to spend a long time to fit our data. We could calculate the mean and standard deviation (only parameters of the distribution) incrementally as the data is added and that is it. This also opens a good opportunity for easily updating the Product Quantization data over time since the whole process is very cheap in terms of time.
bot> None None
bot>
system> How does KMeans achieve a balanced distribution of data over the centroids?
bot> KMeans generates a tiling over the full range of values using the centroids. When fitting KMeans to the data, tiles are generated in a homogenous way, meaning that more tiles are created where there is a higher density of data. This allows data to be more evenly balanced over the centroids.
bot> None None
bot>
system> What is the algorithm used to determine which tile a new vector belongs to in the Tile Encoder?
bot> The algorithm used to determine which tile a new vector belongs to in the Tile Encoder is to check its closest found tile.
bot> None None
bot>
system> What is the difference in Recall vs Latency and Indexing vs Latency for HNSW-PQTile experiment?
bot> The Recall vs Latency shows that with HNSW-PQTile, the recall increases as the latency decreases. The Indexing vs Latency shows that with HNSW-PQTile, the indexing time increases as the latency increases.
bot> None None
bot>
system> What are the differences between the KMeans and Tile encoders when creating centroids?
bot> The KMeans and Tile encoders generate similar results, with centroids that are dense at the origin of both axes and much more sparse as the values grow. The Tile encoder is able to monitor the situation and update the data more quickly if needed due to the data drifting from new trends.
bot> None None
bot>
system> What is the difference between KMeans and Tile encoders?
bot> KMeans and Tile encoders generate similar results when fitted using the same number of centroids. However, KMeans can fit the data better than Tile if enough centroids are used. Additionally, KMeans can be applied in a multivariate approach while Tile can only be applied in a cartesian product of individual segments.
bot> None None
bot>
system> What are the results of the comparison between KMeans and the Tile encoder?
bot> The results of the comparison between KMeans and the Tile encoder are that the recall results are very similar when using KMeans vs Tile encoder and fitting with Tile is immediate while it takes much longer with KMeans. Additionally, no downtime is needed when compressing with the Tile encoder, while your server will not be available for querying while compressing with the KMeans encoder.
bot> None None
bot>
system> What affects the querying time when indexing?
bot> The segmentation of data, compress action, and amount of data used in the indexing process.
bot> None None
bot>
system> What is the advantage of using the Tile encoder versus the KMeans encoder?
bot> The Tile encoder does not need to be fit to the data, so it does not take as long to encode the data. Additionally, no downtime is needed when compressing with the Tile encoder, while the server is not available for querying when compressing with the KMeans encoder.
bot> None None
bot>
system> What distributions does the encoder currently support?
bot> The encoder currently supports normal and lognormal distributions.
bot> None None
bot>
"""
