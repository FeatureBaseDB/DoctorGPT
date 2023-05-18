import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def collatz_sequence(n):
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence

def plot_collatz_formation(sequence):
    x = list(range(len(sequence)))
    y = sequence
    z = [i % 2 for i in sequence]  # Represent odd/even nature as an additional dimension

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='blue', marker='o')

    ax.set_xlabel('Step')
    ax.set_ylabel('Value')
    ax.set_zlabel('Odd/Even Dimension')

    plt.title('Collatz-Like Formation')
    plt.show()

# Example usage:
starting_number = 10000
collatz_seq = collatz_sequence(starting_number)
plot_collatz_formation(collatz_seq)
