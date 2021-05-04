# Topological Densification and Neural Collapse
 A project studying the interactions between topological densification and neural collapse
 
 ## Introduction
 This project is based on two main papers: 
 **Topologically Densified Distributions:** https://arxiv.org/pdf/2002.04805.pdf 
 **Prevalence of Neural Collapse during the terminal phase of deep learning training:** https://arxiv.org/pdf/2008.08186.pdf
V. Papyan et al observed an interesting phenomenon occurring in the second last layer of neural networks during training, naming it **neural collapse**. The class means converge to a set of maximally equiangular points in the embedding space called the **Simplex Equiangular Tight Frame (Simplex ETF)**, as well as converging to their own duals in the classifier (dual) space. It was later found out that this configuration is the solution to the dynamical system corresponding to minimizing the MSE and crossentropy losses in a neural network (albeit a simplified version of the dynamical system). 

Indeed, V. Papyan et al observed that as the class-means moved closer to the Simplex ETF and to their dual classifiers, the testing accuracy also improved, even after the model has achieved 100% training accuracy. This phenomenon was recorded by V. Papyan et al across all the canonical datasets (MNIST, SVHN, CIFAR-10, etc.).

One of the features of the neural collapse phenomenon was the convergence of within-class variability to 0, meaning that members of the same class in the training data cluster closer together over more training time. On the other hand, there was been interesting work by C. Hofer et al which leverages topological properties of the training data (namely Vietoris-Rips persistent homology) to enforce the clustering of training data. It turns out that enforcing the clustering of data will in effect "drag" the space around the data so that the testing data will become closer to the training data as well, eventually dragging the testing data across the decision boundary to the correct region. This is a process the authors call **"Topological Densification"**. One unexplained effect that happened during the authors' experiments is that it was detrimental to collapse the data too quickly. We did an experiment where we took this to the extreme and found out that collapsing the data too early prevents the classes from seaparating from each other (thereby preventing neural collapse). This is an effect which we leverage in our experiments.

We combine the ideas in both papers as follows: we use the topological regularizer constructed by C. Hofer et al to "coax" the class-means toward the Simplex ETF. Since the convergence to 0 of within-class variability is a feature of neural collapse, it seemed natural to actually enforce this effect quantitatively via a regularizer.
Our strategy is to introduce:
- A sliding weight on C. Hofer's regularizer so that during the beginning of training, the regularizer has no weight while at the end of training, the regularizer has full weight. I.e. the beginning of training is just a vanilla model with crossentropy loss, and at the end of training there is a regularizer encouraging the clustering of training data. 
- A sliding distance β for the maximally allowable distance between points. From a constant we choose at the beginning of training decaying to 0 by the end of training. I.e. we aim to slowly make the data cluster together throughout the entirely of training, avoiding the pitfalls of collapsing the data too quickly in the early epochs.

By doing so we have achieved improvements in accuracy over both the vanilla model and C. Hofer et al's topological regularizer (shown in the tables below). Our heuristic explanation is that since our regularizer carries very little weight at the beginning of training, the model will first make the data converge to a Simplex ETF. When the regularizer kicks in during the latter stages, the classes are already sufficiently separated so that the topological regularizer will only cluster them toward their class-means instead of clustering the whole training data. In doing so, our sliding regularizer actually improved the model's convergence speed to the Simplex ETF and dual classifiers. 

In conclusion, it seems to be a promising approach to use topological properties of the training data to faciliate neural collapse in deep neural networks. 

 
 ## Setup and Installation
 1. Install the torchph package by 
```
  git clone https://github.com/c-hofer/torchph.git
  pip install -e torchph
  ```
 2. Run svhn_top.py to run experiments on the SVHN dataset and 
    mnist_top.py to run experiments on the MNIST dataset
    model_analysis.py to calculate the neural collapse metrics 
 

## Results
For all training runs we have used SGD with momentum 0.9 and weight decay 0.001. As in Hofer et al’s
paper, we use the names MNIST-250 and SVHN-250 to mean that our training sample size is 250.
We also used the following hyperparameters:
| Dataset | Model | Hyperparameter | Value |
|---------|-------|----------------|-------|
|MNIST-250|Simple-MNIST CNN 13|Learning rate <br> Topological Scale <br> β|0.1 <br> 0.1 <br> 1.1 |
|SVHN-250|Simple CNN 13|Learning rate <br> Topological Scale <br> β|0.03 <br> 0.1 <br> 1.0 |

| Regularization Type  | MNIST-250 | SVHN-250 |
| ------------- | ------------- | ---------|
| Vanilla  | 92.53 ± 0.76| 75.07 ± 2.70 |
| Hofer et al's topological regularizer | 94.10 ± 0.30  (a) | 77.50 ± 2.00 (b) |
| Our regularizer  | 94.24 ± 0.47  | 78:23 ± 1:81  |

(a) Hofer’s best result after varying only β and keeping other hyperparameters fixed (e.g. lr=0.1)<br>
(b) Hofer’s best result after a full hyperparameter grid search (i.e. varying both learning rate and β)
