# -*- coding: utf-8 -*-
"""svhn_top

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/16bI9k4zqfnOWAkVJho1x4LsDjFKMlWHp

Install the topology package and Torchph
"""

!cd /tmp/
!git clone https://github.com/c-hofer/torchph.git
!pip install -e torchph
!pip install ninja

# Commented out IPython magic to ensure Python compatibility.
import sys
sys.path.append('/content/drive/MyDrive/TDD')
# %cd /content/drive/MyDrive/TDD
# %load svd.py
# %load ds_util_mod.py
from ds_util_mod import * 

print(sys.path)

import json
import urllib.request

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.utils.data as Data

import torchvision.utils
import torchvision.datasets as dsets
import torchvision.transforms as transforms
import torchvision.transforms.functional as F
from torchvision import models
from torch.distributions import MultivariateNormal
import svd

from torchvision import datasets, transforms

from sklearn.decomposition import PCA
from scipy.sparse.linalg import svds


# import VR persistence computation functionality
from torchph.torchph.pershom import vr_persistence_l1, vr_persistence #This may take a long time to load

"""The CNN models used in the paper"""

class LinearView(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x.view(x.size()[0], -1)

#Model used by Hofer et al. to train on MNIST
class SimpleCNN_MNIST(nn.Module):
    def __init__(self,
                 num_classes,
                 batch_norm):
        super().__init__()

        def activation(): return nn.LeakyReLU(0.1)

        if batch_norm:
            def bn_2d(dim): return nn.BatchNorm2d(dim)

            def bn_1d(dim): return nn.BatchNorm1d(dim)
        else:
            def bn_2d(dim): return Identity(dim)

            def bn_1d(dim): return Identity(dim)

        self.feat_ext = nn.Sequential(
            nn.Conv2d(1, 8, 3, padding=1),
            bn_2d(8),
            activation(),
            nn.MaxPool2d(2, stride=2, padding=0),
            #
            nn.Conv2d(8, 32, 3, padding=1),
            bn_2d(32),
            activation(),
            nn.MaxPool2d(2, stride=2, padding=0),
            #
            nn.Conv2d(32, 64, 3, padding=1),
            bn_2d(64),
            activation(),
            nn.MaxPool2d(2, stride=2, padding=0),
            #
            nn.Conv2d(64, 128, 3, padding=1),
            bn_2d(128),
            activation(),
            nn.MaxPool2d(2, stride=2, padding=0),
            LinearView(),
        )

        cls = nn.Linear(128, num_classes)

        self.cls = nn.Sequential(cls)

    def forward(self, x):
        z = self.feat_ext(x)
        y_hat = self.cls(z)

        return y_hat

class SimpleCNN13(nn.Module):
    def __init__(self,
                 num_classes: int,
                 batch_norm: bool, 
                 drop_out: bool, 
                 cls_spectral_norm: bool,
                 final_bn: bool):
        super().__init__()

        def activation(): return nn.LeakyReLU(0.1)

        if drop_out:
            def dropout(p): return nn.Dropout(p)
        else:
            def dropout(p): return Identity()

        bn_affine = True

        if batch_norm:
            def bn_2d(dim): return nn.BatchNorm2d(dim, affine=bn_affine)

            def bn_1d(dim): return nn.BatchNorm1d(dim, affine=bn_affine)
        else:
            def bn_2d(dim): return Identity(dim)

            def bn_1d(dim): return Identity(dim)

        self.feat_ext = nn.Sequential(
            nn.Conv2d(3, 128, 3, padding=1),
            bn_2d(128),
            activation(),
            nn.Conv2d(128, 128, 3, padding=1),
            bn_2d(128),
            activation(),
            nn.Conv2d(128, 128, 3, padding=1),
            bn_2d(128),
            activation(),
            nn.MaxPool2d(2, stride=2, padding=0),
            dropout(0.5),
            #
            nn.Conv2d(128, 256, 3, padding=1),
            bn_2d(256),
            activation(),
            nn.Conv2d(256, 256, 3, padding=1),
            bn_2d(256),
            activation(),
            nn.Conv2d(256, 256, 3, padding=1),
            bn_2d(256),
            activation(),
            nn.MaxPool2d(2, stride=2, padding=0),
            dropout(0.5),
            #
            nn.Conv2d(256, 512, 3, padding=0),
            bn_2d(512),
            activation(),
            nn.Conv2d(512, 256, 1, padding=0),
            bn_2d(256),
            activation(),
            nn.Conv2d(256, 128, 1, padding=0),
            bn_2d(128) if final_bn else Identity(),
            activation(),
            nn.AvgPool2d(6, stride=2, padding=0),
            LinearView(),
        )

        cls = nn.Linear(128, num_classes)
        if cls_spectral_norm:
            nn.utils.spectral_norm(cls)

        self.cls = nn.Sequential(cls)

    def forward(self, x):
        z = self.feat_ext(x)
        y_hat = self.cls(z)

        return y_hat

"""Helper functions"""

'''
Does a projection to the first 2 basis vectors of the simplex ETF
'''
def rep_plot(model, device, layer, data_loader, name):
    model.eval()
    #data_rep = np.empty((0, 128))
    data_rep = torch.empty((0, 128)).to(device)
    labels = torch.empty((0)).to(device)
    data_pca = []
    colors = ['red','green','blue','purple', 'yellow',
    'magenta','black','orange', 'pink','brown'] #Color code the different classes
    for batch_idx, (x, y) in enumerate(data_loader, start=1):
        x, y = x.to(device), y.to(device)
        # second last layer's output
        model(x)
        features = layer.output

        data_rep = torch.cat((data_rep, features), 0)
        labels = torch.cat((labels, y), 0)

    #Do SVD decomposition
    C = num_classes
    means = svd.SVD_Visualizer(data_rep, labels, C, feature_dim)

    # means
    mu = means.mean()
    mu_G = means.global_mean().unsqueeze(0)

    mu = mu.to(device)
    mu_G = mu_G.to(device)

    mu_c = mu - mu_G #Center class means around global mean

    # weights
    #w = self.model.get_imp_layers()[-1].weight

    # procrustes problem
    J = torch.eye(C) - torch.ones(C)/C
    J = J.to(device)
    u,s,v = torch.svd(J.T @ mu_c)
    R = v @ u.T

    #w_ = w @ R
    mu_c_ = mu_c @ R

    #Project data to the first 2 rows of R
    data_rep_c_ = data_rep @ R
    two_dim_projection = data_rep_c_[:, 0:2]
    projected_data = two_dim_projection.detach().cpu().numpy()

    plt.figure(figsize=(5,5))
    plt.scatter(projected_data[:,0], projected_data[:,1], c=labels.detach().cpu().numpy(), cmap=matplotlib.colors.ListedColormap(colors))
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Representation space of data');
    plt.savefig("images_svhn_top/" + name)


def vr_persistence_l2(point_cloud):
    EPSILON = 0.000001
    D = (point_cloud.unsqueeze(0) - point_cloud.unsqueeze(1)).pow(2).sum(2)
    tmp = torch.zeros_like(D)
    tmp[D == 0.0] = EPSILON
    D = D + tmp
    D = D.sqrt()
    return vr_persistence(D, 0, 0)

#Setup for training
epochs = 310
batch_size = 8
top_scale = 0.5
w_top_loss = 0.1 #Weight given to the topological loss
num_classes = 10
num_samples = 250    #250 for MNIST/SVHN, 1000 for CIFAR10
feature_dim = 128

from torch.utils.data import DataLoader, Subset, Dataset
class my_subset(Dataset):
    """
    Subset of a dataset at specified indices.

    Arguments:
        dataset (Dataset): The whole Dataset
        indices (sequence): Indices in the whole set selected for subset
        labels(sequence) : targets as required for the indices. will be the same length as indices
    """
    def __init__(self, dataset, indices, labels):
        self.dataset = torch.utils.data.Subset(dataset, indices)
        self.targets = torch.tensor(labels)[indices]
    def __getitem__(self, idx):
        image = self.dataset[idx][0]
        target = self.targets[idx]
        return (image, target)

    def __len__(self):
        return len(self.targets)

def collate_fn(it):
    batch_x = []
    batch_y = []
    
    for x, y in it:
        batch_x.append(x)
        batch_y.append(torch.tensor([y]*x.shape[0], dtype=torch.long))

    #Convert to tensors
    batch_x = torch.cat(batch_x, 0)
    batch_y = torch.cat(batch_y, 0)

    return batch_x, batch_y

#Load data splits from data_loader_pickle
import pickle
import os
from pathlib import Path


# Save the second last layer's output (i.e. the representation space)
def hook(module, input, output):
    module.output = output

SPLIT_INDICES_PTH = 'data_train_indices.pickle'

with open(SPLIT_INDICES_PTH, 'br') as fid:
        cache = pickle.load(fid)

I = cache['cifar10_train', 1000]

J = cache['MNIST_train', 250]

K = cache['SVHN_train', 250]

#train_data = datasets.MNIST('../data', download=True, train=True, transform=transforms.ToTensor())
#test_data = datasets.MNIST('../data', download=True, train=False, transform=transforms.ToTensor())

#train_data = datasets.CIFAR10('../data', download=True, train=True, transform=transforms.ToTensor())
#test_data = datasets.CIFAR10('../data', download=True, train=False, transform=transforms.ToTensor())

train_data = datasets.SVHN('../data', download=True, split='train', transform=transforms.ToTensor())
test_data = datasets.SVHN('../data', download=True, split='test', transform=transforms.ToTensor())



#Test data
test_loader = torch.utils.data.DataLoader(
    test_data,
    batch_size=batch_size, shuffle=False, drop_last=False)

#Take the dataset splits from the pickle (data over 10 runs)
train_data = [my_subset(train_data, indices=i, labels=train_data.labels) for i in K]

for k in range(1):
    
    train_accuracy = []
    test_accuracy = []
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    #model = SimpleCNN_MNIST(num_classes, True).to(device)
    model = SimpleCNN13(num_classes, True, True, False, True).to(device) #For SVHN and CIFAR10


    layer = model.feat_ext #Feature space = R^128
    layer.register_forward_hook(hook)

    # Hyperparameters
    lr = 0.03
    momentum=0.9
    weight_decay = 10e-3


    optimizer = torch.optim.SGD(model.parameters(), lr=lr, weight_decay=weight_decay, momentum=momentum)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer,
                T_max=epochs,
                eta_min=0,
                last_epoch=-1)
    loss_function = nn.CrossEntropyLoss()
    #Separate the data into the 10 classes
    class_inds = [torch.where(train_data[k].targets == class_idx)[0]
          for class_idx in range(10)]

    
    ds_stats = ds_statistics(train_data[k])
    # Transforms employed in C. Hofer et al's paper
    transform = transforms.Compose([transforms.RandomCrop(32, padding=4),
            transforms.RandomHorizontalFlip(), transforms.Normalize(
                ds_stats['channel_mean'],
                ds_stats['channel_std'])])
    train_data[k].dataset.transform = transform

    
    #This custom dataset draws num_intra_samples samples from the same class
    augmented_data = IntraLabelMultiDraw(
            train_data[k], 16)    
    
    #Plot the data of the first run
    if (k == 0):
        #Collect data for plotting
        data_loader = torch.utils.data.DataLoader(train_data[k],
                batch_size=batch_size, shuffle=False, drop_last=False)
        rep_plot(model, device, layer, data_loader, "pre_training") #What the rep space looks like before training

    dl_train = DataLoader(
        augmented_data,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        collate_fn=collate_fn,
        num_workers=0)     
     
    
    #Training
    print("Starting run " + str(k + 1))
    for epoch in range(1, epochs+1):
        # train phase
        model.train()
        accuracy = 0
        N = 0

        batches = 0
        
        for batch_idx, (x, y) in enumerate(dl_train, start=1):
            x, y = x.to(device), y.to(device)
            
            n = x.shape[0] // batch_size

            # forward pass
            logits = model(x)
            loss = loss_function(logits, y)
            
            z = layer.output #Features in representation space
                
            l_top = torch.tensor(0.0).to(device)
            
            #Sliding Regularizer
            #Have the beta decrease by square root to 0 and top. weight go up linearly from 0 to 0.1
            time_scale = (epoch / epochs) * 0.1
            t = np.sqrt(epochs - epoch) / np.sqrt(epochs)
            top_scale = (t * 1.0)        

            for i in range(batch_size):
                z_sample = z[i*n: (i+1)*n, :].contiguous()
                lt = vr_persistence_l2(z_sample)[0][0][:, 1]
                #lt = vr_persistence_l1(z_sample, 1, 0)[0][0][:, 1]           
                l_top = l_top + (lt-top_scale).abs().sum()
            l_top = l_top / float(batch_size)
            print(l_top)
            w_top = time_scale
            
            l = loss + (w_top * l_top)
            
            #l = loss
            # backpropagation
            optimizer.zero_grad()
            l.backward()

            optimizer.step()


            # check if predicted labels are equal to true labels
            predicted_labels = torch.argmax(logits,dim=1)
            accuracy += torch.sum((predicted_labels==y).float()).item()
            N += x.shape[0]

            print('Train\t\tEpoch: {} \t'
                  'Batch {}({:.0f}%) \t'
                  'Batch Loss: {:.6f} \t'
                  'Batch Accuracy: {:.6f}'.format(
                      epoch,
                      batch_idx,
                      100. * batch_idx / (num_samples // batch_size),
                      l.item(),
                      100. * accuracy/N))
        train_accuracy.append(100. * accuracy/N)

        scheduler.step()

        # test phase
        model.eval()
        accuracy = 0
        N = 0

        # iterate over test data
        for batch_idx, (x, y) in enumerate(test_loader, start=1):
            x, y = x.to(device), y.to(device)

            # forward pass
            logits = model(x)

            # check if predicted labels are equal to true labels
            predicted_labels = torch.argmax(logits,dim=1)
            accuracy += torch.sum((predicted_labels==y).float()).item()
            N += x.shape[0]
        test_accuracy.append(100. * accuracy/N)
        print(test_accuracy[-1])

        #Take snapshot of training data every 10 epochs
        #if (k == 0 and epoch % 10 == 0):
            #rep_plot(model, device, layer, data_loader, "epoch_" + str(epoch)) #What the rep space looks like before training

    # plot results

    plt.close("all")
    plt.title('Accuracy Versus Epoch')
    plt.plot(range(1, epochs+1), train_accuracy, label='Train')
    plt.plot(range(1, epochs+1), test_accuracy, label='Test')
    plt.legend()
    results_path = "/content/drive/MyDrive/TDD/images_svhn_top/" + "results_" + str(k) + ".png"
    #plt.savefig(results_path)
    plt.show()

    model_path = "/content/drive/MyDrive/TDD/models/" + "svhn_delayed_" + str(k) + ".pt"
    torch.save(model.state_dict(), model_path)
    #rep_plot(model, device, layer, data_loader, "post_training") #What the rep space looks like after training