import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.manifold import TSNE
import openai
import config
import sys
from sklearn.preprocessing import MinMaxScaler


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
    "Cats have soft and fluffy fur.",
    "Cats are clean animals and spend a lot of time grooming themselves.",
    "Cats are often considered mysterious and enigmatic creatures.",
    "Cats have a keen sense of balance and are skilled at jumping and landing.",
    "Cats can see in almost total darkness due to their highly sensitive eyes.",
    "Cats are crepuscular animals, meaning they are most active during dawn and dusk.",
    "Cats have a unique behavior of kneading with their paws, often seen as a sign of contentment.",
    "Cats have a specialized collarbone that allows them to always land on their feet when falling.",
    "Cats communicate through various vocalizations, including meowing, purring, and hissing.",
    "Cats have a remarkable ability to squeeze through small spaces due to their flexible bodies.",
    "Cats have been domesticated for thousands of years and have played significant roles in many cultures.",
    "Cats have a well-developed sense of hearing and can detect high-frequency sounds that are inaudible to humans.",
    "Cats have a strong sense of territory and use scent marking to communicate and establish their boundaries.",
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

scaler = MinMaxScaler(feature_range=(0, 1))
projected_vectors = scaler.fit_transform(projected_vectors)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the projected vectors
ax.scatter(
    projected_vectors[:, 0],
    projected_vectors[:, 1],
    projected_vectors[:, 2],
    c='blue',
    alpha=0.3
)

# Set labels and title
ax.set_xlabel('Component 1')
ax.set_ylabel('Component 2')
ax.set_zlabel('Component 3')
plt.title('Projection of Sentences to 3D Space')

# Show the plot
plt.show()
