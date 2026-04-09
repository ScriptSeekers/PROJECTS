import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# 1. Load dataset
data = pd.read_csv("D:\\PROJECTS\\AIML Projects\\Car_Prediction\\cars.csv")   # rename your file accordingly

# Drop rows with missing target
data = data.dropna(subset=["MSRP"])

# Features and Target
X = data.drop("MSRP", axis=1)
y = data["MSRP"]

# 2. Select useful features
X = data.drop("MSRP", axis=1)
y = data["MSRP"]

categorical_features = ["Make", "Model", "Engine Fuel Type", "Transmission Type", 
                        "Driven_Wheels", "Market Category", "Vehicle Size", "Vehicle Style"]

numerical_features = ["Year", "Engine HP", "Engine Cylinders", 
                      "Number of Doors", "highway MPG", "city mpg", "Popularity"]

# Clean categorical columns (convert all to string)
for col in categorical_features:
    X[col] = X[col].astype(str)

# Fill missing values
X[numerical_features] = X[numerical_features].fillna(0)
X[categorical_features] = X[categorical_features].fillna("Unknown")
# 3. Preprocessing
preprocessor = ColumnTransformer([
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ("num", "passthrough", numerical_features)
])

# 4. Model Pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=200, random_state=42))
])

# 5. Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Handle missing values in numerical columns
X_train = X_train.fillna(0)
X_test = X_test.fillna(0)

# Train
model.fit(X_train, y_train)

# 6. Evaluate
y_pred = model.predict(X_test)
print("R2:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))
import numpy as np
print("RMSE:", np.sqrt(mean_squared_error(y_test, y_pred)))

# 7. Save model
with open("used_car_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as used_car_model.pkl")
