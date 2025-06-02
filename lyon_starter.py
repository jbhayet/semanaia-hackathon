from sklearn.neighbors import KNeighborsRegressor # type: ignore
from metrics import regression_evaluate
from utils import read_test_csv,read_test_csv_full,read_train_csv,visualize_prediction_samples

# Read the training data for Lyon bike sharing system
source,target = read_train_csv('data/lyon_data_series_train.csv')

# Using 90pc for training, 10pc for validation
train_size  = int(len(source) * 0.95)
source_train= source[:train_size]
source_val  = source[train_size:]
target_train= target[:train_size]
target_val  = target[train_size:]

# Read the test data for Lyon bike sharing system
test = read_test_csv('data/lyon_data_series_test_no_occupation.csv')

# Train a model 
neigh = KNeighborsRegressor(n_neighbors=2)
neigh.fit(source_train,target_train)

# Aply prediciton
prediction_val = neigh.predict(source_val)
performance = regression_evaluate(prediction_val,target_val)
print(f"--- Current performance: {performance}")

visualize_prediction_samples(source_val,prediction_val,target_val)