"""
FastAPI Backend Server for Radiator Inspection System
Handles image uploads, inference, and inspection logic
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ultralytics import YOLO
from PIL import Image, ImageDraw, ImageFont
import io
import json
import base64
from pathlib import Path
from datetime import datetime
import logging
from contextlib import asynccontextmanager

import sys
import os

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import inspection logic
from inspection.inspection_logic import InspectionEngine, Detection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize model and engine on startup"""
    global model, inspection_engine
    
    logger.info("Loading YOLO model...")
    model_path = Path("models/radiator_detector/weights/best.pt")
    
    if not model_path.exists():
        # Fallback to EDI2 directory where the user's weights actually are
        fallback_path = Path(parent_dir).parent / "EDI2" / "radiator_ai_inspection" / "models" / "radiator_detector" / "weights" / "best.pt"
        if fallback_path.exists():
            model_path = fallback_path
            logger.info(f"Found model weights in EDI2 fallback folder: {model_path}")
        else:
            logger.warning(f"⚠️ Model weights not found at {model_path} or fallback.")
            logger.info("Searching for alternative weights in both directories...")
            
            # Look for any .pt files in local models directory
            alternative_weights = list(Path("models").rglob("*.pt"))
            
            # Look in EDI2 directory
            if not alternative_weights:
                edi2_models = Path(parent_dir).parent / "EDI2" / "radiator_ai_inspection" / "models"
                if edi2_models.exists():
                    alternative_weights = list(edi2_models.rglob("*.pt"))
            
            if alternative_weights:
                model_path = alternative_weights[0]
                logger.info(f"Found alternative weights: {model_path}")
            else:
                logger.error("❌ No model weights (.pt files) found in any models directory.")
                logger.info("Please run 'python scripts/train_model.py' to train the model first.")
    
    if model_path.exists():
        try:
            model = YOLO(str(model_path))
            logger.info(f"✓ Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
    
    logger.info("Initializing inspection engine...")
    try:
        config_path = os.path.join(parent_dir, "config", "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                full_config = yaml.safe_load(f)
            
            engine_config = {
                'required_components': full_config['inspection']['required_components'],
                'min_confidence': full_config['inspection']['min_confidence'],
                'max_defects': full_config['inspection']['max_defects'],
                'component_rules': full_config.get('component_rules', {}),
                'views': full_config['inspection'].get('views', {})
            }
            inspection_engine = InspectionEngine(config=engine_config)
            logger.info("✓ Inspection engine initialized")
        else:
            logger.warning(f"Config file not found at {config_path}")
            inspection_engine = InspectionEngine()
    except Exception as e:
        logger.warning(f"Failed to load config.yaml: {e}. Falling back to default config.")
        inspection_engine = InspectionEngine()
    
    # Create results directory
    results_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    # Clean up (if needed)
    logger.info("Shutting down server...")

app = FastAPI(
    title="Radiator Inspection API",
    description="AI-Based Visual Inspection System for Automotive Radiators",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
inspection_engine = None
results_dir = Path("results/inspections")

import yaml


def draw_annotated_image(
    image: Image.Image,
    detections: list,
    inspection_result: dict
) -> str:
    """
    Draw colored bounding boxes on the image and return as base64 PNG.

    - GREEN box  → component detected with OK status
    - RED box    → component detected but count is insufficient (COUNT_MISMATCH)
    - RED banner → missing components (no box, never detected)

    Args:
        image: Original PIL Image
        detections: List of Detection objects
        inspection_result: Output of generate_final_decision()

    Returns:
        Base64-encoded PNG string
    """
    img = image.copy()
    draw = ImageDraw.Draw(img)
    img_w, img_h = img.size

    present_components = inspection_result.get('component_presence', {}).get('present_components', {})
    count_mismatches = set(inspection_result.get('component_presence', {}).get('count_mismatches', []))
    missing_components = inspection_result.get('component_presence', {}).get('missing_components', [])

    # Try to load a font; fall back to default if unavailable
    try:
        font = ImageFont.truetype("arial.ttf", max(12, img_h // 40))
        small_font = ImageFont.truetype("arial.ttf", max(10, img_h // 55))
    except Exception:
        font = ImageFont.load_default()
        small_font = font

    BOX_WIDTH = max(2, img_w // 300)

    for det in detections:
        class_name = det.class_name
        conf = det.confidence
        x_c, y_c, w, h = det.bbox  # could be normalized (0..1) or absolute pixels

        # If bbox values look normalized (<= 1), convert to pixel coords
        if 0 < x_c <= 1 and 0 < y_c <= 1 and 0 < w <= 1 and 0 < h <= 1:
            x_c_pix = int(x_c * img_w)
            y_c_pix = int(y_c * img_h)
            w_pix = int(w * img_w)
            h_pix = int(h * img_h)
        else:
            x_c_pix = int(x_c)
            y_c_pix = int(y_c)
            w_pix = int(w)
            h_pix = int(h)

        x1 = int(x_c_pix - w_pix / 2)
        y1 = int(y_c_pix - h_pix / 2)
        x2 = int(x_c_pix + w_pix / 2)
        y2 = int(y_c_pix + h_pix / 2)

        # Decide colour
        if class_name in count_mismatches:
            color = (220, 38, 38)   # red — detected but not enough
        elif class_name in present_components:
            color = (34, 197, 94)   # green — detected and OK
        else:
            color = (234, 179, 8)   # amber — detected but not required / low conf

        # Draw rectangle
        draw.rectangle([x1, y1, x2, y2], outline=color, width=BOX_WIDTH)

        # Label background + text
        label = f"{class_name} {conf:.0%}"
        try:
            bbox_text = draw.textbbox((x1, y1), label, font=small_font)
            tw = bbox_text[2] - bbox_text[0]
            th = bbox_text[3] - bbox_text[1]
        except AttributeError:
            tw, th = draw.textsize(label, font=small_font)

        label_y = max(0, y1 - th - 4)
        draw.rectangle([x1, label_y, x1 + tw + 6, label_y + th + 4], fill=color)
        draw.text((x1 + 3, label_y + 2), label, fill=(255, 255, 255), font=small_font)

    # Load predefined missing regions (if any) from config
    try:
        missing_cfg_path = Path("config/missing_regions.yaml")
        if missing_cfg_path.exists():
            with open(missing_cfg_path, "r", encoding="utf-8") as f:
                missing_cfg = yaml.safe_load(f) or {}
        else:
            missing_cfg = {}
    except Exception:
        missing_cfg = {}

    # Draw Red Outline Boxes for MISSING components using predefined regions or fallback
    if missing_components:
        for i, comp in enumerate(missing_components):
            # Try to get region from config (expects bbox as [x_center, y_center, w, h])
            region = missing_cfg.get(comp)
            if region and isinstance(region, (list, tuple)) and len(region) == 4:
                x_c, y_c, w, h = region
                x1 = int(x_c - w / 2)
                y1 = int(y_c - h / 2)
                x2 = int(x_c + w / 2)
                y2 = int(y_c + h / 2)
                draw.rectangle([x1, y1, x2, y2], outline=(220, 38, 38), width=BOX_WIDTH + 2)
                # Label
                label = f"MISSING: {comp.upper()}"
                try:
                    txt_w, txt_h = draw.textsize(label, font=font)
                    txt_x = x1 + (w - txt_w) // 2
                    txt_y = y1 + (h - txt_h) // 2
                    draw.text((txt_x, txt_y), label, fill=(255, 255, 255), font=font)
                except Exception:
                    draw.text((x1 + 4, y1 + 4), label, fill=(255, 255, 255))
            else:
                # Fallback: draw centered placeholder box
                box_w = max(30, img_w // 10)
                box_h = max(30, img_h // 10)
                x1 = int((img_w - box_w) / 2)
                y1 = int(img_h // 4 + i * (box_h + 10))
                x2 = x1 + box_w
                y2 = y1 + box_h
                draw.rectangle([x1, y1, x2, y2], outline=(220, 38, 38), width=BOX_WIDTH + 2)
                label = f"MISSING: {comp.upper()}"
                try:
                    txt_w, txt_h = draw.textsize(label, font=font)
                    txt_x = x1 + (box_w - txt_w) // 2
                    txt_y = y1 + (box_h - txt_h) // 2
                    draw.text((txt_x, txt_y), label, fill=(255, 255, 255), font=font)
                except Exception:
                    draw.text((x1 + 4, y1 + 4), label, fill=(255, 255, 255))


    # Encode to base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Radiator Inspection API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "engine_ready": inspection_engine is not None,
        "available_views": list(inspection_engine.config.get('views', {}).keys()) if inspection_engine else []
    }


@app.post("/inspect")
async def inspect_radiator(file: UploadFile = File(...), view: str = None):
    """
    Main inspection endpoint
    
    Args:
        file: Image file of radiator
        view: Optional side/view to check (e.g., front_side, back_side)
        
    Returns:
        Inspection result with OK/NOT OK status
    """
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        logger.info(f"Processing image: {file.filename}")
        
        # Check if model is loaded
        if model is None:
            raise HTTPException(
                status_code=503, 
                detail="Model not loaded. Please ensure training is complete and best.pt exists."
            )
        
        # Run YOLO inference
        # Use a lower confidence filter at model level so the inspection engine
        # can apply per-component thresholds defined in config (detection_threshold).
        results = model.predict(source=image, conf=0.2, verbose=False)
        
        # Extract detections (store absolute pixel coords for annotation)
        detections = []
        if results and len(results) > 0:
            for result in results:
                for box, conf, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    x1, y1, x2, y2 = box.tolist()
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1

                    # Normalize class name to match config keys (underscores, lowercase)
                    class_name = model.names[int(cls)].replace(' ', '_').lower()
                    confidence = float(conf)
                    
                    # Store bbox as normalized coordinates (0..1) for inspection logic
                    img_w, img_h = image.size
                    detection = Detection(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x_center / img_w, y_center / img_h, width / img_w, height / img_h)
                    )
                    detections.append(detection)
        
        # Generate inspection report
        inspection_result = inspection_engine.generate_final_decision(detections, view=view, filename=file.filename)
        inspection_result['image_filename'] = file.filename
        
        # --- Annotate image with colored bounding boxes ---
        annotated_b64 = draw_annotated_image(image, detections, inspection_result)
        
        # Save result
        result_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"inspection_{result_id}.json"
        
        with open(result_file, 'w') as f:
            json.dump(inspection_result, f, indent=2, default=str)
        
        logger.info(f"✓ Inspection complete. Status: {inspection_result['status']}")
        
        return {
            "result_id": result_id,
            "status": inspection_result['status'],
            "detected_view": inspection_result.get('detected_view', 'unknown'),
            "timestamp": inspection_result['timestamp'],
            "components": inspection_result['component_presence']['present_components'],
            "missing_components": inspection_result['component_presence']['missing_components'],
            "confidence": inspection_result['confidence_score'],
            "failures": inspection_result['failures'],
            "warnings": inspection_result['warnings'],
            "annotated_image": annotated_b64,
            "detections": [
                {
                    "class_name": d.class_name,
                    "confidence": round(d.confidence, 4),
                    "bbox": list(d.bbox)
                }
                for d in detections
            ]
        }
    
    except Exception as e:
        logger.error(f"✗ Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inspect/batch")
async def inspect_batch(files: list[UploadFile] = File(...), view: str = None):
    """
    Batch inspection endpoint
    
    Args:
        files: Multiple image files
        view: Optional side/view to check for all images in batch
        
    Returns:
        List of inspection results
    """
    results = []
    
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            
            # Run YOLO inference (lower conf to allow per-component filtering)
            model_results = model.predict(source=image, conf=0.2, verbose=False)
            
            # Extract detections
            detections = []
            if model_results and len(model_results) > 0:
                for result in model_results:
                    for box, conf, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                        x1, y1, x2, y2 = box.tolist()
                        x_center = (x1 + x2) / 2
                        y_center = (y1 + y2) / 2
                        width = x2 - x1
                        height = y2 - y1

                        # Normalize class name to match config keys
                        class_name = model.names[int(cls)].replace(' ', '_').lower()
                        confidence = float(conf)

                        img_w, img_h = image.size
                        detection = Detection(
                            class_name=class_name,
                            confidence=confidence,
                            bbox=(x_center / img_w, y_center / img_h, width / img_w, height / img_h)
                        )
                        detections.append(detection)
            
            # Generate inspection report (enables auto-view detection by passing filename)
            inspection_result = inspection_engine.generate_final_decision(detections, view=view, filename=file.filename)
            
            results.append({
                "filename": file.filename,
                "detected_view": inspection_result.get('detected_view', 'unknown'),
                "status": inspection_result['status'],
                "confidence": inspection_result['confidence_score'],
                "failures": inspection_result['failures']
            })
        
        except Exception as e:
            logger.error(f"✗ Error processing {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"total_files": len(files), "results": results}


@app.get("/results/{result_id}")
async def get_result(result_id: str):
    """
    Get detailed inspection result
    
    Args:
        result_id: Inspection result ID
        
    Returns:
        Full inspection report
    """
    result_file = results_dir / f"inspection_{result_id}.json"
    
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    
    with open(result_file, 'r') as f:
        return json.load(f)


@app.get("/results")
async def list_results(limit: int = 10):
    """
    List recent inspection results
    
    Args:
        limit: Number of results to return
        
    Returns:
        List of recent results
    """
    result_files = sorted(results_dir.glob("inspection_*.json"), reverse=True)[:limit]
    
    results = []
    for result_file in result_files:
        with open(result_file, 'r') as f:
            data = json.load(f)
            results.append({
                "result_id": result_file.stem.replace("inspection_", ""),
                "status": data['status'],
                "timestamp": data['timestamp'],
                "image": data.get('image_filename', 'N/A')
            })
    
    return results


@app.get("/statistics")
async def get_statistics():
    """Get inspection statistics"""
    result_files = list(results_dir.glob("inspection_*.json"))
    
    ok_count = 0
    not_ok_count = 0
    total_count = len(result_files)
    
    for result_file in result_files:
        with open(result_file, 'r') as f:
            data = json.load(f)
            if data['status'] == 'OK':
                ok_count += 1
            else:
                not_ok_count += 1
    
    return {
        "total_inspections": total_count,
        "passed": ok_count,
        "failed": not_ok_count,
        "pass_rate": ok_count / total_count if total_count > 0 else 0
    }


@app.get("/model/info")
async def get_model_info():
    """Get model information"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    return {
        "model_name": "YOLOv8",
        "classes": model.names,
        "input_size": 640,
        "device": "GPU" if model.device == "cuda" else "CPU"
    }


@app.get("/export/report/{result_id}")
async def export_report(result_id: str):
    """Export inspection report as text file"""
    result_file = results_dir / f"inspection_{result_id}.json"
    
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    
    with open(result_file, 'r') as f:
        data = json.load(f)
    
    # Create text report (simplified version)
    report = f"""
RADIATOR INSPECTION REPORT
{'='*60}
Inspection ID: {result_id}
Timestamp: {data['timestamp']}
Status: {data['status']}
Confidence: {data['confidence_score']:.2%}

COMPONENTS DETECTED:
{'-'*60}
"""
    
    for component, details in data['component_presence']['present_components'].items():
        report += f"{component.upper()}: {details['count']} (expected: {details['expected']}) - Confidence: {details['confidence']:.2%}\n"
    
    if data['component_presence']['missing_components']:
        report += "\nMISSING COMPONENTS:\n"
        for component in data['component_presence']['missing_components']:
            report += f"- {component.upper()}\n"
    
    report += f"\n{'='*60}\n"
    
    # Save to file
    report_file = results_dir / f"report_{result_id}.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    return FileResponse(report_file, filename=f"report_{result_id}.txt")


if __name__ == "__main__":
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
