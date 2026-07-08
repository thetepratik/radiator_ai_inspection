# 🚀 Radiator Inspection System - Setup Guide

## 📋 Table of Contents
1. Prerequisites
2. Environment Setup
3. Project Structure Creation
4. Dataset Preparation
5. Model Training
6. Running the System
7. Troubleshooting

---

## 1️⃣ Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.9 or higher
- **RAM**: Minimum 16GB (32GB recommended)
- **GPU**: NVIDIA GPU with CUDA support (optional but recommended)

### Check Python Installation
```bash
python --version
pip --version
```

### NVIDIA GPU Setup (Optional but Recommended)
```bash
# Install CUDA Toolkit 11.8
# Download from: https://developer.nvidia.com/cuda-11-8-0-download-wizard

# Install cuDNN
# Download from: https://developer.nvidia.com/cudnn

# Verify GPU support
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 2️⃣ Environment Setup

### Step 1: Clone or Create Project Folder
```bash
mkdir radiator_ai_inspection
cd radiator_ai_inspection
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Upgrade pip
```bash
pip install --upgrade pip
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Verify Installation
```bash
python -c "
import torch
import cv2
import ultralytics
import fastapi
import streamlit
print('✓ All packages installed successfully!')
print(f'✓ PyTorch version: {torch.__version__}')
print(f'✓ CUDA available: {torch.cuda.is_available()}')
"
```

---

## 3️⃣ Project Structure Creation

### Create Folders
```bash
mkdir -p dataset/images/{train,val,test}
mkdir -p dataset/labels/{train,val,test}
mkdir -p models
mkdir -p results/inspections
mkdir -p config
mkdir -p api
mkdir -p ui
mkdir -p inspection
mkdir -p scripts
mkdir -p annotations
```

### Copy Files
Place these files in the project root:
- `augment_dataset.py` → scripts/
- `train_model.py` → scripts/
- `inspection_logic.py` → inspection/
- `server.py` → api/
- `streamlit_app.py` → ui/
- `requirements.txt` → root/
- `config.yaml` → config/

---

## 4️⃣ Dataset Preparation

### 4.1 Collect Radiator Images

**Image Requirements:**
- Minimum 300 original images
- Multiple views: front, back, side, top
- High quality (5MP minimum)
- Well-lit, clear images
- Consistent background

**Recommended Collection:**
```
Front View: 80 images
Back View: 80 images
Side View: 80 images
Top View: 60 images
Total: ~300 images
```

### 4.2 Organize Images

```
dataset/images/
├── train/
│   ├── radiator_001_front.jpg
│   ├── radiator_001_back.jpg
│   ├── radiator_002_front.jpg
│   └── ... (70% of all images)
├── val/
│   └── ... (15% of all images)
└── test/
    └── ... (15% of all images)
```

### 4.3 Annotate Images

**Using Roboflow (Recommended):**

1. Sign up at https://roboflow.com/
2. Create new project
3. Upload images to Roboflow
4. Annotate bounding boxes for each component:
   - fan
   - pipe
   - connector
   - drain_plug
   - rubber_grommet
   - clip
   - radiator_fin
5. Download annotations in YOLO format
6. Extract to `dataset/labels/`

**Alternative: Using CVAT**

1. Install CVAT: https://github.com/openvinotoolkit/cvat
2. Create annotation project
3. Draw bounding boxes around components
4. Export as YOLO format

### 4.4 Label Format Validation

Each image should have a corresponding `.txt` file:

```
radiator_001_front.jpg
radiator_001_front.txt
```

Label format (YOLO):
```
<class_id> <x_center> <y_center> <width> <height>
0 0.5 0.5 0.3 0.4
1 0.7 0.6 0.2 0.15
2 0.3 0.8 0.15 0.1
```

**Validate Labels:**
```bash
python scripts/validate_labels.py
```

---

## 5️⃣ Data Augmentation

Expand dataset 3x using augmentation:

```bash
python scripts/augment_dataset.py
```

This will:
- Rotate images (±15°)
- Adjust brightness/contrast
- Add noise and blur
- Flip images
- Create 3 variations per original image
- Generate corresponding labels

**Result:** ~300 → ~1200 training images

---

## 6️⃣ Model Training

### Step 1: Create Configuration
Edit `config/config.yaml`:

```yaml
model:
  name: "yolov8m"  # Options: nano, small, medium, large
  epochs: 100
  batch_size: 16
  img_size: 640
  device: 0  # GPU device ID, or -1 for CPU

dataset:
  path: "./dataset"
  
components:
  - fan
  - pipe
  - connector
  - drain_plug
  - rubber_grommet
  - clip
  - radiator_fin

inspection:
  required_components:
    - fan
    - pipe
    - connector
  min_confidence: 0.5
```

### Step 2: Train Model
```bash
python scripts/train_model.py
```

**Training Output:**
- `models/radiator_detector/weights/best.pt` - Best model
- `models/radiator_detector/weights/last.pt` - Last checkpoint
- Training plots and metrics

**Expected Time:**
- GPU (RTX 3060): 1-2 hours
- GPU (RTX 4090): 30-45 minutes
- CPU: 8-12 hours

### Step 3: Monitor Training
```bash
# TensorBoard (if available)
tensorboard --logdir=models/radiator_detector/runs
```

### Step 4: Validate & Test
```bash
# The training script includes validation
# Test results saved in: runs/detect/predict/
```

---

## 7️⃣ Running the System

### 7.1 Start Backend API

```bash
# Terminal 1
python api/server.py

# Or with custom settings
uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 7.2 Start Frontend UI

```bash
# Terminal 2
streamlit run ui/streamlit_app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
Network URL: http://XXX.XXX.XXX.XXX:8501
```

### 7.3 Access the System

1. **Web Interface**: http://localhost:8501
2. **API Documentation**: http://localhost:8000/docs
3. **API (Swagger)**: http://localhost:8000/redoc

### 7.4 Test Single Inspection

```bash
curl -X POST "http://localhost:8000/inspect" \
  -H "accept: application/json" \
  -F "file=@radiator_sample.jpg"
```

---

## 🔍 Key Workflow

### 1. Image Upload
→ User uploads radiator image via UI

### 2. API Processing
→ Image sent to FastAPI backend
→ Image validated and processed

### 3. Model Inference
→ YOLO model detects components
→ Extracts bounding boxes and confidence scores

### 4. Inspection Logic
→ Applies business rules
→ Checks component presence
→ Verifies installation rules
→ Checks component condition

### 5. Result Generation
→ Generates OK/NOT OK decision
→ Creates detailed report
→ Returns results to frontend

### 6. Display & Storage
→ Results displayed in UI
→ Results saved to JSON
→ Statistics updated

---

## 📊 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/inspect` | Single image inspection |
| POST | `/inspect/batch` | Batch multiple images |
| GET | `/results` | Get recent results |
| GET | `/results/{id}` | Get specific result |
| GET | `/statistics` | Get system statistics |
| GET | `/health` | Health check |
| GET | `/model/info` | Model information |

---

## 🐛 Troubleshooting

### Issue: CUDA/GPU Not Found
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False, try CPU mode
# Edit config.yaml: device: -1
```

### Issue: Model Not Loading
```bash
# Check model path
ls models/radiator_detector/weights/

# Ensure you've trained the model first
python scripts/train_model.py
```

### Issue: API Connection Error
```bash
# Verify API is running
curl http://localhost:8000/health

# Check port 8000 is available
netstat -an | grep 8000
```

### Issue: Low Accuracy
- Collect more images (aim for 500+)
- Improve annotation quality
- Increase training epochs (150-200)
- Use data augmentation
- Try larger model: `yolov8l` instead of `yolov8m`

### Issue: Out of Memory
```python
# In config.yaml, reduce batch size
batch_size: 8  # From 16

# Or use smaller model
name: "yolov8s"  # From yolov8m
```

### Issue: Slow Inference
- Use GPU instead of CPU
- Reduce image size (from 640 to 416)
- Use smaller model: `yolov8n` (nano)

---

## 📈 Performance Optimization

### For Faster Training
```yaml
# config.yaml
batch_size: 32  # Increase if GPU supports
img_size: 416   # Reduce from 640
epochs: 50      # Start with fewer epochs
```

### For Faster Inference
```yaml
# Smaller model
name: "yolov8n"  # Nano (fastest)
# Or reduce image size in API
```

### For Better Accuracy
```yaml
# Larger model + more data
name: "yolov8l"  # Large model
epochs: 200
batch_size: 16
```

---

## 📚 Next Steps

1. **Collect Dataset** (Week 1-2)
   - Minimum 300 images
   - Multiple views
   - Well-lit, clear quality

2. **Annotate Images** (Week 2-3)
   - Use Roboflow or CVAT
   - Double-check all labels
   - Maintain consistency

3. **Augment & Train** (Week 3-4)
   - Run augmentation
   - Train model (50-100 epochs)
   - Validate on test set

4. **Deploy System** (Week 4)
   - Start API server
   - Launch Streamlit UI
   - Test with sample radiators

5. **Fine-tune & Deploy** (Week 5+)
   - Gather more data
   - Improve inspection rules
   - Deploy to production

---

## 🔗 Additional Resources

- **YOLO Docs**: https://docs.ultralytics.com/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **Roboflow**: https://roboflow.com/
- **CVAT**: https://cvat.ai/

---

## 💡 Tips for Success

✅ Start with clean, well-organized dataset
✅ Invest time in accurate annotations
✅ Use data augmentation to expand dataset
✅ Monitor training metrics and loss curves
✅ Validate frequently on test set
✅ Fine-tune hyperparameters based on results
✅ Keep inspection rules updated
✅ Track system performance metrics

---

**Happy inspecting! 🎉**
