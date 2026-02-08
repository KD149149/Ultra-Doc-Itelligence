# ultra_doc_intelligence_final.py
"""
Ultra Doc-Intelligence POC
Design & Developer: Kajal Dadas
Email: kajaldadas149@gmail.com
Phone: 7972244559
"""

import streamlit as st
import tempfile
import re
from PyPDF2 import PdfReader
import docx
from sentence_transformers import SentenceTransformer, util
import numpy as np

# ----------------------------
# Initialize embeddings model
# ----------------------------
MODEL = SentenceTransformer('all-MiniLM-L6-v2')

# ----------------------------
# Streamlit session state init
# ----------------------------
if 'document_text' not in st.session_state:
    st.session_state.document_text = ""
if 'chunks' not in st.session_state:
    st.session_state.chunks = []
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None

# ----------------------------
# Helper functions
# ----------------------------
def parse_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def parse_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def parse_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def parse_file(file):
    ext = file.name.split('.')[-1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp:
        tmp.write(file.getbuffer())
        tmp_path = tmp.name
    if ext == "pdf":
        return parse_pdf(tmp_path)
    elif ext == "docx":
        return parse_docx(tmp_path)
    elif ext == "txt":
        return parse_txt(tmp_path)
    else:
        raise ValueError("Unsupported file type")

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

def store_chunks(chunks):
    st.session_state.chunks = chunks
    st.session_state.embeddings = MODEL.encode(chunks, convert_to_tensor=True)

def retrieve_chunks(question, top_k=5):
    q_emb = MODEL.encode(question, convert_to_tensor=True)
    sims = util.pytorch_cos_sim(q_emb, st.session_state.embeddings)[0].cpu().numpy()
    idxs = np.argsort(-sims)[:top_k]
    retrieved = [st.session_state.chunks[i] for i in idxs]
    scores = [float(sims[i]) for i in idxs]
    return retrieved, scores

# Map question keywords to field regex patterns
FIELD_PATTERNS = {
    "shipment_id": r"Shipment[_ ]?ID[:\s]*(\w+)",
    "shipper": r"Shipper[:\s]*(.+)",
    "consignee": r"Consignee[:\s]*(.+)",
    "pickup": r"Pickup[:\s]*(.+)",
    "delivery": r"Delivery[:\s]*(.+)",
    "equipment": r"Equipment[:\s]*(\w+)",
    "mode": r"Mode[:\s]*(\w+)",
    "rate": r"Rate[:\s]*([\d\.]+)",
    "currency": r"Currency[:\s]*(\w+)",
    "weight": r"Weight[:\s]*([\d\.]+)",
    "carrier": r"Carrier[:\s]*(.+)"
}

def find_answer_in_text(question, text):
    question_lower = question.lower()
    for keyword, pattern in FIELD_PATTERNS.items():
        if keyword in question_lower:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"The {keyword.replace('_',' ')} is {match.group(1).strip()}."
    # fallback: return first sentence containing keyword
    for keyword in FIELD_PATTERNS:
        if keyword in question_lower:
            sentences = re.split(r'[.\n]', text)
            for s in sentences:
                if keyword in s.lower():
                    return s.strip()
    return None

def ask_question(question):
    if not st.session_state.chunks:
        return {"answer": "Upload a document first", "confidence": 0.0, "source": None}
    retrieved_chunks, scores = retrieve_chunks(question)
    # Lowered guardrail threshold to 0.3 so we don't miss answers
    if not retrieved_chunks or max(scores) < 0.3:
        return {"answer": "Not found in document", "confidence": 0.0, "source": None}
    # Search for answer in retrieved chunks
    for chunk in retrieved_chunks:
        answer = find_answer_in_text(question, chunk)
        if answer:
            confidence = float(max(scores))
            return {"answer": answer, "confidence": confidence, "source": chunk}
    # fallback
    return {"answer": "Not found in document", "confidence": 0.0, "source": None}

# Structured extraction
def extract_field(text, field_name):
    pattern = FIELD_PATTERNS.get(field_name.lower())
    if not pattern:
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None

def extract_shipment_data(text):
    return {f: extract_field(text, f) for f in FIELD_PATTERNS}

# ----------------------------
# Streamlit UI
# ----------------------------
st.markdown("<h5 style='text-align: center; color: gray;'>Design & Developed by Kajal Dadas</h5>", unsafe_allow_html=True)
st.title("Ultra Doc-Intelligence POC")

uploaded_file = st.file_uploader("Upload a logistics document", type=['pdf','docx','txt'])

if uploaded_file:
    st.session_state.document_text = parse_file(uploaded_file)
    chunks = chunk_text(st.session_state.document_text)
    store_chunks(chunks)
    st.success(f"Document uploaded and processed. Total chunks: {len(chunks)}")

question = st.text_input("Ask a question about the document:")

if question:
    result = ask_question(question)
    st.write("Answer:", result["answer"])
    st.write("Confidence:", result["confidence"])
    st.write("Source:", result["source"])

if st.button("Extract structured shipment data"):
    if st.session_state.document_text:
        data = extract_shipment_data(st.session_state.document_text)
        st.json(data)
    else:
        st.write("Upload a document first")
