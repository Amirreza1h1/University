import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import skfuzzy as fuzz

# Step 1: Generate synthetic data for clustering with more variance (causing overlaps)
np.random.seed(42)
data_1 = np.random.randn(150, 2) * 2 + [0, 0]   # Cluster 1
data_2 = np.random.randn(150, 2) * 2 + [8, 8]  # Cluster 2
data_3 = np.random.randn(150, 2) * 2 + [16, 0]  # Cluster 3
data_4 = np.random.randn(150, 2) * 2 + [4, 4]  # Cluster 4
data_5 = np.random.randn(150, 2) * 2 + [12, 8]  # Cluster 5

data = np.vstack((data_1, data_2, data_3, data_4, data_5))

# Step 2: Function to find the optimal number of clusters using silhouette score (for K-Means)


def find_optimal_clusters_kmeans(data, max_clusters):
    silhouette_scores = []
    for n in range(2, max_clusters+1):
        kmeans = KMeans(n_clusters=n, random_state=42, n_init=10)
        kmeans_labels = kmeans.fit_predict(data)
        score = silhouette_score(data, kmeans_labels)
        silhouette_scores.append((n, score))
    return silhouette_scores

# Function to find the optimal number of clusters for FCM using FPC (Fuzzy Partition Coefficient)


def find_optimal_clusters_fcm(data, max_clusters):
    fpcs = []
    for n in range(2, max_clusters + 1):
        cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
            data.T, c=n, m=2, error=0.005, maxiter=1000)
        # Return only two columns from u
        u = u[:, :n]
        fpcs.append((n, fpc))
    return fpcs


# Step 3: Determine optimal clusters using K-Means and FCM
max_clusters = 6
optimal_kmeans = find_optimal_clusters_kmeans(data, max_clusters)
optimal_fcm = find_optimal_clusters_fcm(data, max_clusters)

# Find the best number of clusters (highest silhouette score for KMeans and FPC for FCM)
best_kmeans_clusters = max(optimal_kmeans, key=lambda x: x[1])[0]
best_fcm_clusters = max(optimal_fcm, key=lambda x: x[1])[0]

print(f"Best number of clusters (KMeans): {best_kmeans_clusters}")
print(f"Best number of clusters (FCM): {best_fcm_clusters}")

# Step 4: Apply C-Means (K-Means) with the best number of clusters
kmeans = KMeans(n_clusters=best_kmeans_clusters, random_state=42, n_init=10)
kmeans_labels = kmeans.fit_predict(data)

# Step 5: Apply Fuzzy C-Means (FCM) with the best number of clusters
cntr, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(
    data.T, c=best_fcm_clusters, m=2, error=0.005, maxiter=1000)

fcm_labels = np.argmax(u, axis=0)

# Step 5: Visualize FCM membership probabilities


def plot_fcm_membership(ax, data, u, cluster_index):
    colors = u[cluster_index, :]
    scatter = ax.scatter(data[:, 0], data[:, 1], c=colors,
                         cmap='coolwarm', edgecolor='k', marker='o')
    plt.colorbar(scatter, ax=ax)

# Step 6: Define a function to plot circular boundaries for the clusters


def plot_cluster_circles(ax, centers, color='r', linewidth=2):
    for center in centers:
        circle = plt.Circle(center, color=color,
                            fill=False, linewidth=linewidth)
        ax.add_artist(circle)

# Step 7: Plot the results


fig, axes = plt.subplots(2, 2, figsize=(14, 14))

# Plot C-Means (K-Means) results
axes[1, 1].scatter(data[:, 0], data[:, 1], c=kmeans_labels,
                   cmap='viridis', marker='o', edgecolor='k')
axes[1, 1].set_title('C-Means (K-Means) Clustering')
plot_cluster_circles(
    axes[1, 1], kmeans.cluster_centers_, color='blue')

# Plot FCM membership for each cluster
for i in range(best_fcm_clusters):
    axes[i//2, i % 2].set_title(f'Fuzzy C-Means - Cluster {i} Membership')
    plot_fcm_membership(axes[i//2, i % 2], data, u, i)

plt.tight_layout()
plt.show()
