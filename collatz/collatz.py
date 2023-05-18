import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import TSNE
import openai
import config

# Set up OpenAI API credentials
openai.api_key = config.openai_token

def gpt3_embedding(content, model='text-embedding-ada-002'):
    content = content.encode(encoding='ASCII', errors='ignore').decode()
    response = openai.Embedding.create(
        input=content,
        model=model
    )
    vector = response['data'][0]['embedding']  # this is a normal list
    return vector

# Sentences about cats, dogs, and rats
sentences = [
    "Cats are known for their independent nature.",
    "Cats are excellent hunters with sharp claws.",
    "I love the way cats purr when they are happy.",
    "Cats are agile and can climb trees easily.",
    "Cats have a strong sense of curiosity.",
    "Playing with a cat can be a lot of fun.",
    "Cats have a wide range of vocalizations.",
]

# Embed the sentences
embedded_vectors = []
for sentence in sentences:
    vector = gpt3_embedding(sentence)
    embedded_vectors.append(vector)

# Convert embedded vectors to NumPy array
embedded_vectors = np.array(embedded_vectors)

# Perform t-SNE for dimensionality reduction
tsne = TSNE(n_components=3, perplexity=6, random_state=42, init='random', learning_rate=200)
projected_vectors = tsne.fit_transform(embedded_vectors)

# Assign categories and ratings to each sentence
categories = ['Cat'] * 7
ratings = np.random.choice([1, 2, 3, 4, 5], size=len(sentences))

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Define color mappings for categories
category_colors = {'Cat': 'blue', 'Dog': 'green', 'Rat': 'red'}

# Plot the projected vectors with colorization based on categories
for i, category in enumerate(categories):
    indices = np.where(np.array(categories) == category)[0]
    ax.scatter(
        projected_vectors[indices, 0],
        projected_vectors[indices, 1],
        projected_vectors[indices, 2],
        c=category_colors[category],
        label=category,
        alpha=0.3
    )

# Set labels and title
ax.set_xlabel('Component 1')
ax.set_ylabel('Component 2')
ax.set_zlabel('Component 3')
plt.title('Projection of Sentences to 3D Space with Category Colorization')

# Add a colorbar legend for ratings
cbar = plt.colorbar(matplotlib.cm.ScalarMappable(norm=None, cmap=plt.cm.get_cmap('viridis')))
cbar.set_ticks([1, 2, 3, 4, 5])
cbar.set_label('Rating')

# Add a legend for categories
ax.legend()

# Show the plot
plt.show()
