#Step 1 : Importing Liberies

import pandas as pd

#Step 2 : Reading CSV file
df = pd.read_csv('D:/PROJECTS/AIML Projects/Car_Prediction/cars.csv')
print(df.head())
average_value = df['Engine HP'].mean()
print("Average of the column:", average_value)
summary_stats = df.describe()
print("Summary statistics:\n", summary_stats)
missing_values = df.isnull().sum()
print("Missing values per column:\n", missing_values)
