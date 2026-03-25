# H-CX-101: PH Difficulty Score — Predicting Dataset Difficulty via Epoch 1 H0_total

> Epoch 1 H0_total is a universal indicator of dataset difficulty.
> Larger H0 = classes well-separated = easier; smaller H0 = overlapping = harder.

## Background

- MNIST H0≈4.2, Fashion H0≈2.3, CIFAR H0≈2.1
- MNIST acc=98% > Fashion 89% > CIFAR 54%
- H0 and final accuracy share the same ordering

## Predictions

1. Correlation between epoch 1 H0_total and final accuracy r > 0.9
2. H0_total can predict difficulty before training on new datasets too
3. H0_total / n_classes = normalized difficulty score

## Verification Status

- [ ] cross-dataset H0 vs accuracy
- [ ] normalized score
