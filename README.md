# PPE Violation Detection System

An AI-powered Personal Protective Equipment (PPE) detection system that analyzes uploaded images, detects people and safety equipment, identifies missing helmets or safety vests, and displays detection results through an interactive dashboard.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Detection Workflow](#detection-workflow)
6. [Detection Classes](#detection-classes)
7. [Compliance Logic](#compliance-logic)
8. [Project Structure](#project-structure)
9. [Installation](#installation)
10. [Running the Application](#running-the-application)
11. [API Endpoints](#api-endpoints)
12. [Database and Storage](#database-and-storage)
13. [Current Scope and Limitations](#current-scope-and-limitations)
14. [Future Enhancements](#future-enhancements)

---

## 1. Project Overview

The PPE Violation Detection System uses a YOLO object-detection model to identify people and Personal Protective Equipment in uploaded images.

The system detects:

- People
- Safety helmets
- Missing helmets
- Safety vests
- Missing safety vests

OpenCV processes detection results and generates annotated images with bounding boxes and labels.

A dedicated compliance service analyzes the detected classes and determines the overall compliance status.

The application consists of:

- **Streamlit:** Interactive frontend dashboard.
- **FastAPI:** Backend REST API.
- **YOLO (Ultralytics):** PPE object detection.
- **OpenCV:** Image processing and annotation.
- **SQLite:** Local storage of detection history.
- **SQLAlchemy:** Database ORM.

## 2. Features

- Upload images in JPG, JPEG, PNG, and WEBP formats.
- Detect people and PPE-related objects.
- Identify missing helmets and safety vests.
- Apply confidence thresholds to detections.
- Generate annotated images using OpenCV.
- Display detection summaries and compliance status.
- Maintain detection history.
- View previous detection results.
- Delete detection records and associated files.
- Store detection metadata in an SQLite database.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend REST API |
| Streamlit | Frontend dashboard |
| YOLO / Ultralytics | Object detection |
| OpenCV | Image processing and annotation |
| SQLAlchemy | Database ORM |
| SQLite | Local database |
| Uvicorn | ASGI application server |

## 4. System Architecture

The application follows a modular architecture that separates the frontend, backend API, AI processing, compliance logic, and data storage.

```text
                         USER
                           |
                           v
                  STREAMLIT FRONTEND
                    frontend/app.py
                           |
                     Image Upload
                           |
                           v
                    FASTAPI BACKEND
                    backend/main.py
                           |
                           v
                      API ROUTES
                   backend/api/routes.py
                           |
               +-----------+-----------+
               |                       |
               v                       v
          PPE DETECTOR             FILE STORAGE
      backend/ai/detector.py       storage/uploads/
               |                   storage/processed/
               |
               v
           YOLO MODEL
        models/ppe_model.pt
               |
               v
        DETECTION RESULTS
               |
               v
         OPENCV ANNOTATION
               |
               v
       COMPLIANCE SERVICE
 backend/services/compliance_service.py
               |
               v
        COMPLIANCE STATUS
               |
               v
         SQLITE DATABASE
 backend/database/database.py
 backend/database/models.py
               |
               v
           API RESPONSE
               |
               v
        STREAMLIT DASHBOARD
```

### Main Components

| Component | Responsibility |
|---|---|
| `frontend/app.py` | Provides the user interface and displays detection results |
| `backend/main.py` | Initializes the FastAPI application and database tables |
| `backend/api/routes.py` | Handles detection, history, deletion, and image-serving requests |
| `backend/ai/detector.py` | Loads the YOLO model, performs inference, filters detections, and annotates images |
| `backend/services/compliance_service.py` | Counts detected labels and determines compliance status |
| `backend/database/database.py` | Configures the SQLite database connection |
| `backend/database/models.py` | Defines the detection-history database model |

## 5. Detection Workflow

The system follows this sequence:

1. User uploads an image through the Streamlit dashboard.
2. Streamlit sends the image to the FastAPI backend.
3. FastAPI validates the file extension and saves the original image.
4. The PPE detector loads the YOLO model.
5. YOLO performs object detection.
6. Relevant detections are filtered using confidence thresholds.
7. OpenCV draws bounding boxes and labels.
8. The annotated image is saved in the processed directory.
9. The compliance service calculates detection counts and violation status.
10. Detection information is stored in SQLite.
11. FastAPI returns the results to Streamlit.
12. The dashboard displays the detection status, summary, annotated image, and history.

## 6. Detection Classes

The model classes are mapped to application labels as follows:

| YOLO Model Class | Application Label | Description |
|---|---|---|
| `Person` | `person` | Person detected |
| `Hardhat` | `helmet` | Safety helmet detected |
| `NO-Hardhat` | `no-helmet` | Missing helmet detected |
| `Safety Vest` | `vest` | Safety vest detected |
| `NO-Safety Vest` | `no-vest` | Missing safety vest detected |

### Confidence Thresholds

The detector uses the following configuration:

| Parameter | Value |
|---|---:|
| YOLO inference confidence | 0.15 |
| IoU threshold | 0.45 |
| Maximum detections | 100 |
| Final vest threshold | 0.15 |
| Final threshold for other classes | 0.40 |

The detector runs on CPU.

## 7. Compliance Logic

The compliance service analyzes detection labels and calculates the number of violations.

### Violation Conditions

- Every `no-helmet` detection contributes to the violation count.
- Every `no-vest` detection contributes to the violation count.

### Status Determination

```python
IF violation_count > 0:
    status = "VIOLATION DETECTED"

ELIF person_count > 0:
    status = "NO VIOLATION DETECTED"

ELSE:
    status = "NO PERSON DETECTED"
```

### Status Explanation

| Condition | Result |
|---|---|
| At least one missing-helmet or missing-vest detection | VIOLATION DETECTED |
| Person detected and no violation labels detected | NO VIOLATION DETECTED |
| No person detected | NO PERSON DETECTED |

**Important:** The current implementation evaluates detection labels and their counts independently. It does not associate a helmet or safety vest with a specific person. Therefore, the compliance result is image-level analysis, not verified individual-worker compliance.

## 8. Project Structure

```text
ppe_detection/
│
├── .streamlit/
│   └── config.toml
│
├── backend/
│   │
│   ├── main.py
│   │
│   ├── ai/
│   │   └── detector.py
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   └── __init__.py
│   │
│   └── services/
│       └── compliance_service.py
│
├── frontend/
│   └── app.py
│
├── models/
│   └── ppe_model.pt
│
├── runs/
│   └── detect/
│
├── storage/
│   ├── uploads/
│   ├── processed/
│   └── ppe_detection.db
│
├── requirements.txt
└── README.md
```

### Folder Responsibilities

| Folder | Purpose |
|---|---|
| `backend/ai/` | AI model inference and detection |
| `backend/api/` | FastAPI routes and endpoints |
| `backend/database/` | Database connection and models |
| `backend/schemas/` | API schema definitions |
| `backend/services/` | Compliance and business logic |
| `frontend/` | Streamlit application |
| `models/` | Trained YOLO model |
| `storage/uploads/` | Original uploaded images |
| `storage/processed/` | Annotated detection images |
| `runs/` | Generated YOLO detection outputs |

`.venv/` is a local Python virtual environment and is not part of the application source code.

## 9. Installation

### Prerequisites

- Python 3.10 or newer, compatible with the installed dependencies.
- pip package manager.
- Trained YOLO model file.
- Sufficient CPU and RAM for model inference.

A dedicated GPU is not required because the current detector uses CPU inference.

### Step 1: Clone the Repository

```bash
git clone https://github.com/prachikumari850/ppe_detection.git
cd ppe_detection
```

Replace `<repository-url>` with your actual Git repository URL.

### Step 2: Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Verify the YOLO Model

Make sure the trained model exists at:

```text
models/ppe_model.pt
```

The application requires this model file to perform detection.

## 10. Running the Application

The backend and frontend must run in separate terminals.

### Step 1: Start the FastAPI Backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### Step 2: Start the Streamlit Frontend

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run frontend/app.py
```

Streamlit will display the local dashboard URL in the terminal.

Open that URL in your browser.

**Note:** If the frontend uses a configured backend URL, ensure that it points to the running FastAPI server.

## 11. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API root/status |
| GET | `/api/health` | Backend health check |
| POST | `/api/detect` | Upload image and perform PPE detection |
| GET | `/api/history` | Retrieve detection history |
| DELETE | `/api/history/{record_id}` | Delete detection record and associated files |
| GET | `/processed/{filename}` | Retrieve annotated image |

### Image Detection

```http
POST /api/detect
```

The endpoint accepts an image upload using `multipart/form-data`.

Supported formats:

- JPG
- JPEG
- PNG
- WEBP

### API Documentation

FastAPI automatically provides interactive Swagger documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

## 12. Database and Storage

The application uses SQLite for storing detection records.

### Storage Locations

| Path | Stored Data |
|---|---|
| `storage/uploads/` | Original uploaded images |
| `storage/processed/` | Annotated images |
| `storage/ppe_detection.db` | Detection-history database |

### Database Information

The `detection_records` table stores information such as:

- Record ID
- Original image name
- Annotated image path
- Detection status
- Person count
- Helmet count
- Missing-helmet count
- Safety-vest count
- Missing-vest count
- Total violation count
- Creation timestamp

The SQLite database is created locally when the backend initializes its database tables.

Keep the `storage/` directory available while the application is running. Back up this directory if detection history and uploaded images need to be retained.

## 13. Current Scope and Limitations

### Implemented

- Image upload and PPE detection.
- Person, helmet, and safety-vest class detection.
- Missing-helmet and missing-vest detection.
- Confidence-based detection filtering.
- OpenCV image annotation.
- Compliance status calculation.
- Detection history.
- SQLite database storage.
- Detection record deletion.

### Not Currently Implemented

- Video upload and processing.
- Live webcam detection.
- CCTV camera integration.
- Worker tracking across frames.
- Person-to-PPE association.
- User authentication.
- Role-based access control.
- Automated alerts and notifications.

Detection accuracy depends on image quality, lighting, camera angle, object size, and the model's training data. Results should be reviewed before being used for operational safety decisions.

## 14. Future Enhancements

The following features can be considered for future development:

- Video upload and frame-by-frame PPE detection.
- Real-time webcam and CCTV monitoring.
- Person-to-PPE association for individual-worker compliance analysis.
- User authentication and role-based access control.
- Advanced analytics and reporting dashboard.
- Configurable confidence thresholds.
- Exportable violation reports.
- Automated notifications and alerts.
- Improved file validation and upload-size restrictions.
- Production deployment and containerization.

---

## Project Information

| Property | Details |
|---|---|
| Project Name | PPE Violation Detection System |
| Project Type | AI-Based PPE Detection |
| Backend | FastAPI |
| Frontend | Streamlit |
| AI Model | YOLO (Ultralytics) |
| Image Processing | OpenCV |
| ORM | SQLAlchemy |
| Database | SQLite |
| Inference Device | CPU |

**Purpose:** To automate image-based detection of PPE compliance indicators and help identify potential safety violations at work sites.
