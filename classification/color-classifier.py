'''
Script for finding the color of an image.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
from sklearn.cluster import KMeans

img = cv.imread('top_data/top_318.jpg')

# convert to RGB
img = cv.cvtColor(img, cv.COLOR_BGR2RGB)

# flatten to a single list of vectors
img = img.reshape((img.shape[1]*img.shape[0],3))

kmeans = KMeans(n_clusters=5)
s = kmeans.fit(img)

# get the labels of each of the color vectors (which cluster they are assigned to)
labels = list(kmeans.labels_)

# get the centroid vectors
centroid = kmeans.cluster_centers_


percent = []
for i in range(len(centroid)):
  j = labels.count(i)
  j = j / len(labels)
  percent.append(j)

plt.pie(percent,colors=np.array(centroid/255),labels=np.arange(len(centroid)))
# plt.imshow(img)
plt.show()