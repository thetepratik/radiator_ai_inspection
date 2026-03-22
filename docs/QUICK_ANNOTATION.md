# ⚡ QUICK COMMAND GUIDE - Organize Your Images

## In 3 Simple Steps

### Step 1: Navigate to Project Folder
```bash
cd radiator_ai_inspection
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Step 3: Run Organization Script
```bash
python scripts/organize_dataset.py
```

---

## That's It!

When prompted:
1. **Enter path to your images:** `C:\Users\YourName\Documents\radiator_images`
2. **Choose method:** `1` (if images are organized by view) or `2` (if random)
3. **Wait** for completion

---

## Verify It Worked

**Windows:**
```bash
dir dataset\images\train /b | find /c ".jpg"
```

**Mac/Linux:**
```bash
ls dataset/images/train | wc -l
```

Should show ~210 images

---

## What It Does

✅ Takes your 300 images
✅ Splits into 70/15/15 (train/val/test)
✅ Copies to project folders
✅ Shows progress

---

## Next Step After Organization

Read the **ANNOTATION_GUIDE.md** to learn how to annotate images!

```bash
pip install label-studio
label-studio
```

Open: http://localhost:8080

---

## Done! ✅

Your images are now organized and ready for annotation!