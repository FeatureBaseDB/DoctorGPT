import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.decomposition import PCA

# Number of vectors to create
num_vectors = 600

# Dimensionality of the vectors
dim = 5

# Create random 5-dimensional vectors
vectors = np.random.rand(num_vectors, dim)

# Perform PCA for dimensionality reduction
pca = PCA(n_components=3)
projected_vectors = pca.fit_transform(vectors)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the projected vectors
ax.scatter(projected_vectors[:, 0], projected_vectors[:, 1], projected_vectors[:, 2], c='blue', marker='o')

# Set labels and title
ax.set_xlabel('Component 1')
ax.set_ylabel('Component 2')
ax.set_zlabel('Component 3')
plt.title('Projection of Vectors to 3D Space')

# Show the plot
plt.show()
