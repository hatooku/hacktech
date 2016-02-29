import numpy as np
from sklearn.cluster import KMeans as KM

""" Takes in filtered data and identifies 8 cluster centers.
"""
def findClusterCenters(data):
    # prepare data
    nonzero_xy = np.nonzero(data)
    if len(nonzero_xy) != 2:
        return
    if nonzero_xy[0].size < 8:
        return
        
    processed_data = np.vstack((nonzero_xy[0], nonzero_xy[1])).transpose()
    
    # K-Means algorithm
    kmeans = KM(n_clusters = 8, max_iter=20, n_init = 5)
    kmeans.fit(processed_data)
    center_points = np.fliplr(kmeans.cluster_centers_)
    return center_points



# Plot heatmap to compare
#plt.imshow(data)
#plt.show()
