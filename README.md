# Topological Densification and Neural Collapse
 A project studying the interactions between topological densification and neural collapse
 
 ## Setup and Installation
 1. Install the torchph package by 
```
  git clone https://github.com/c-hofer/torchph.git
  pip install -e torchph
  ```
 2. Run svhn_top.py to run experiments on the SVHN dataset and 
    mnist_top.py to run experiments on the MNIST dataset

## Results

| First Header  | Second Header | SVHN-250 |
| ------------- | ------------- | ---------|
| Vanilla  | 92.53 +- 0.76| 75.07 +- 2.70 |
| Hofer et al's topological regularizer | 94.10 +- 0.30 (*)  | 77.50 +- 2.00 (**) |
| Our regularizer  | 94.24 +- 0.47  | 77.50 +- 2.00  |
(*) Hofer’s best result after varying only β and keeping other hyperparameters fixed (e.g. lr=0.1)
(**) Hofer’s best result after a full hyperparameter grid search (i.e. varying both learning rate and β)
