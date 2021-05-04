import sys
import copy
import scipy
import torch
import numpy as np

from IPython import embed
from scipy.sparse.linalg import svds



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

data = np.random.rand(30, 100)
labels = np.random.randint(10, size=(30))
C = 10 #number of classes

class SVD_Visualizer():
    def __init__(self, z, y, num_classes, features):
        self.z = z
        self.y = y
        self.classes = []
        self.num_classes = num_classes
        self.features = features
        for i in range(num_classes):
            sub_batch = torch.cat([z[j].unsqueeze(0) for j in range(z.shape[0]) if y[j] == i], 0)
            self.classes.append(sub_batch)
    #Calculate class means
    def mean(self):
        class_means = torch.zeros(self.num_classes, self.features)
        for i in range(self.num_classes):
            class_means[i] = torch.mean(self.classes[i], 0)
        return class_means

    #Calculate global mean
    def global_mean(self):
        return torch.mean(self.z, 0)
