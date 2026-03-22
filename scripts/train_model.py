"""
YOLOv8 Training Script for Radiator Component Detection
Trains the object detection model on annotated radiator images
"""

import yaml
import torch
from pathlib import Path
from ultralytics import YOLO
import matplotlib.pyplot as plt

class RadiatorModelTrainer:
    """Train YOLOv8 model for radiator component detection"""
    
    def __init__(self, config_path="config/config.yaml"):
        """Initialize trainer with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_name = self.config['model']['name']
        self.epochs = self.config['model']['epochs']
        self.batch_size = self.config['model']['batch_size']
        self.img_size = self.config['model']['img_size']
        self.device = self.config['model']['device']
        
        print(f"Using device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    def create_dataset_yaml(self):
        """Create dataset.yaml for YOLO training"""
        dataset_yaml = {
            'path': str(Path(self.config['dataset']['path']).absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': len(self.config['components']),
            'names': {i: comp for i, comp in enumerate(self.config['components'])}
        }
        
        output_path = Path(self.config['dataset']['path']) / 'dataset.yaml'
        with open(output_path, 'w') as f:
            yaml.dump(dataset_yaml, f)
        
        print(f"✓ Created dataset.yaml")
        return str(output_path)
    
    def create_classes_file(self):
        """Create classes.txt file"""
        output_path = Path(self.config['dataset']['path']).parent / 'annotations' / 'classes.txt'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            for component in self.config['components']:
                f.write(f"{component}\n")
        
        print(f"✓ Created classes.txt")
    
    def train(self):
        """Train the model"""
        print(f"\n{'='*60}")
        print(f"Starting YOLOv8 Training")
        print(f"{'='*60}")
        print(f"Model: {self.model_name}")
        print(f"Epochs: {self.epochs}")
        print(f"Batch Size: {self.batch_size}")
        print(f"Image Size: {self.img_size}")
        print(f"{'='*60}\n")
        
        # Create dataset.yaml
        dataset_yaml = self.create_dataset_yaml()
        self.create_classes_file()
        
        # Load model
        model = YOLO(f'{self.model_name}.pt')
        
        # Train
        results = model.train(
            data=dataset_yaml,
            epochs=self.epochs,
            imgsz=self.img_size,
            batch=self.batch_size,
            device=self.device,
            patience=20,  # Early stopping patience
            save=True,
            project='models',
            name='radiator_detector',
            pretrained=True,
            optimizer='SGD',
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            mosaic=1.0,
            mixup=0.1,
            copy_paste=0.0,
            augment=True,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=10,
            translate=0.1,
            scale=0.5,
            flipud=0.0,
            fliplr=0.5,
            perspective=0.0,
            flipud=0.0,
            verbose=True,
        )
        
        return results
    
    def validate(self, model_path='models/radiator_detector/weights/best.pt'):
        """Validate trained model"""
        print(f"\n{'='*60}")
        print(f"Validating Model")
        print(f"{'='*60}\n")
        
        model = YOLO(model_path)
        results = model.val()
        
        return results
    
    def test(self, model_path='models/radiator_detector/weights/best.pt', test_image_path=None):
        """Test model on test set"""
        print(f"\n{'='*60}")
        print(f"Testing Model")
        print(f"{'='*60}\n")
        
        model = YOLO(model_path)
        
        if test_image_path:
            # Test on single image
            results = model.predict(source=test_image_path, conf=0.5, save=True)
        else:
            # Test on test set
            test_dir = Path(self.config['dataset']['path']) / 'images' / 'test'
            results = model.predict(source=str(test_dir), conf=0.5, save=True)
        
        return results
    
    def export_model(self, model_path='models/radiator_detector/weights/best.pt', 
                     export_format='onnx'):
        """Export model to different formats"""
        print(f"\n{'='*60}")
        print(f"Exporting Model to {export_format.upper()}")
        print(f"{'='*60}\n")
        
        model = YOLO(model_path)
        exported_path = model.export(format=export_format)
        
        print(f"✓ Model exported to: {exported_path}")
        return exported_path


def main():
    """Main training pipeline"""
    
    # Initialize trainer
    trainer = RadiatorModelTrainer('config/config.yaml')
    
    # Phase 1: Train
    print("\n[1/4] TRAINING PHASE")
    print("-" * 60)
    trainer.train()
    
    # Phase 2: Validate
    print("\n[2/4] VALIDATION PHASE")
    print("-" * 60)
    trainer.validate()
    
    # Phase 3: Test
    print("\n[3/4] TESTING PHASE")
    print("-" * 60)
    trainer.test()
    
    # Phase 4: Export
    print("\n[4/4] EXPORT PHASE")
    print("-" * 60)
    trainer.export_model(export_format='onnx')
    trainer.export_model(export_format='tflite')
    
    print("\n" + "="*60)
    print("✓ Training Pipeline Complete!")
    print("="*60)
    print("\nBest model saved at: models/radiator_detector/weights/best.pt")


if __name__ == "__main__":
    main()
