# Disease Prediction Using Machine Learning

A machine learning project that predicts diseases based on patient symptoms using an ensemble approach combining three different classifiers.

## Features

- **Ensemble Learning**: Combines SVM, Naive Bayes, and Random Forest classifiers
- **Symptom-Based Prediction**: Takes 132 symptom indicators as input
- **Cross-Validation**: Uses 10-fold CV for reliable model assessment
- **Visualization**: Confusion matrices and performance comparisons
- **Modular Prediction**: Easy-to-use function for disease prediction

## Dependencies

- numpy
- pandas
- scipy
- matplotlib
- seaborn
- scikit-learn

## How to Run

1. **Install dependencies:**
   ```bash
   pip install numpy pandas scipy matplotlib seaborn scikit-learn
   ```

2. **Open the Jupyter notebook:**
   - Navigate to the project folder
   - Open `Notebook-Disease_Prediction_Using_Machine_Learning.ipynb` in Jupyter

3. **Execute cells sequentially** to train models and test predictions

## Dataset Details

- **Features**: 132 symptom indicators (binary 0/1 values)
- **Diseases**: 20+ conditions including AIDS, Diabetes, Malaria, Migraine, etc.
- **Training**: 80/20 split with cross-validation

## Model Performance

- **Individual Models**: SVM, Gaussian Naive Bayes, Random Forest
- **Ensemble Method**: Mode voting from three classifiers
- **Evaluation**: Accuracy scores and confusion matrices

## Prediction Function

```python
result = predictDisease("Itching,Skin Rash,Nodal Skin Eruptions")
# Returns predictions from each model and final ensemble prediction
```

## Workflow

1. Data loading and exploration
2. Model training and evaluation
3. Ensemble prediction with mode voting
4. Interactive disease prediction