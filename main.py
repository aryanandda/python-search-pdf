import spacy
import PyPDF2
import os
import time
start_time = time.time()

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

search_terms = {
    "Resource Interdependence": ["partnership", "collaboration", "joint venture", "mutual reliance"],
    "Joint Value Creation": ["co-development", "joint project", "community project"],
    "Stakeholder Inclusivity": ["inclusive decision-making", "stakeholder panel", "community engagement"],
    "Dynamic Stakeholder Engagement": ["strategy adaptation", "responsive strategy", "feedback loop"]
}

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        findings = {key: {} for key in search_terms.keys()}
        for page in range(len(reader.pages)):
          text = reader.pages[page].extract_text()
          doc = nlp(text)
          for sent in doc.sents:
              for category, keywords in search_terms.items():
                if any(keyword.lower() in sent.text.lower() for keyword in keywords):
                    if page + 1 in findings[category]:
                        findings[category][page+1].append(sent.text.strip().replace("\n", "")) 
                    else:
                        findings[category][page+1] = [sent.text.strip().replace("\n", "")]
    return findings

def process_documents(directory):
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory, filename)
            results[filename] = extract_text_from_pdf(file_path)
    return results

# Specify the directory containing the documents
directory = './'
results = process_documents(directory)

# Display or save the results
for filename, content in results.items():
    print(f"Results for {filename}:")
    # for key, value in content.items():
    #     print(f"{key}: {value}")
    print(content)

print("--- %s seconds ---" % (time.time() - start_time))