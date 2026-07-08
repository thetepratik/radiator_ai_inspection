# 📋 Annotation Guide - Local Tools for 300 Radiator Images

## 🎯 Overview

You need to create **bounding boxes** around 7 component types in 300 images. This creates the labeled dataset needed to train the AI model.

**Time required:** 2-4 days (depending on experience and tool)

---

## 🛠️ Tool Comparison

| Tool | Speed | Setup | Cost | Best For |
|------|-------|-------|------|----------|
| **Label Studio** | ⚡⚡⚡ Fast | 5 min | Free | Local, quick annotation |
| **CVAT** | ⚡⚡ Medium | 15 min | Free | Professional, advanced |
| **Roboflow** | ⚡ Slow | 5 min | Free | Cloud, sharing annotations |

**Recommendation:** Use **Label Studio** for fastest local annotation

---

## ✅ Method 1: Label Studio (RECOMMENDED - Fastest)

### Installation (5 minutes)

```bash
# Install Label Studio
pip install label-studio

# Start Label Studio
label-studio
```

Then open: **http://localhost:8080**

### Step-by-Step Guide

#### Step 1: Create Project
1. Click **"Create"**
2. Project name: `radiator-inspection`
3. Click **"Data Import"** → **"File Upload"**
4. Upload your **dataset/images/** folder (all 300 images)
5. Click **"Proceed"**

#### Step 2: Configure Labeling Template
1. Click **"Labeling Setup"**
2. Choose **"Object Detection"**
3. Add 7 labels (press + button for each):

```
✓ fan
✓ pipe
✓ connector
✓ drain_plug
✓ rubber_grommet
✓ clip
✓ radiator_fin
```

4. Click **"Save"**

#### Step 3: Start Annotating
1. Click **"Label"**
2. For each image:
   - Select component type from list
   - **Click and drag** to draw bounding box around component
   - Repeat for all components in image
   - Click **"Submit"** when done

### Drawing Tips
- ✅ Draw **tight boxes** around each component
- ✅ Don't include background
- ✅ Be **consistent** across images
- ❌ Don't make boxes too large
- ❌ Don't miss any components

### Speed Tips
- Use **keyboard shortcuts**: 
  - Press number (1-7) to select label quickly
  - Press **Space** to submit
- Do images in batches of 50
- Take breaks every 50 images

### Export Labels (CRITICAL)
1. Click **"Export"**
2. Select format: **YOLO**
3. Click **"Export"**
4. You'll get a ZIP file

**Extract to your project:**
```bash
# After exporting and extracting
unzip label-studio-export.zip

# Copy to your dataset
cp -r images/* dataset/images/
cp -r labels/* dataset/labels/
```

---

## ✅ Method 2: CVAT (More Professional)

### Installation (15 minutes)

**Option A: Docker (Easier)**
```bash
# Install Docker first: https://www.docker.com/products/docker-desktop

# Run CVAT in Docker
docker run -d \
  -p 8080:8080 \
  -p 8443:8443 \
  --name cvat \
  openvino/cvat:latest

# Wait 1-2 minutes for startup
# Open: http://localhost:8080
```

**Option B: Local Installation**
```bash
# Clone CVAT
git clone https://github.com/openvinotoolkit/cvat.git
cd cvat

# Install dependencies
pip install -r requirements.txt

# Start server
python manage.py runserver
```

### Step-by-Step Guide

#### Step 1: Create Task
1. Click **"Create Task"**
2. Name: `radiator-inspection`
3. Project: Create new → `radiator-inspection`
4. Label schema: Select **"Object detection"**

#### Step 2: Add Labels
Click **"+ Label"** for each component:
- fan
- pipe
- connector
- drain_plug
- rubber_grommet
- clip
- radiator_fin

#### Step 3: Upload Images
1. Click **"Select Files"**
2. Choose all 300 images from dataset/images/
3. Click **"Submit & Open"**

#### Step 4: Annotate
1. Select **Rectangle tool** (or press R)
2. Click and drag to draw boxes
3. Select label from dropdown
4. Repeat for all components
5. Save frequently (Ctrl+S)

#### Step 5: Export
1. Click **"Menu"** → **"Export"**
2. Format: **YOLO 1.1**
3. Click **"OK"**
4. Download ZIP file

**Extract labels:**
```bash
unzip cvat-export.zip
cp -r obj_train_data/obj/* dataset/labels/train/
cp -r obj_train_data/obj/* dataset/labels/val/
cp -r obj_train_data/obj/* dataset/labels/test/
```

---

## ⚡ Method 3: Roboflow (Easiest, but Cloud-based)

### Setup
1. Go to **https://roboflow.com**
2. Sign up (free tier available)
3. Create new project: `radiator-inspection`
4. Upload all 300 images
5. Annotate in browser
6. Export as YOLO format

**Pros:**
- Easiest interface
- Web-based (no installation)
- Good for learning

**Cons:**
- Slower (uploads/downloads)
- Internet dependent
- Less local control

---

## 📝 YOLO Format Explanation

After annotation, you'll have `.txt` label files like:

**Example: radiator_001_front.txt**
```
0 0.5 0.45 0.25 0.35
1 0.2 0.6 0.15 0.3
1 0.8 0.65 0.12 0.28
2 0.5 0.15 0.1 0.08
3 0.5 0.9 0.12 0.08
4 0.15 0.35 0.08 0.06
4 0.35 0.5 0.08 0.06
4 0.65 0.5 0.08 0.06
4 0.85 0.35 0.08 0.06
5 0.1 0.2 0.06 0.06
5 0.9 0.2 0.06 0.06
```

**Format:** `<class_id> <x_center> <y_center> <width> <height>`

- **class_id**: 0=fan, 1=pipe, 2=connector, 3=drain_plug, 4=grommet, 5=clip, 6=fin
- **x_center, y_center**: Center coordinates (0.0 to 1.0)
- **width, height**: Box dimensions (0.0 to 1.0)

---

## 🎯 Annotation Best Practices

### ✅ Do's
- ✅ Draw **tight bounding boxes**
- ✅ Ensure box **touches component edges**
- ✅ Label **ALL components** in image
- ✅ Be **consistent** across images
- ✅ Verify labels are correct
- ✅ Take breaks every 50 images

### ❌ Don'ts
- ❌ Don't make boxes too loose
- ❌ Don't include background
- ❌ Don't miss small components
- ❌ Don't use different styles for same component
- ❌ Don't rush (quality > speed)

---

## 📊 Expected Component Counts Per Radiator

Use this to verify your annotation:

| Component | Typical Count | Min | Max |
|-----------|---------------|-----|-----|
| fan | 1 | 1 | 1 |
| pipe | 2-3 | 2 | 4 |
| connector | 1-2 | 1 | 2 |
| drain_plug | 1 | 1 | 1 |
| rubber_grommet | 3-5 | 3 | 5 |
| clip | 4-8 | 4 | 8 |
| radiator_fin | Many | - | - |

If your counts are very different, double-check annotation accuracy.

---

## ⏱️ Annotation Timeline

### Realistic Schedule (300 images, 1 person)

| Phase | Days | Images/Day | Total |
|-------|------|-----------|-------|
| Setup & First 50 | 1 | 50 | 50 |
| Speed up (50-150) | 1 | 100 | 100 |
| Steady (150-250) | 1 | 100 | 100 |
| Final push (250-300) | 0.5 | 50 | 50 |
| **Total** | **3-4 days** | **75/day avg** | **300** |

**Tips to speed up:**
- Use keyboard shortcuts
- Work in focused 2-hour sessions
- Do similar view radiators consecutively
- Take breaks to avoid fatigue

---

## 🔍 Quality Assurance

### Before Proceeding to Training

```bash
# 1. Verify label format
python validate_labels.py

# 2. Check class distribution
# Should see roughly:
# - 300 fans
# - 600-900 pipes
# - 300-600 connectors
# - 300 drain plugs
# - 900-1500 grommets
# - 1200-2400 clips
```

### Manual Spot Check

1. Pick 10 random images
2. Open image + corresponding .txt file
3. Verify counts match
4. Check box coordinates (0-1 range)

---

## 📂 File Organization After Annotation

```
dataset/
├── images/
│   ├── train/  (210 images + labels)
│   ├── val/    (45 images + labels)
│   └── test/   (45 images + labels)
└── labels/
    ├── train/  (210 .txt files)
    ├── val/    (45 .txt files)
    └── test/   (45 .txt files)
```

**Verify:**
- ✓ Each image has matching .txt file
- ✓ 70/15/15 split across folders
- ✓ All labels in YOLO format

---

## 🚀 Next Steps After Annotation

```bash
# Step 1: Validate all labels
python validate_labels.py

# Step 2: Expand dataset 3x using augmentation
python augment_dataset.py

# Step 3: Train YOLOv8 model
python train_model.py
```

---

## 🆘 Troubleshooting

### Label Studio Won't Start
```bash
# Clear cache and restart
rm -rf data/
label-studio reset
label-studio
```

### CVAT Docker Error
```bash
# Check if port 8080 is available
netstat -an | grep 8080

# Use different port
docker run -d -p 9090:8080 openvino/cvat:latest
# Then access: http://localhost:9090
```

### Export Format Wrong
- Make sure to select **YOLO** format
- Not COCO, not VOC, only YOLO
- Version should be YOLO 1.1

### Labels Not in YOLO Format
- Check file has 5 values per line: `class_id x y w h`
- Values should be decimal numbers (0.0 to 1.0)
- No extra spaces or characters

---

## 💡 Pro Tips

1. **Annotate in batches of 50** - easier to maintain consistency
2. **Save frequently** - use Ctrl+S or auto-save
3. **Take breaks every 50 images** - prevents errors
4. **Use same color for same component** - if tool allows
5. **Verify as you go** - catch mistakes early
6. **Double-check small components** - rubber_grommet, clip
7. **Zoom in on difficult areas** - most tools allow zoom

---

## ✅ Checklist Before Moving to Training

- [ ] All 300 images annotated
- [ ] All .txt label files created
- [ ] Labels in YOLO format (5 values per line)
- [ ] Proper train/val/test split (70/15/15)
- [ ] validate_labels.py passes
- [ ] Manual spot check of 10 random images
- [ ] No missing labels
- [ ] No corrupted image files

---

## 🎓 Learning Resources

- **Label Studio Docs**: https://labelstud.io/
- **CVAT Tutorial**: https://cvat.ai/
- **YOLO Format**: https://docs.ultralytics.com/
- **Annotation Best Practices**: https://roboflow.com/

---

**Now choose your tool and start annotating! You've got this!** 💪
