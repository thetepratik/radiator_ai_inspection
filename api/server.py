"""
FastAPI Backend Server for Radiator Inspection System
Handles image uploads, inference, and inspection logic
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ultralytics import YOLO
from PIL import Image
import io
import json
from pathlib import Path
from datetime import datetime
import logging

# Import inspection logic
from inspection_logic import InspectionEngine, Detection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Radiator Inspection API",
    description="AI-Based Visual Inspection System for Automotive Radiators",
    version="1.0.0"
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

@app.on_event("startup")
async def startup_event():
    """Initialize model and engine on startup"""
    global model, inspection_engine
    
    logger.info("Loading YOLO model...")
    try:
        model_path = "models/radiator_detector/weights/best.pt"
        model = YOLO(model_path)
        logger.info(f"✓ Model loaded from {model_path}")
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}")
        raise
    
    logger.info("Initializing inspection engine...")
    inspection_engine = InspectionEngine()
    logger.info("✓ Inspection engine initialized")
    
    # Create results directory
    results_dir.mkdir(parents=True, exist_ok=True)


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
        "engine_ready": inspection_engine is not None
    }


@app.post("/inspect")
async def inspect_radiator(file: UploadFile = File(...)):
    """
    Main inspection endpoint
    
    Args:
        file: Image file of radiator
        
    Returns:
        Inspection result with OK/NOT OK status
    """
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        logger.info(f"Processing image: {file.filename}")
        
        # Run YOLO inference
        results = model.predict(source=image, conf=0.5, verbose=False)
        
        # Extract detections
        detections = []
        if results and len(results) > 0:
            for result in results:
                for box, conf, cls in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
                    x1, y1, x2, y2 = box.tolist()
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    width = x2 - x1
                    height = y2 - y1
                    
                    class_name = model.names[int(cls)]
                    confidence = float(conf)
                    
                    detection = Detection(
                        class_name=class_name,
                        confidence=confidence,
                        bbox=(x_center, y_center, width, height)
                    )
                    detections.append(detection)
        
        # Generate inspection report
        inspection_result = inspection_engine.generate_final_decision(detections)
        inspection_result['image_filename'] = file.filename
        
        # Save result
        result_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"inspection_{result_id}.json"
        
        with open(result_file, 'w') as f:
            json.dump(inspection_result, f, indent=2, default=str)
        
        logger.info(f"✓ Inspection complete. Status: {inspection_result['status']}")
        
        return {
            "result_id": result_id,
            "status": inspection_result['status'],
            "timestamp": inspection_result['timestamp'],
            "components": inspection_result['component_presence']['present_components'],
            "missing_components": inspection_result['component_presence']['missing_components'],
            "confidence": inspection_result['confidence_score'],
            "failures": inspection_result['failures'],
            "warnings": inspection_result['warnings']
        }
    
    except Exception as e:
        logger.error(f"✗ Error processing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/inspect/batch")
async def inspect_batch(files: list[UploadFile] = File(...)):
    """
    Batch inspection endpoint
    
    Args:
        files: Multiple image files
        
    Returns:
        List of inspection results
    """
    results = []
    
    for file in files:
        try:
            contents = await file.read()
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            
            # Run YOLO inference
            model_results = model.predict(source=image, conf=0.5, verbose=False)
            
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
                        
                        class_name = model.names[int(cls)]
                        confidence = float(conf)
                        
                        detection = Detection(
                            class_name=class_name,
                            confidence=confidence,
                            bbox=(x_center, y_center, width, height)
                        )
                        detections.append(detection)
            
            # Generate inspection report
            inspection_result = inspection_engine.generate_final_decision(detections)
            
            results.append({
                "filename": file.filename,
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
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
