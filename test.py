from typing import Union, List
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel

import spacy
import PyPDF2
import os

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload")
def upload(files: List[UploadFile] = File(...)):
    uploadedFiles = []
    for file in files:
        try:
            contents = file.file.read()
            with open(file.filename, 'wb') as f:
                f.write(contents)
                uploadedFiles.append(file.filename)
        except Exception:
            return {"message": "There was an error uploading the file(s)"}
        finally:
            file.file.close()

    return {"files": uploadedFiles}   

class SubmitRequest(BaseModel):
    variables: object = {}
    files: list = []

@app.post("/submit")
def submit(request: SubmitRequest):
    result = []
    for filename in request.files:
        data = extract_text_from_pdf(f"./{filename}", request.variables)
        result.append({
            'file': filename,
            'results': data
        })

    return {"data": result}

def extract_text_from_pdf(pdf_path, search_terms):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        findings = []
        print(findings)
        for page in range(len(reader.pages)):
          text = reader.pages[page].extract_text()
          doc = nlp(text)
          for sent in doc.sents:
              for category, keywords in search_terms.items():
                for keyword in keywords:
                    if keyword.lower() in sent.text.lower():
                        findings.append({
                            'page': page + 1,
                            'sentence': sent.text.strip().replace("\n", ""),
                            'variable': category,
                            'keyword': keyword.lower()
                        })
    return findings

def process_documents(directory):
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            results[filename] = extract_text_from_pdf(file_path)
    return results

# Specify the directory containing the documents
# directory = '/mnt/d/Arya Nanda/Work/Project/Frans/python-search-pdf'
# results = process_documents(directory)

# # Display or save the results
# for filename, content in results.items():
#     print(f"Results for {filename}:")
#     # for key, value in content.items():
#     #     print(f"{key}: {value}")
#     print(content)

# print("--- %s seconds ---" % (time.time() - start_time))