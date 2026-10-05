# VISIONGUARD
### Explainable Visual Fact-Checking Assistant using Multimodal Image Forensics and AI-assisted Verification

---

## 1. Overview
**VisionGuard** is an open, explainable multimodal digital forensics and visual fact-checking system. In an era saturated with generative AI images, deepfakes, cheap fakes (spliced/recompressed content), and viral misinformation memes, standard black-box detectors provide arbitrary probability scores without justification.

VisionGuard bridges this gap by combining:
1. **Low-level forensic signal processing**: Error Level Analysis (ELA), Copy-Move forgery detection with displacement vector clustering, and 2D Fourier Fast Fourier Transform (FFT) frequency spectrum analysis.
2. **Provenance & Metadata analysis**: Hardware EXIF parsing, camera sensor consistency, and editing software footprint detection.
3. **Textual fact-checking & NLP**: Optical Character Recognition (OCR), entity extraction with spaCy, and fact verification without source fabrication.
4. **Explainable Decision Engine**: Dynamically normalized score weighting with explicit verbal evidence summaries ("Why did VisionGuard reach this result?"), confidence scores, and limitations statements.

---

## 2. Key Features
- **Real Error Level Analysis (ELA)**: Computes recompression differentials against controlled JPEG compression levels, measuring standard deviation, maximum error, and anomaly ratios.
- **Copy-Move Forgery Detection**: Employs ORB/SIFT feature descriptor self-matching with spatial Euclidean distance filtering and translational displacement vector clustering.
- **2D Fourier Frequency Domain Analysis**: Analyzes high-frequency versus low-frequency spectral roll-off and highlights unnatural periodic grid spikes indicative of GAN or diffusion upsampling artifacts.
- **Transparent AI-Generation Baseline**: Evaluates chromatic entropy, Laplacian noise variance, and gradient sharpness dynamically, clearly labeled as an experimental estimate.
- **OCR & Named Entity Recognition**: Safely attempts Tesseract / EasyOCR, passing extracted text to spaCy for entity and claim segmentation.
- **No-Fabrication Fact Verification**: Verifies claims against trusted databases; if credentials or sources are unavailable, strictly returns `UNVERIFIED` rather than fabricating evidence.
- **Multi-Artifact Visual Comparator**: Interactive UI allowing investigators to switch between the original source, ELA difference map, copy-move vector map, FFT magnitude heatmap, and OCR bounding boxes.
- **Comprehensive Report Generation**: Generates structured JSON exports and professional forensic PDF reports with embedded visual artifacts and evidence tables.
- **Dedicated Demo Mode**: Allows instant presentation of precomputed forensic cases clearly labeled with `DEMO RESULT` banners.

---

## 3. Architecture
```
        +-----------------------------+
        |   React + Vite Frontend     |
        | (Dashboard, Viewer, Export) |
        +--------------+--------------+
                       | HTTP / REST
        +--------------v--------------+
        |     FastAPI Application     |
        +--------------+--------------+
                       |
       +---------------v---------------+
       |       Analysis Pipeline       |
       +---------------+---------------+
                       |
       +---------------+---------------+
       | Forensic & Verification Units |
       | - Image Preprocessing        |
       | - Metadata / EXIF            |
       | - Error Level Analysis (ELA)  |
       | - Copy-Move Detector          |
       | - 2D FFT Frequency Forensics  |
       | - AI Detection Baseline       |
       | - OCR (Tesseract / EasyOCR)   |
       | - spaCy NLP Claim Extraction  |
       | - Fact-Checking Provider      |
       +---------------+---------------+
                       |
       +---------------v---------------+
       |   Explainable Decision Engine |
       | - Dynamic Weight Normalizer   |
       | - Evidence Bullet Synthesizer |
       +---------------+---------------+
                       |
       +---------------v---------------+
       |  SQLite DB & PDF/JSON Export  |
       +-------------------------------+
```

---

## 4. Tech Stack
- **Frontend**: React 18, Vite, Lucide Icons, Modern Responsive Forensic CSS.
- **Backend API**: Python 3.13, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy.
- **Image Processing & Forensics**: OpenCV, Pillow, NumPy, SciPy/FFT.
- **NLP & Verification**: spaCy (`en_core_web_sm`), Requests.
- **Reporting**: ReportLab (PDF generation), JSON.
- **Database**: SQLite.
- **Testing**: pytest, httpx.

---

## 5. Folder Structure
```
visionguard/
│
├── backend/
│   ├── main.py                     # FastAPI application entrypoint & lifespan
│   ├── config.py                   # Central settings, paths, and size limits
│   ├── database.py                 # SQLite database engine and session
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Local environment variables
│   ├── .env.example                # Environment variables template
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_health.py        # GET /api/health
│   │   └── routes_analysis.py      # POST /api/analyze, GET status, artifacts, PDF
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── database_models.py      # SQLAlchemy AnalysisRecord table
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── analysis_schema.py      # Pydantic validation schemas
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── preprocessing.py        # Normalization, resizing, validation
│   │   ├── metadata_analysis.py    # EXIF, camera make, editor detection
│   │   ├── ela.py                  # Error Level Analysis differential
│   │   ├── copy_move.py            # Keypoint matching & vector clustering
│   │   ├── frequency_analysis.py   # 2D FFT spectrum magnitude analysis
│   │   ├── ai_detector.py          # Explainable AI generation baseline
│   │   ├── ocr.py                  # Tesseract / EasyOCR with fallback
│   │   ├── nlp.py                  # spaCy NER and claim extraction
│   │   ├── fact_checker.py         # Provider abstraction (Local / Web)
│   │   └── decision_engine.py      # Dynamic weighting & evidence synthesis
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_pipeline.py    # Sequential pipeline orchestrator
│   │   └── report_generator.py     # PDF (ReportLab) & JSON export
│   │
│   ├── uploads/                    # Secure image upload storage
│   ├── results/                    # Generated forensic image artifacts
│   ├── reports/                    # Generated PDF and JSON reports
│   └── tests/
│       ├── __init__.py
│       ├── generate_test_images.py # Synthetic test image generator
│       ├── test_backend.py         # 10 automated unit/integration tests
│       └── test_images/            # Test fixtures (ELA, copy-move, text)
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js              # Vite server & proxy configuration
│   ├── index.html
│   │
│   └── src/
│       ├── main.jsx                # React DOM entrypoint
│       ├── App.jsx                 # Top-level state & polling loop
│       ├── api/
│       │   └── api.js              # Axios backend client
│       ├── components/
│       │   ├── Navbar.jsx          # Header, health indicator & demo toggle
│       │   ├── UploadZone.jsx      # Drag & drop upload with preview
│       │   ├── AnalysisProgress.jsx# Live stage checklist & progress tracker
│       │   ├── ScoreCard.jsx       # Trust score gauge & weight breakdown
│       │   ├── ForensicCard.jsx    # Modular cards for ELA, EXIF, etc.
│       │   ├── AIDetectorCard.jsx  # Dual probability comparison bar
│       │   ├── OCRPanel.jsx        # Extracted text with one-click copy
│       │   ├── ClaimsPanel.jsx     # Claims with verdicts & evidence
│       │   ├── SuspiciousRegions.jsx # Multi-artifact visual tab viewer
│       │   └── EvidenceSummary.jsx # Synthesis bullets & PDF/JSON download
│       ├── pages/
│       │   ├── Home.jsx            # Landing page with methodology
│       │   └── Analysis.jsx        # Results dashboard
│       └── styles/
│           └── index.css           # Dark navy forensic theme
│
├── README.md
├── .gitignore
└── docker-compose.yml
```

---

## 6. Windows Setup & Run Commands

### Prerequisites
- Python 3.11, 3.12, or 3.13
- Node.js (v18+) and npm
- Windows PowerShell

### Step 1: Backend Setup
Open a terminal in the project directory:
```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests
pytest tests/test_backend.py -v

# Start the FastAPI server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Backend runs at: **`http://127.0.0.1:8000`**  
Interactive API Docs (Swagger): **`http://127.0.0.1:8000/docs`**

### Step 2: Frontend Setup
Open a second terminal:
```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm.cmd install

# Start Vite development server
npm.cmd run dev
```
Frontend runs at: **`http://localhost:5173`**

---

## 7. Environment Variables (`backend/.env`)
Create `backend/.env` using `backend/.env.example` as reference:
```env
DATABASE_URL=sqlite:///./visionguard.db
MAX_UPLOAD_SIZE_MB=10
FACT_CHECK_API_KEY=
AI_MODEL_NAME=visionguard-forensic-baseline-v1
```

---

## 8. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status check |
| `POST` | `/api/analyze` | Multipart upload for image verification |
| `GET` | `/api/analysis/{id}/status` | Polling endpoint for ongoing pipeline stage |
| `GET` | `/api/analysis/{id}` | Full forensic details and decision synthesis |
| `GET` | `/api/analysis/{id}/artifact/{filename}` | Serves visual artifacts (ELA, FFT, Copy-Move) |
| `GET` | `/api/analysis/{id}/report?format=pdf` | Exports comprehensive forensic PDF report |
| `GET` | `/api/analysis/{id}/report?format=json` | Exports complete raw JSON analysis data |
| `POST` | `/api/demo` | Loads sample precomputed demo investigation |

---

## 9. Forensic Methodology & Scientific Responsibility

### 1. Error Level Analysis (ELA)
- **Concept**: Repeated JPEG compression reduces error disparity over time. Splicing an uncompressed or differently compressed patch introduces localized high-contrast error levels.
- **Policy**: High ELA disparity indicates *recompression inconsistency*, not definitive malice.

### 2. Copy-Move Forgery Detection
- **Concept**: Uses ORB/SIFT keypoint self-matching with Euclidean spatial distance thresholds. Shift-vector clustering groups keypoints sharing identical displacement vectors.
- **Policy**: If too few keypoints exist or vectors do not cluster, returns *Insufficient evidence* rather than claiming forgery.

### 3. 2D Fast Fourier Transform (FFT)
- **Concept**: Natural camera optics exhibit continuous frequency fall-off. Periodic grid spikes often correspond to synthetic GAN or diffusion convolutional upsampling artifacts.
- **Policy**: Frequency-domain analysis is treated as supporting evidence, not independent proof.

### 4. AI-Generated Image Estimation
- **Concept**: Evaluates Laplacian high-frequency noise variance, chromatic saturation distributions, and gradient smoothness.
- **Policy**: Explicitly labeled as an *Experimental Baseline* to prevent misrepresentation.

### 5. Fact Verification & Zero Hallucination
- **Concept**: Extracts text and parses entities with spaCy. Verifies against ground-truth benchmarks or Google Fact Check API.
- **Policy**: If no source corroborates the assertion, the verdict is strictly **`UNVERIFIED`**, never fabricated.

---

## 10. Automated Testing
Run the test suite with:
```powershell
.\backend\.venv\Scripts\pytest.exe backend\tests\test_backend.py -v
```
All 10 test cases verify:
- Health check endpoint
- File validation & size restrictions
- EXIF extraction & stripped metadata resilience
- Real Error Level Analysis calculation
- Copy-move feature matching
- 2D FFT frequency spectrum generation
- AI detector baseline functionality
- Transparent dynamic weight normalization in Decision Engine
- End-to-end pipeline execution & PDF generation
- Demo mode endpoint compliance

---

## 11. Known Limitations & Future Improvements
1. **OCR Dependencies**: On systems without Tesseract installed in PATH, OCR gracefully degrades to `unavailable` without crashing the pipeline. Installing Tesseract-OCR binary enables full text extraction.
2. **Deep Learning AI Models**: For production deployments, heavy vision transformers (e.g. CLIP-based or ResNet-based AI classifiers) can be plugged into `modules/ai_detector.py`.
3. **Fact Verification API**: Live web search requires a Google Fact Check API key configured in `.env`.
