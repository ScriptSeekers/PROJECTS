# Smart Health Monitoring

A machine learning-based health risk assessment system that generates synthetic health data and trains a predictive model to classify individuals as high or low health risk.

## Features

- **Synthetic Data Generation**: Creates 1,000 realistic patient records
- **Predictive Modeling**: Logistic Regression for binary health risk classification
- **Data Visualization**: Three charts analyzing health patterns and predictions
- **Model Evaluation**: Accuracy score and confusion matrix reporting
- **Health Metrics**: Age, heart rate, calories burned, activity level

## Dependencies

- matplotlib
- numpy
- pandas
- scikit-learn
- seaborn

## How to Run

```bash
.\.venv\Scripts\python "Smart Health Monitoring.py"
```

## Workflow

1. **Data Generation**: Creates synthetic patient data with health metrics
2. **Preprocessing**: Converts categorical data and prepares features
3. **Model Training**: Trains Logistic Regression on 80% of data
4. **Evaluation**: Tests on remaining 20% and reports performance
5. **Visualization**: Generates three charts:
   - Heart rate distribution histogram
   - Calories vs age scatter plot (colored by risk)
   - Predicted risk probability distribution

## Model Details

- **Algorithm**: Logistic Regression
- **Features**: Age, Heart Rate, Calories Burned, Activity Level
- **Target**: Binary health risk (0/1)
- **Split**: 80% training, 20% testing

## Output

- Model accuracy and confusion matrix
- Three visualization charts saved/displayed