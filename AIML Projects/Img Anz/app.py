import streamlit as st
import google.generativeai as genai
from PIL import Image
from pathlib import Path
import os
import io
#==============================
# API KEY LOAD
#==============================
API_KEY = "___YOUR_KEY___"
# =============================
# CONFIGURE GEMINI
# =============================
genai.configure(api_key=API_KEY)
# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Image Analyzer",
    page_icon="🖼️",
    layout="centered"
)
st.title("Image Analyzer")
# =============================
# IMAGE UPLOAD
# =============================
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file:
    image = Image.open(uploaded_file)
    if image.mode != "RGB":
        image = image.convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    image_bytes = buffer.getvalue()
    if st.button("Analyze Image"):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                [
                    "Describe this image in detail.",
                    {
                        "mime_type": "image/jpeg",
                        "data": image_bytes
                    }
                ]
            )
            st.success("✅ Image analysis succeeded")
            st.write(response.text)
        except Exception as e:
            st.error("❌ Image analysis failed")
            st.error(e)