import os
import re
import json
import google.generativeai as genai
import PIL.Image
from pdf2image import convert_from_path

# This global variable will be configured by the main script
model = None

def configure_model(api_key):
    #Initializes the Gemini model with the provided API key
    global model
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        print("✅ Gemini Model Configured Successfully")
    except Exception as e:
        print(f"🛑 ERROR: Failed to configure Gemini model: {e}")
        raise

def convert_pdf_to_images(pdf_path, output_folder):
    #Converts a PDF file to a series of PNG images.
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    print(f"Converting {pdf_path} to images...")
    try:
        images = convert_from_path(pdf_path, fmt='png', output_folder=output_folder)
        image_paths = sorted([os.path.join(output_folder, f) for f in os.listdir(output_folder) if f.endswith('.png') and not f.startswith('.')])
        print(f"Successfully converted PDF to {len(image_paths)} images.")
        return image_paths
    except Exception as e:
        print(f"An error occurred during PDF conversion: {e}")
        return []

def extract_text_from_image(image_path):
    #Uses the Gemini model to extract all text from a single image.
    print(f"Processing image: {image_path}...")
    if not model:
        raise ValueError("Gemini model is not configured. Call configure_model() first.")
    try:
        img = PIL.Image.open(image_path)
        response = model.generate_content(["Extract all visible text from this document image.", img], stream=False)
        return response.text if response.parts else "Warning: Model returned no content."
    except Exception as e:
        return f"An error occurred while processing {image_path}: {e}"

def structure_extracted_text(text_content):

    #Uses the Gemini model to convert unstructured text into a structured JSON object,including a self-assessed confidence score.
    
    print("Structuring extracted text and assessing confidence...")
    if not model:
        raise ValueError("Gemini model is not configured. Call configure_model() first.")
    
    prompt = f"""
    Based on the following medical claim text, extract the key details. Then, return a single, clean, valid JSON object with two main keys: "data" and "extraction_confidence".
    
    1.  The "data" key should contain the structured information matching this schema:
        {{
          "patient": {{"name": "string", "age": "integer or null", "Insurance Scheme Service Provider": "string or null"}},
          "diagnoses": ["list of strings"],
          "medications": [{{"name": "string", "dosage": "string or null", "quantity": "string or null"}}],
          "procedures": ["list of strings"],
          "admission": {{"was_admitted": "boolean", "admission_date": "string in YYYY-MM-DD format or null", "discharge_date": "string in YYYY-MM-DD format or null"}},
          "total_amount": "string"
        }}
    2.  The "extraction_confidence" key should contain your estimated confidence level (a number from 0% to 100%) that the extracted data is accurate and complete based on the source text.

    Do not include any explanatory text or markdown formatting like ```json.

    Text to analyze:
    ---
    {text_content}
    ---
    """
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        # The entire response is the JSON object needed
        structured_output = json.loads(cleaned_text)
        print("Successfully structured data with confidence score.")
        return structured_output
    except Exception as e:
        print(f"Error during structuring: {e}\nRaw response: {response.text}")
        return {"error": "Failed to parse JSON from model output.", "details": str(e)}

import json 

def answer_question_from_context(question, json_context):
    """
    Answers a question based on JSON data and provides a confidence score.
    Returns a dictionary.
    """
    print(f"Answering question '{question}' with confidence assessment...")
    if not model:
        raise ValueError("Gemini model is not configured. Call configure_model() first.")

    prompt = f"""
    You are an assistant for a medical claims processor. Answer the question based ONLY on the provided JSON data.

    Then, return your response as a single, clean JSON object with two keys:
    1. "answer": A string containing your concise answer.
    2. "answer_confidence": A number from 0% to 100% representing how certain you are that the answer is fully supported by the provided data.

    JSON Data:
    {json.dumps(json_context, indent=2)}

    Question: {question}
    """
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
        # The function now returns a dictionary, not just a string
        answer_object = json.loads(cleaned_text)
        return answer_object
    except Exception as e:
        print(f"An error occurred during question answering: {e}")
        return {"answer": "Sorry, an error occurred while answering.", "answer_confidence": 0}
