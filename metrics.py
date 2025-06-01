import numpy as np

# Define the metrics for evaluating the predictions
def regression_evaluate(predictions,ground_truth):
    difference = (predictions-ground_truth)**2
    mse        = np.sqrt(difference.mean(axis=1))
    maxe       = np.sqrt(difference.max(axis=1))
    return mse.mean().round(3),maxe.mean().round(3)