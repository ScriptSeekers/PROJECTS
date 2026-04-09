# Image Analyzer (Img Anz)

An AI-powered web application that provides detailed image analysis using Google's Gemini AI model.

## Features

- **Image Upload**: Support for JPG, JPEG, PNG, and WebP formats
- **AI Analysis**: Uses Google Gemini 2.5-flash model for detailed descriptions
- **Image Preview**: Displays uploaded images within the interface
- **User Feedback**: Success/error messages with visual indicators
- **Error Handling**: Graceful exception handling for API failures

## Dependencies

- Pillow
- google-generativeai
- streamlit

## How to Run

```bash
.\.venv\Scripts\python -m streamlit run app.py
```

## Setup Requirements

- Replace `API_KEY = "___YOUR_KEY___"` in `app.py` with your actual Google Generative AI API key
- Install dependencies: `pip install -r requirements.txt`

## Workflow

1. Upload an image through the web interface
2. Image is converted to JPEG format if needed
3. Click "Analyze Image" button
4. AI generates detailed description using Gemini model
5. Results displayed to the user

## Technical Details

- **Model**: Google Gemini 2.5-flash
- **Prompt**: "Describe this image in detail"
- **Format Conversion**: Automatic RGB conversion for compatibility