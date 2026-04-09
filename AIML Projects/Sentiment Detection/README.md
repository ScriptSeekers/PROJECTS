# Sentiment Detection

A command-line sentiment analyzer that uses natural language processing to determine the emotional tone and characteristics of text.

## Features

- **Sentiment Classification**: Categorizes text as Positive, Negative, or Neutral
- **Polarity Score**: Returns score between -1 and 1 indicating positivity/negativity
- **Subjectivity Score**: Measures how subjective (opinion-based) vs objective the text is
- **Interactive Loop**: Continuously accepts user input until 'exit' command

## Dependencies

- textblob

## How to Run

```bash
.\.venv\Scripts\python "Sentiment Detection.py"
```

## Analysis Output

For each input text, the program returns:
- **Sentiment**: Positive/Negative/Neutral classification
- **Polarity**: Numerical score (-1 to 1)
- **Subjectivity**: Numerical score (0 to 1)

## Technical Details

- **Library**: TextBlob for sentiment analysis
- **Classification Logic**: Based on polarity score (positive > 0, negative < 0, neutral = 0)
- **Input Method**: Command-line interface with continuous input loop