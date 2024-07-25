from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTFeatureExtractor, AutoTokenizer
import pytesseract
import torch
import io
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
# Initialize FastAPI app

# Load the image captioning model and related components
vit_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Set device to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vit_model.to(device)

# Parameters for the image captioning model
max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

# Path to tesseract executable
pytesseract.pytesseract.tesseract_cmd = "F:\\Python\\Tesseract-OCR\\tesseract.exe"

def extract_text(image_data):
    """
    Extracts text from the given image data using Tesseract OCR.

    Parameters:
    image_data (bytes): The image data in bytes.

    Returns:
    str: The extracted text.
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        clean_text = ' '.join(text.split())
        logging.info(f"Extracted text: {clean_text}")
        return clean_text
    except Exception as e:
        logging.error(f"Error in extract_text: {e}")
        return f"An error occurred: {e}"

def predict_caption(image_data):
    """
    Generates a caption for the given image data using the ViT-GPT2 model.

    Parameters:
    image_data (bytes): The image data in bytes.

    Returns:
    str: The generated caption.
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        if image.mode != "RGB":
            image = image.convert(mode="RGB")
        
        pixel_values = feature_extractor(images=image, return_tensors="pt").pixel_values
        pixel_values = pixel_values.to(device)
        
        output_ids = vit_model.generate(pixel_values, **gen_kwargs)
        preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        preds = [pred.strip() for pred in preds]
        logging.info(f"Generated caption: {preds[0]}")
        return preds[0]
    except Exception as e:
        logging.error(f"Error in predict_caption: {e}")
        return f"An error occurred: {e}"

