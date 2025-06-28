import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from pydantic import BaseModel
import processor  # Your core logic file

# --- App Initialization ---
app = FastAPI(
    title="Curacel Intelligent Claims QA Service",
    description="Extracts structured data from medical claims and answers questions with confidence scores.",
)

# --- In-Memory Storage ---
# This will store the full output from the processor, including confidence scores
documents_db = {}

# --- Pydantic Models ---
class AskRequest(BaseModel):
    document_id: str
    question: str

# --- API Endpoints ---

@app.get("/", summary="Root endpoint to check service status")
def read_root():
    #A simple endpoint to confirm that the service is running.
    return {"status": "ok", "message": "Welcome to the Intelligent Claims QA Service!"}


@app.post("/extract", summary="Extract structured data from a claim document")
async def extract_data_from_document(file: UploadFile = File(...)):
    """
    Accepts a medical claim document (image or PDF), extracts structured data,
    and returns it along with an extraction confidence score.
    """
    temp_dir = f"temp_{uuid.uuid4()}"
    os.makedirs(temp_dir)
    temp_file_path = os.path.join(temp_dir, file.filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        image_paths = [temp_file_path]
        if file.filename.lower().endswith('.pdf'):
            image_paths = processor.convert_pdf_to_images(temp_file_path, temp_dir)
            if not image_paths:
                raise HTTPException(status_code=500, detail="Failed to convert PDF to images.")

        full_document_text = ""
        for i, path in enumerate(image_paths):
            page_text = processor.extract_text_from_image(path)
            full_document_text += f"\n\n--- Page {i+1} ---\n\n{page_text}"

        structured_output = processor.structure_extracted_text(full_document_text)
        if "error" in structured_output:
            raise HTTPException(status_code=500, detail=structured_output.get("details", "Processing error"))

        document_id = str(uuid.uuid4())
        documents_db[document_id] = structured_output  # Store the entire object

        print(f"Successfully processed and stored document with ID: {document_id}")

        # The response includes the document_id and unpacks the processor's output
        return {
            "document_id": document_id,
            **structured_output
        }

    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.post("/ask", summary="Ask a question about a previously extracted document")
async def ask_question(request: AskRequest):
    """
    Accepts a document_id and a question, responding with an answer
    and a confidence score based on the stored data.
    """
    document_full_output = documents_db.get(request.document_id)
    if not document_full_output:
        raise HTTPException(status_code=404, detail="Document not found. Please run /extract first.")

    # I pass only the 'data' part to the context for answering the question.
    document_data_context = document_full_output.get("data")
    if not document_data_context:
         raise HTTPException(status_code=404, detail="Could not find 'data' for the specified document.")


    # This function now returns a dict with 'answer' and 'answer_confidence'
    answer_object = processor.answer_question_from_context(request.question, document_data_context)

    # The response unpacks the answer object from the processor
    return {
        "document_id": request.document_id,
        "question": request.question,
        **answer_object
    }

# To run the app in Colab or locally:
# 1. Ensure you have an environment variable `GOOGLE_API_KEY` set.
# 2. In your terminal, run: `uvicorn main:app --reload`
# 3. Open your browser to http://127.0.0.1:8000/docs for the API documentation.
