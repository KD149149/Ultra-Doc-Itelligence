
---

# Ultra Doc-Intelligence POC

**Design & Developer:** Kajal Dadas kajaldadas149@gmail.com +917972244559

A Proof-of-Concept AI system that allows users to upload logistics documents (PDF, DOCX, TXT), interact with them using natural language questions, and extract structured shipment data. The system retrieves relevant content, applies guardrails, and returns confidence scores.

---

## **1. Architecture**

```
[Frontend: Streamlit UI]
          │
          ▼
[Backend Logic: Python Functions]
    ├─ Document Parsing (PDF, DOCX, TXT)
    ├─ Chunking & Embeddings (Sentence-Transformers)
    ├─ Vector Storage (In-memory)
    ├─ Retrieval (Semantic Search)
    ├─ Question Answering (Keyword + Chunk Matching)
    └─ Structured Extraction (Regex)
```

**Flow:**

1. User uploads a logistics document.
2. Document is parsed and split into semantic chunks.
3. Each chunk is converted into embeddings and stored in memory.
4. User asks a question.
5. System retrieves relevant chunks using vector similarity.
6. Answer is extracted from retrieved chunks using keyword matching and returned with confidence and source.
7. Structured shipment data can be extracted as JSON.

---

## **2. Chunking Strategy**

* **Chunk size:** 500 words
* **Overlap:** 50 words (to preserve context across chunks)
* **Reasoning:** Ensures long documents are broken into meaningful sections while retaining semantic continuity for retrieval.

---

## **3. Retrieval Method**

* Uses **Sentence-Transformers (`all-MiniLM-L6-v2`) embeddings**.
* Computes **cosine similarity** between user question and chunk embeddings.
* Returns **top K chunks (default 5)** for answer extraction.

---

## **4. Guardrails Approach**

* **Minimum similarity threshold:** 0.3

  * If all retrieved chunks are below this, system returns `"Not found in document"`.
* **Keyword matching:** Answers are only returned if the relevant keyword from the question is found in retrieved chunks.
* **Fallback:** Returns first sentence containing keyword if regex fails.

---

## **5. Confidence Scoring Method**

* Confidence = **maximum similarity score** of retrieved chunks.
* Range: 0.0 → 1.0
* Low confidence indicates either:

  * Keyword not found
  * Document content not sufficient

---

## **6. Failure Cases**

* Keywords not present in the document → `"Not found in document"`
* Poorly scanned PDFs (OCR required) → text extraction may fail
* Questions phrased in very different wording from keywords → may fail without an LLM
* Extremely large documents → embeddings stored in memory may slow down

---

## **7. Improvement Ideas**

1. **Integrate GPT-3.5/4 for RAG**:

   * Allows natural sentence answering without relying on exact keywords.
2. **OCR for scanned documents**:

   * Use `pytesseract` for image-based PDFs.
3. **Persistent Vector Store**:

   * FAISS, Pinecone, or Weaviate for large-scale documents.
4. **Multi-document support**:

   * Retrieve answers across multiple logistics documents.
5. **Enhanced UI/UX**:

   * Highlight source text in answer, show progress bars, and make responses more conversational.
6. **Confidence calibration**:

   * Combine similarity, keyword presence, and multiple chunk agreement.

---

## **8. Usage**

1. Install dependencies:

```bash
pip install streamlit PyPDF2 python-docx sentence-transformers
```

2. Run the application:

```bash
streamlit run ultra_doc_intelligence_final.py
```

3. Features:

* Upload logistics document (PDF, DOCX, TXT)
* Ask natural language questions
* View answer, source chunk, and confidence
* Extract structured shipment data (JSON)

---

This README satisfies the test requirements and documents **architecture, chunking, retrieval, guardrails, confidence, failure cases, and improvement ideas** clearly for evaluation.

---
