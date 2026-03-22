# AI-Based Radiator Visual Inspection System - Implementation Guide

## 📋 Phase-by-Phase Implementation Plan

### Phase 1: Project Setup & Environment (Week 1)
- [ ] Create project structure
- [ ] Set up Python environment
- [ ] Install dependencies
- [ ] Configure dataset folder structure

### Phase 2: Dataset Preparation (Week 2-3)
- [ ] Collect radiator images (minimum 300 images, 4 views each)
- [ ] Organize images by view type
- [ ] Apply data augmentation
- [ ] Split into train/val/test (70/15/15)

### Phase 3: Data Annotation (Week 3-4)
- [ ] Annotate images with bounding boxes using Roboflow/CVAT
- [ ] Create YOLO format labels
- [ ] Validate annotations
- [ ] Generate dataset.yaml configuration

### Phase 4: Model Training (Week 4-5)
- [ ] Train YOLOv8 model
- [ ] Validate model performance
- [ ] Test on test dataset
- [ ] Fine-tune hyperparameters

### Phase 5: Inspection Logic (Week 5)
- [ ] Implement component detection rules
- [ ] Create inspection decision engine
- [ ] Define OK/NOT OK criteria
- [ ] Test with sample radiators

### Phase 6: Backend API (Week 6)
- [ ] Create FastAPI server
- [ ] Implement image upload endpoint
- [ ] Add model inference endpoint
- [ ] Return inspection results

### Phase 7: Frontend UI (Week 6-7)
- [ ] Build Streamlit dashboard OR React UI
- [ ] Real-time image preview
- [ ] Inspection results display
- [ ] Analytics dashboard

### Phase 8: Integration & Testing (Week 7-8)
- [ ] Full system testing
- [ ] Performance optimization
- [ ] Deployment preparation
- [ ] Documentation

---

## 📁 Project Directory Structure

```
radiator_ai_inspection/
├── dataset/
│   ├── images/
│   │   ├── train/
│   │   ├── val/
│   │   └── test/
│   └── labels/
│       ├── train/
│       ├── val/
│       └── test/
├── annotations/
│   ├── classes.txt
│   └── dataset.yaml
├── models/
│   ├── best.pt
│   └── last.pt
├── scripts/
│   ├── __init__.py
│   ├── dataset_preparation.py
│   ├── train_model.py
│   ├── augment_dataset.py
│   └── validate_labels.py
├── inspection/
│   ├── __init__.py
│   ├── detection.py
│   ├── inspection_logic.py
│   └── utils.py
├── api/
│   ├── __init__.py
│   ├── server.py
│   └── models.py
├── ui/
│   ├── streamlit_app.py
│   └── static/
├── config/
│   ├── config.yaml
│   └── requirements.txt
├── results/
│   ├── inspections/
│   └── logs/
└── README.md
```

---

## 🛠️ Environment Setup

### Requirements.txt

```
# Deep Learning
torch==2.0.1
torchvision==0.15.2
ultralytics==8.0.200  # YOLOv8
opencv-python==4.8.1.78
numpy==1.24.3
pandas==2.0.3

# API & Backend
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.4.2

# UI
streamlit==1.28.1
pillow==10.0.1

# Data Processing
scikit-image==0.21.0
scipy==1.11.3

# Utilities
pyyaml==6.0.1
python-dotenv==1.0.0
```

### Installation Steps

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify CUDA support (optional, for GPU training)
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🎯 Key Implementation Files

### 1. Configuration File (config/config.yaml)

```yaml
# Model Configuration
model:
  name: "yolov8m"  # nano, small, medium, large
  pretrained: true
  epochs: 100
  batch_size: 16
  img_size: 640
  device: 0  # GPU device, -1 for CPU

# Dataset Configuration
dataset:
  path: "./dataset"
  train_ratio: 0.7
  val_ratio: 0.15
  test_ratio: 0.15

# Component Classes
components:
  - fan
  - pipe
  - connector
  - drain_plug
  - rubber_grommet
  - clip
  - radiator_fin

# Inspection Rules
inspection:
  required_components:
    - fan
    - pipe
    - connector
  min_confidence: 0.5
  max_defects: 0  # 0 = must be perfect

# Output
output:
  results_dir: "./results"
  log_file: "./results/inspection.log"
```

---

## 📊 Dataset Structure Example

```
dataset/
├── images/
│   ├── train/
│   │   ├── radiator_001_front.jpg
│   │   ├── radiator_001_back.jpg
│   │   ├── radiator_002_front.jpg
│   │   └── ...
│   ├── val/
│   │   └── (images for validation)
│   └── test/
│       └── (images for testing)
└── labels/
    ├── train/
    │   ├── radiator_001_front.txt
    │   └── ...
    ├── val/
    │   └── ...
    └── test/
        └── ...
```

### YOLO Label Format Example

File: `radiator_001_front.txt`

```
0 0.5 0.5 0.3 0.4    # Class 0 (fan), centered at 50%, width 30%, height 40%
1 0.7 0.6 0.2 0.15   # Class 1 (pipe)
2 0.3 0.8 0.15 0.1   # Class 2 (connector)
```

---

## 🚀 Quick Start Code Snippets

### Script 1: Data Augmentation (scripts/augment_dataset.py)

See implementation code file...

### Script 2: Model Training (scripts/train_model.py)

See implementation code file...

### Script 3: Inspection Engine (inspection/inspection_logic.py)

See implementation code file...

### Script 4: FastAPI Backend (api/server.py)

See implementation code file...

---

## 📈 Performance Metrics to Track

1. **Model Metrics**
   - mAP (mean Average Precision)
   - Precision & Recall per class
   - Training loss & Validation loss

2. **Inspection Metrics**
   - True Positive Rate (correctly identified defects)
   - False Positive Rate (false alarms)
   - Inspection time per radiator
   - Accuracy vs manual inspection

3. **System Metrics**
   - API response time
   - Inference speed (FPS)
   - Memory usage

---

## 🔧 Troubleshooting Tips

| Issue | Solution |
|-------|----------|
| Low accuracy | More training data, data augmentation, hyperparameter tuning |
| GPU out of memory | Reduce batch size, use smaller model (nano/small) |
| Slow inference | Use GPU, reduce image size, use smaller model |
| Annotation errors | Validate labels, use multiple annotators, cross-check |
| Class imbalance | Use weighted loss, data augmentation, balanced sampling |

---

## 📚 Next Steps

1. **Choose your starting point** from the options in my question
2. I'll provide detailed code for that phase
3. We'll implement it step-by-step
4. Move to next phase once complete

---

## 🔗 Useful Resources

- YOLOv8 Docs: https://docs.ultralytics.com/
- Roboflow Annotate: https://roboflow.com/
- CVAT Annotation: https://github.com/openvinotoolkit/cvat
- FastAPI Tutorial: https://fastapi.tiangolo.com/
- Streamlit Docs: https://docs.streamlit.io/
