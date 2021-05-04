# Topological Densification and Neural Collapse
 A project studying the interactions between topological densification and neural collapse
 
 ## Introduction
 This project is based on two main papers: 
 **Topologically Densified Distributions:** https://arxiv.org/pdf/2002.04805.pdf 
 **Prevalence of Neural Collapse during the terminal phase of deep learning training:** https://arxiv.org/pdf/2008.08186.pdf
V. Papyan et al observed an interesting phenomenon occurring in the second last layer of neural networks during training, naming it **neural collapse**. The class means converge to a set of maximally equiangular points in the embedding space called the **Simplex Equiangular Tight Frame (Simplex ETF)**, as well as converging to their own duals in the classifier (dual) space. It was later found out that this configuration is the solution to the dynamical system corresponding to minimizing the MSE and crossentropy losses in a neural network (albeit a simplified version of the dynamical system). 

Indeed, V. Papyan et al observed that as the class-means moved closer to the Simplex ETF and to their dual classifiers, the testing accuracy also improved, even after the model has achieved 100% training accuracy. This phenomenon was recorded by V. Papyan et al across all the canonical datasets (MNIST, SVHN, CIFAR-10, etc.).

One of the features of the neural collapse phenomenon was the convergence of within-class variability to 0, meaning that members of the same class in the training data cluster closer together over more training time. On the other hand, there was been interesting work by C. Hofer et al which leverages topological properties of the training data (namely Vietoris-Rips persistent homology) to enforce the clustering of training data. It turns out that enforcing the clustering of data will in effect "drag" the space around the data so that the testing data will become closer to the training data as well, eventually dragging the testing data across the decision boundary to the correct region. This is a process the authors call **"Topological Densification"**.

We combine the ideas in both papers as follows: we use the topological regularizer constructed by C. Hofer et al to "coax" the class-means toward the Simplex ETF. Since the convergence to 0 of within-class variability is a feature of neural collapse, it seemed natural to actually enforce this effect quantitatively via a regularizer.
Our strategy is to introduce a sliding weight on C. Hofer's regularizer so that it 

 
 ## Setup and Installation
 1. Install the torchph package by 
```
  git clone https://github.com/c-hofer/torchph.git
  pip install -e torchph
  ```
 2. Run svhn_top.py to run experiments on the SVHN dataset and 
    mnist_top.py to run experiments on the MNIST dataset

## Results

| Regularization Type  | MNIST-250 | SVHN-250 |
| ------------- | ------------- | ---------|
| Vanilla  | 92.53 +- 0.76| 75.07 +- 2.70 |
| Hofer et al's topological regularizer | 94.10 +- 0.30   | 77.50 +- 2.00  |
| Our regularizer  | 94.24 +- 0.47  | 77.50 +- 2.00  |

(*) Hofer’s best result after varying only β and keeping other hyperparameters fixed (e.g. lr=0.1)
(**) Hofer’s best result after a full hyperparameter grid search (i.e. varying both learning rate and β)
