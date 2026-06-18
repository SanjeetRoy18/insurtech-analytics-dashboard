# Corporate Insurance & Claims Analytics Portal

An automated, full-stack analytics dashboard built for tracking corporate employee benefits, insurance premiums, and wellness stipend utilization. This project demonstrates a production-grade decoupled architecture separating data processing pipelines from interactive user interface frameworks.

## 📐 System Architecture

The application is structured into three clean, independent architectural tiers:

1. **Data Layer:** A structured 100-row spreadsheet containing employee demographics, insurance premium tiers, and year-to-date claim details.
2. **Backend Processing API (Python/Flask):** Ingests raw data using `Pandas`, handles analytical math transformations (loss ratios, binned distribution frequencies), and serves calculated objects as a JSON API endpoint.
3. **AI-Enhanced Engine (RAG & LLM):** Utilizes a Retrieval-Augmented Generation pipeline to ground AI responses in insurance and claims datasets, enabling natural language querying of complex policy data.
4. **Frontend Presentation (HTML/CSS/JS):** An asynchronous UI dashboard that consumes the backend API data feed dynamically via `Fetch API` and renders interactive charts using `Chart.js`.

---

## 📁 Repository Structure

```text
Xceedance/
├── data/
│   └── insurance_data.csv          # Local raw dataset storage
├── backend/
│   ├── app.py                      # Flask API server with RAG/LLM endpoints
│   ├── rag_engine.py               # Vector search & LLM integration logic
│   └── requirements.txt            # Python environment dependencies
├── frontend/
│   ├── index.html                  # Dashboard layout skeleton
│   ├── styles.css                  # Corporate styling configurations
│   └── app.js                      # Asynchronous API fetcher & Chart.js logic
├── notebooks/
│   └── exploration.ipynb           # Initial Jupyter prototyping sandbox
└── README.md                       # Execution documentation
