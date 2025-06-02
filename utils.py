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

def visualize_prediction_daily_sequences(sequence):
    nsamples = 15
    row_ids = np.random.random_integers(0,sequence.shape[0],nsamples)
    sequence_sample     = sequence[row_ids]
    fig, ax = plt.subplots(3,5,figsize=(8, 6))
    plt.suptitle('A few samples of hourly occupation data over a random set of stations', fontsize=16)
    for i in range(nsamples):
        ax[i//5][i%5].plot(sequence_sample[i],color='green')
    plt.show()
