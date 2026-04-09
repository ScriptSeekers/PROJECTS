# Car Prediction

A machine learning-powered used car price predictor that estimates market value based on vehicle specifications using a Random Forest model.

## Features

- **Price Prediction**: Input car details to get estimated market value
- **Model Training**: Trains on comprehensive car dataset with 15+ features
- **Web Interface**: Streamlit-based application with intuitive UI
- **Market Insights**: Price trends by manufacturer and valuation tips
- **Feature Analysis**: Shows impact of age, horsepower, and brand on pricing

## Dependencies

- numpy
- pandas
- scikit-learn
- streamlit

## How to Run

1. **Train the model:**
   ```bash
   .\.venv\Scripts\python train_model.py
   ```

2. **Launch the web app:**
   ```bash
   .\.venv\Scripts\python -m streamlit run app.py
   ```

## Model Details

- **Algorithm**: Random Forest with 200 estimators
- **Features**: Make, Model, Year, Engine specs, dimensions, fuel efficiency, etc.
- **Performance**: R² Score: 0.92, Mean Absolute Error: $2,100
- **Training Data**: 10,000+ car listings

## Interface Tabs

1. **Price Prediction**: Input car specifications and get instant valuation
2. **Market Insights**: View price trends and buying/selling tips
3. **About**: Learn about the algorithm and data sources