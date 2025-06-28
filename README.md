# Intelligent Claims QA Service

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Framework](https://img.shields.io/badge/framework-FastAPI-green)

[cite_start]This project is a Python microservice developed for the Curacel AI/ML Engineer take-home task[cite: 1]. [cite_start]It intelligently processes medical claim documents by extracting structured data from images or PDFs and answering questions about their content[cite: 4].

## ✨ Features

* [cite_start]**Intelligent Data Extraction**: A `POST /extract` endpoint that accepts a claim document (image/PDF) and returns a structured JSON object with key details[cite: 5, 6].
* [cite_start]**Question Answering**: A `POST /ask` endpoint that answers natural language questions based on the data extracted from a previously processed document[cite: 8].
* **Confidence Scoring**: An advanced feature that prompts the model to self-evaluate its performance, returning a percentage confidence score for both the data extraction and question-answering tasks.

---

## 🏛️ Architecture & Approach

The service is built with a clean, maintainable architecture that separates the API layer from the core processing logic.

* **API Layer (`main.py`)**: A modern web server built with **FastAPI**. It handles incoming HTTP requests, manages file uploads, and interacts with the processing module. FastAPI was chosen for its high performance, asynchronous capabilities, and automatic generation of interactive API documentation.

* **Core Logic (`processor.py`)**: This module contains the multi-step document processing pipeline powered by Google's **Gemini 1.5 Flash** model.
    1.  **Input Handling**: Accepts an uploaded file. If it's a PDF, it's first converted into a series of images.
    2.  **Text Recognition (OCR)**: The vision capabilities of the Gemini model are used to extract all raw text from the document images.
    3.  [cite_start]**Structured Extraction**: A carefully engineered prompt instructs the model to parse the raw text and populate a predefined JSON schema, turning unstructured data into a reliable format[cite: 2].
    4.  **Confidence Assessment**: The same prompt also asks the model to self-evaluate its extraction accuracy, providing a confidence score.
    5.  **Question Answering**: For the `/ask` endpoint, the extracted JSON is provided as context to the model, which is instructed to answer questions based only on that data and to provide a confidence score for its answer.

---

## 💡 Assumptions & Decisions

During implementation, the following key decisions were made:

* [cite_start]**LLM Choice**: I selected **Google's Gemini 1.5 Flash** model because it is a powerful, multimodal model available under a generous free tier, making it perfect for handling both vision and language processing tasks in a single, efficient tool[cite: 9].
* [cite_start]**Storage**: As per the guidelines, a simple Python dictionary is used for **in-memory storage** of extracted document data[cite: 10]. This is sufficient for the scope of this task. For a production environment, this would be replaced with a persistent database like Redis (for caching) or PostgreSQL.
* **Confidence Score Method**: Since the Gemini API does not provide a built-in confidence metric, I implemented this feature by enhancing the prompts. The prompts explicitly ask the model to self-evaluate and return a numerical confidence score. This demonstrates a more advanced use of prompting to add value and insight into the model's performance.
* **Development Environment**: The project was developed and tested in a cloud-based notebook environment (Google Colab) for ease of setup and GPU access, but the instructions below are for running it on any local machine.

---

## 🚀 Getting Started

Follow these instructions to run the service on your local machine.

### Prerequisites

* Python 3.8+
* Git
* A Google API Key with the **"Generative Language API"** enabled in your Google Cloud project.
* The `poppler` utility library (a dependency for PDF processing).

**On macOS (using Homebrew):**
```bash
brew install poppler
```

**On Debian/Ubuntu:**
```bash
sudo apt-get update && sudo apt-get install -y poppler-utils
```
**On Windows:**
Download and install Poppler for Windows, and add its `bin` directory to your system's PATH.

### Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-link>
    cd <repository-folder>
    ```

2.  **Set Up Environment Variable:**
    Export your Google API key so the application can access it.
    ```bash
    # For macOS/Linux
    export GOOGLE_API_KEY="your_google_api_key_here"

    # For Windows Command Prompt
    set GOOGLE_API_KEY="your_google_api_key_here"
    ```

3.  **Install Dependencies:**
    Install all required Python packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

### Running the Service

1.  **Start the Server:**
    Use `uvicorn` to run the FastAPI application.
    ```bash
    uvicorn main:app --reload
    ```
    The `--reload` flag automatically restarts the server when you make code changes.

2.  **Access the API:**
    The service will be available at `http://127.0.0.1:8000`.
    Open your web browser and navigate to **`http://127.0.0.1:8000/docs`** to view the interactive API documentation (Swagger UI).

---

## 🛠️ API Endpoints

You can test the endpoints directly from the interactive `/docs` page.

### 1. Extract Data

* `POST /extract`
* **Description**: Upload a medical claim document (`.pdf`, `.png`, `.jpg`).
* **Request**: `multipart/form-data` with a `file` field.
* **Successful Response (200 OK):**
    ```json
    {
      "document_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "data": {
        "patient": { "name": "Jane Doe", "age": 34 },
        "diagnoses": ["Malaria"],
        "medications": [{ "name": "Paracetamol", "dosage": "500mg", "quantity": "10 tablets" }],
        "procedures": ["Malaria test"],
        "admission": { "was_admitted": true, "admission_date": "2023-06-10", "discharge_date": "2023-06-12" },
        "total_amount": "15,000"
      },
      "extraction_confidence": 95
    }
    ```

### 2. Ask a Question

* `POST /ask`
* **Description**: Ask a question about an already processed document using its ID.
* **Request Body**:
    ```json
    {
      "document_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "question": "How many tablets of paracetamol were prescribed?"
    }
    ```
* **Successful Response (200 OK):**
    ```json
    {
      "document_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "question": "How many tablets of paracetamol were prescribed?",
      "answer": "10 tablets were prescribed.",
      "answer_confidence": 100
    }
    ```

---

## 🔮 Future Improvements

* **Persistent Storage**: Replace the in-memory dictionary with a robust database like PostgreSQL or a NoSQL alternative to persist data.
* **Containerization**: Create a `Dockerfile` to containerize the application for consistent deployments and scalability.
* **Enhanced Error Handling**: Implement more granular error handling and logging for production monitoring.
* **CI/CD**: Set up a continuous integration and deployment pipeline to automate testing and releases.
