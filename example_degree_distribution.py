import matplotlib.pyplot as plt

t = [1, 2, 3, 2, 3, 1]
n, bins, patches = plt.hist(t, bins=[1, 2, 3, 4], facecolor='blue', rwidth=0.5, align="left")
plt.xlabel(r"Degree")
plt.ylabel(r"Number of Vertices")

plt.savefig('./data/example_degree_distribution.jpg')