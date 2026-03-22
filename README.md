# 🤖 Radiator AI Visual Inspection System

> AI-Powered Automated Quality Control for Automotive Radiators

![Status](https://img.shields.io/badge/Status-Ready%20to%20Build-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Project Overview

This is a **complete, production-ready** AI-based visual inspection system for automotive radiators. It uses **YOLOv8** deep learning model to automatically detect radiator components and determine quality status (OK/NOT OK).

### Key Features
✅ Automatic component detection (7 types)
✅ Real-time inspection processing
✅ Detailed quality reports
✅ REST API backend
✅ Web-based user interface
✅ Batch processing support
✅ Inspection history & analytics

---

## 🚀 Quick Start (5 Steps)

### Step 1: Setup Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Organize Images
```bash
python scripts/organize_dataset.py
# Enter path to your 300 images folder
# Select organization method: 1 (by view)
```

### Step 3: Annotate Images
```bash
pip install label-studio
label-studio
# Open http://localhost:8080
# Upload images and draw bounding boxes around components
# Read: docs/ANNOTATION_GUIDE.md for detailed instructions
```

### Step 4: Validate & Augment
```bash
python scripts/validate_labels.py
python scripts/augment_dataset.py
```

### Step 5: Train Model
```bash
python scripts/train_model.py
# Takes 1-3 hours with GPU, ~10 hours with CPU
```

### Step 6: Deploy System
```bash
# Terminal 1: Start API
python api/server.py

# Terminal 2: Start Web UI
streamlit run ui/streamlit_app.py

# Open: http://localhost:8501
```

---

## 📁 Project Structure

```
radiator_ai_inspection/
│
├── 📄 README.md (THIS FILE)
├── 📋 START_HERE.md ⭐ Read this first!
├── 📦 requirements.txt (Python dependencies)
├── ⚙️ quick_start.py (Interactive workflow guide)
│
├── 📂 config/
│   └── config.yaml (All system configuration)
│
├── 📂 dataset/
│   ├── images/
│   │   ├── train/ (70% of images)
│   │   ├── val/ (15% of images)
│   │   └── test/ (15% of images)
│   ├── labels/
│   │   ├── train/ (training labels)
│   │   ├── val/ (validation labels)
│   │   └── test/ (test labels)
│   └── dataset.yaml (YOLO dataset config)
│
├── 📂 scripts/
│   ├── organize_dataset.py (Organize images into train/val/test)
│   ├── train_model.py (Train YOLOv8 model)
│   ├── augment_dataset.py (Expand dataset 3x)
│   └── validate_labels.py (Check annotation format)
│
├── 📂 api/
│   └── server.py (FastAPI REST API backend)
│
├── 📂 ui/
│   └── streamlit_app.py (Streamlit web interface)
│
├── 📂 inspection/
│   ├── __init__.py
│   └── inspection_logic.py (OK/NOT OK decision logic)
│
├── 📂 models/
│   └── radiator_detector/
│       ├── weights/
│       │   └── best.pt (Trained model file - generated after training)
│       └── runs/ (Training logs and metrics)
│
├── 📂 results/
│   ├── inspections/ (JSON inspection results)
│   └── logs/ (System logs)
│
├── 📂 annotations/
│   ├── classes.txt (Component class names)
│   └── dataset.yaml (YOLO format config)
│
├── 📂 docs/
│   ├── START_HERE.md ⭐ Your situation & next steps
│   ├── YOUR_IMPLEMENTATION_PLAN.md (5-7 day timeline)
│   ├── ANNOTATION_GUIDE.md (How to annotate)
│   ├── SETUP_GUIDE.md (Technical details)
│   ├── RADIATOR_SYSTEM_GUIDE.md (System architecture)
│   ├── PROJECT_SUMMARY.md (Overview)
│   └── COMPLETE_PACKAGE_SUMMARY.md (Detailed checklist)
│
└── .gitignore (Git ignore rules)
```

---

## 📖 Documentation Guide

### Read First
1. **START_HERE.md** - Your situation and quick start
2. **docs/YOUR_IMPLEMENTATION_PLAN.md** - Detailed 5-7 day timeline

### During Implementation
3. **docs/ANNOTATION_GUIDE.md** - How to annotate images (CRITICAL)
4. **docs/SETUP_GUIDE.md** - Technical troubleshooting

### Reference
5. **docs/RADIATOR_SYSTEM_GUIDE.md** - How system works
6. **docs/PROJECT_SUMMARY.md** - Complete overview

---

## 🔄 Component Detection

The system detects **7 radiator components**:

| Component | Min | Max | Required |
|-----------|-----|-----|----------|
| **Fan** | 1 | 1 | ✓ |
| **Pipe** | 2 | 4 | ✓ |
| **Connector** | 1 | 2 | ✓ |
| **Drain Plug** | 1 | 1 | ✓ |
| **Rubber Grommet** | 3 | 5 | ✓ |
| **Clip** | 4 | 8 | ✓ |
| **Radiator Fin** | - | - | Optional |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **AI Model** | YOLOv8 (Ultralytics) |
| **Computer Vision** | OpenCV |
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **Data Processing** | NumPy, Pandas |
| **Framework** | PyTorch |

---

## 📋 System Architecture

```
┌──────────────────────────────┐
│   Web Interface (Streamlit)   │
│  http://localhost:8501        │
└───────────┬──────────────────┘
            │ HTTP Requests
            ↓
┌──────────────────────────────┐
│   FastAPI REST Backend        │
│  http://localhost:8000        │
│  /inspect, /results, /stats   │
└───────────┬──────────────────┘
            │
      ┌─────┴──────┐
      ↓            ↓
┌────────────┐  ┌──────────────┐
│  YOLOv8    │  │ Inspection   │
│  Detection │  │ Logic Engine │
│  Model     │  │ (OK/NOT OK)  │
└────────────┘  └──────────────┘
      │            │
      └─────┬──────┘
            ↓
     ┌─────────────┐
     │  JSON       │
     │  Results    │
     │  Storage    │
     └─────────────┘
```

---

## 📊 7-Day Implementation Timeline

```
DAY 1 (Today)
├─ Setup Python environment
├─ Install dependencies
└─ Organize 300 images into train/val/test
   ✓ Preparation complete

DAYS 2-4 (Annotation)
├─ Use Label Studio or CVAT
├─ Annotate all 300 images with bounding boxes
└─ Export labels in YOLO format
   ✓ Labeled dataset ready

DAY 5 (Validation)
├─ Validate annotation format
└─ Augment dataset (300 → ~900 images)
   ✓ Preparation complete

DAY 6 (Training)
├─ Train YOLOv8 model
└─ Validate performance
   ✓ Model trained (1-3 hours with GPU)

DAY 7 (Deployment)
├─ Start API server
├─ Start web interface
└─ Test with sample images
   ✓ System ready! 🚀
```

---

## ⚡ Quick Commands Reference

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/organize_dataset.py
```

### Annotation
```bash
pip install label-studio
label-studio
# Open http://localhost:8080
```

### Data Preparation
```bash
python scripts/validate_labels.py
python scripts/augment_dataset.py
```

### Training
```bash
python scripts/train_model.py
```

### Deployment
```bash
# Terminal 1
python api/server.py

# Terminal 2
streamlit run ui/streamlit_app.py
```

---

## 🔍 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/inspect` | Single image inspection |
| POST | `/inspect/batch` | Process multiple images |
| GET | `/results` | Get recent inspection results |
| GET | `/results/{id}` | Get specific result details |
| GET | `/statistics` | Get system statistics |
| GET | `/health` | Health check |
| GET | `/model/info` | Model information |

**API Documentation:** http://localhost:8000/docs

---

## 💻 System Requirements

### Minimum
- Python 3.9+
- 16 GB RAM
- 512 GB SSD
- Internet connection

### Recommended
- Python 3.9+
- 32 GB RAM
- 1 TB SSD
- NVIDIA GPU (RTX 3060+)
- CUDA 11.8+
- cuDNN
- Internet connection

### Without GPU
- Everything works
- Training takes 8+ hours instead of 1-3 hours

---

## 📈 Expected Results

After 7 days of following this plan:

✅ **AI Model**
- Trained on 900+ images
- Detects 7 component types
- 85-95% accuracy (depends on annotation quality)

✅ **REST API**
- FastAPI backend with full functionality
- Image upload & inference
- Batch processing
- Results storage & retrieval
- Statistics tracking

✅ **Web Interface**
- Streamlit dashboard
- Single & batch inspection
- Results history viewer
- Analytics dashboard
- Real-time processing

✅ **Quality Control System**
- Automatic OK/NOT OK decisions
- Component presence verification
- Installation rule checking
- Detailed inspection reports

---

## 🔧 Configuration

All system settings are in **`config/config.yaml`**:

```yaml
model:
  name: "yolov8m"      # Model size
  epochs: 100          # Training epochs
  batch_size: 16       # Batch size
  device: 0            # GPU device (0) or CPU (-1)

inspection:
  required_components: [fan, pipe, connector]
  min_confidence: 0.5
  max_defects: 0
```

See `config/config.yaml` for all available options.

---

## 📝 Key Files Explained

| File | Purpose |
|------|---------|
| `scripts/organize_dataset.py` | Organize 300 images into train/val/test |
| `scripts/train_model.py` | Train YOLOv8 detection model |
| `scripts/augment_dataset.py` | Expand dataset 3x with augmentation |
| `scripts/validate_labels.py` | Validate annotation format |
| `api/server.py` | FastAPI REST API server |
| `ui/streamlit_app.py` | Web interface for users |
| `inspection/inspection_logic.py` | Business logic for decisions |
| `config/config.yaml` | System configuration |
| `requirements.txt` | Python dependencies |

---

## 🚀 Your Next Actions

### Right Now
1. Read **START_HERE.md** (10 minutes)
2. Read **docs/YOUR_IMPLEMENTATION_PLAN.md** (20 minutes)

### Today
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/organize_dataset.py
```

### Days 2-4
- Read **docs/ANNOTATION_GUIDE.md**
- Annotate all 300 images using Label Studio
- Export labels in YOLO format

### Day 5
```bash
python scripts/validate_labels.py
python scripts/augment_dataset.py
```

### Day 6
```bash
python scripts/train_model.py
```

### Day 7
```bash
python api/server.py  # Terminal 1
streamlit run ui/streamlit_app.py  # Terminal 2
```

---

## 📞 Help & Support

### If You Get Stuck
1. Check **START_HERE.md** for quick answers
2. Read **docs/YOUR_IMPLEMENTATION_PLAN.md** for detailed timeline
3. Check **docs/ANNOTATION_GUIDE.md** for annotation issues
4. See **docs/SETUP_GUIDE.md** for technical problems

### Common Issues
| Problem | Solution |
|---------|----------|
| Python not found | Install Python 3.9+ from python.org |
| Dependencies fail | Run `pip install --upgrade pip` first |
| Port in use | Change port in api/server.py or kill process |
| CUDA not found | Don't need GPU - model works on CPU (just slower) |
| Annotation confused | Read docs/ANNOTATION_GUIDE.md completely |

---

## 🎓 What You'll Learn

By completing this project, you'll understand:
- ✓ Data preparation for AI training
- ✓ YOLO object detection architecture
- ✓ Deep learning model training
- ✓ REST API design with FastAPI
- ✓ Web application development with Streamlit
- ✓ AI implementation in manufacturing

---

## 📊 Project Statistics

- **Python Scripts:** 7 files
- **Documentation:** 7 comprehensive guides
- **Configuration:** YAML-based setup
- **Dependencies:** 20+ packages
- **Components to Detect:** 7 types
- **Expected Training Data:** 900+ images
- **Expected Model Accuracy:** 85-95%
- **Expected Timeline:** 5-7 days

---

## ✨ Features

### Data Preparation
- Automatic image organization
- Dataset validation
- Data augmentation (3x expansion)
- Train/val/test splitting

### Model Training
- YOLOv8 integration
- GPU acceleration support
- Automatic validation
- Early stopping
- Model export (ONNX, TFLite)

### Inspection System
- Component detection
- Installation rule verification
- Condition checking
- Batch processing
- History tracking

### Web Interface
- Image upload
- Real-time results
- Batch processing
- Results history
- Analytics dashboard

### REST API
- Single image inspection
- Batch processing
- Result retrieval
- Statistics tracking
- Auto-documentation

---

## 📜 License

This project is provided as-is for educational and commercial use.

---

## 🎉 You're Ready!

You have everything needed to build a production-grade AI inspection system. 

**Start by reading:** `START_HERE.md`

**Timeline:** 5-7 days to working system

**Difficulty:** Medium (hardest part is annotation)

**Support:** Complete documentation included

---

## 📚 Additional Resources

- **YOLOv8 Docs:** https://docs.ultralytics.com/
- **FastAPI:** https://fastapi.tiangolo.com/
- **Streamlit:** https://docs.streamlit.io/
- **Label Studio:** https://labelstud.io/
- **CVAT:** https://cvat.ai/

---

**Good luck! You've got everything you need to succeed! 💪**

For questions, refer to the documentation files in the `docs/` folder.

Last updated: January 2024 | Status: Ready to Build
