import pandas as pd # type: ignore
import numpy as np
import ast
import matplotlib.pyplot as plt # type: ignore

def read_train_csv(train_file):
    print(f"--- Reading train data from {train_file}")
    data_train = pd.read_csv(train_file) 
    print(f"--- Read {len(data_train)} records")
    # Columns occupation are filled with strings corresponding to arrays, so we get these arrays
    target     = np.array(data_train['occupation'].apply(
        lambda x: np.array(ast.literal_eval(x))
    ).to_list())
    # Drop the target from the source data
    data_train = data_train.drop(columns=['occupation'])
    # Source data
    source = data_train.to_numpy()
    return source,target

def read_test_csv(test_file):
    print(f"--- Reading test data from {test_file}")
    data_test = pd.read_csv(test_file) 
    print(f"--- Read {len(data_test)} records")
    # Source data
    source = data_test.to_numpy()
    return source

def read_test_csv_full(test_file):
    print(f"--- Reading test data from {test_file}")
    data_test = pd.read_csv(test_file) 
    print(f"--- Read {len(data_test)} records")
    # Source data
    source = data_test.to_numpy()
    return source

def visualize_prediction_samples(source,prediction,ground_truth):

    nsamples = 15
    row_ids = np.random.random_integers(0,source.shape[0],nsamples)
    source_sample     = source[row_ids]
    prediction_sample = prediction[row_ids]
    ground_truth_sample = ground_truth[row_ids]
    fig, ax = plt.subplots(3,5,figsize=(8, 6))
    plt.suptitle('A few samples of prediction/ground truth pairs')
    for i in range(nsamples):
        ax[i//5][i%5].plot(prediction_sample[i],color='red')
        ax[i//5][i%5].plot(ground_truth_sample[i],color='green')
    plt.show()
