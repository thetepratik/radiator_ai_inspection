"""
Label Validation Script for YOLO Dataset
Validates annotation format and detects common errors
"""

import os
from pathlib import Path
import json

class LabelValidator:
    """Validate YOLO format labels"""
    
    def __init__(self, dataset_path="./dataset", num_classes=7):
        self.dataset_path = Path(dataset_path)
        self.num_classes = num_classes
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_images': 0,
            'total_labels': 0,
            'valid_labels': 0,
            'invalid_labels': 0,
            'missing_labels': 0,
            'extra_labels': 0,
            'missing_images': 0,
            'invalid_format': 0,
        }
    
    def validate_label_file(self, label_path):
        """Validate single label file format"""
        errors = []
        
        if not label_path.exists():
            return None, ["Label file not found"]
        
        if label_path.stat().st_size == 0:
            return True, []  # Empty file is valid (image with no objects)
        
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        for line_idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
            
            parts = line.split()
            
            # Check format
            if len(parts) != 5:
                errors.append(f"Line {line_idx}: Expected 5 values, got {len(parts)}")
                self.stats['invalid_format'] += 1
                continue
            
            try:
                class_id = int(parts[0])
                x_center = float(parts[1])
                y_center = float(parts[2])
                width = float(parts[3])
                height = float(parts[4])
                
                # Validate class ID
                if class_id < 0 or class_id >= self.num_classes:
                    errors.append(f"Line {line_idx}: Invalid class ID {class_id} (range: 0-{self.num_classes-1})")
                
                # Validate coordinates
                if not (0 <= x_center <= 1):
                    errors.append(f"Line {line_idx}: x_center {x_center} out of range [0, 1]")
                if not (0 <= y_center <= 1):
                    errors.append(f"Line {line_idx}: y_center {y_center} out of range [0, 1]")
                if not (0 < width <= 1):
                    errors.append(f"Line {line_idx}: width {width} out of range (0, 1]")
                if not (0 < height <= 1):
                    errors.append(f"Line {line_idx}: height {height} out of range (0, 1]")
                
            except ValueError as e:
                errors.append(f"Line {line_idx}: Cannot parse values - {e}")
        
        return len(errors) == 0, errors
    
    def validate_dataset(self):
        """Validate entire dataset"""
        print("🔍 Validating YOLO Dataset...")
        print("=" * 60)
        
        for split in ['train', 'val', 'test']:
            print(f"\n📂 Validating {split.upper()} split...")
            print("-" * 60)
            
            images_dir = self.dataset_path / 'images' / split
            labels_dir = self.dataset_path / 'labels' / split
            
            if not images_dir.exists():
                print(f"⚠️  Images directory not found: {images_dir}")
                continue
            
            # Get all image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
            image_files = [f for f in images_dir.iterdir() 
                          if f.suffix.lower() in image_extensions]
            
            split_stats = {
                'images': len(image_files),
                'valid': 0,
                'invalid': 0,
                'missing_labels': 0,
            }
            
            for image_file in image_files:
                label_file = labels_dir / f"{image_file.stem}.txt"
                
                if not label_file.exists():
                    print(f"  ✗ Missing label: {image_file.name}")
                    split_stats['missing_labels'] += 1
                    self.stats['missing_labels'] += 1
                    continue
                
                # Validate label
                is_valid, errors = self.validate_label_file(label_file)
                
                if is_valid:
                    split_stats['valid'] += 1
                    self.stats['valid_labels'] += 1
                else:
                    split_stats['invalid'] += 1
                    self.stats['invalid_labels'] += 1
                    print(f"  ✗ {image_file.name}:")
                    for error in errors:
                        print(f"     - {error}")
            
            self.stats['total_images'] += split_stats['images']
            
            # Summary for split
            print(f"\n  Summary for {split.upper()}:")
            print(f"  ✓ Valid: {split_stats['valid']}")
            print(f"  ✗ Invalid: {split_stats['invalid']}")
            print(f"  ⚠️  Missing labels: {split_stats['missing_labels']}")
    
    def analyze_class_distribution(self):
        """Analyze class distribution in dataset"""
        print("\n\n📊 Class Distribution Analysis...")
        print("=" * 60)
        
        class_counts = {}
        
        for split in ['train', 'val', 'test']:
            labels_dir = self.dataset_path / 'labels' / split
            
            if not labels_dir.exists():
                continue
            
            print(f"\n{split.upper()} Split:")
            print("-" * 60)
            
            split_class_counts = {}
            total_objects = 0
            
            for label_file in labels_dir.glob('*.txt'):
                if label_file.stat().st_size == 0:
                    continue
                
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        class_id = int(parts[0])
                        split_class_counts[class_id] = split_class_counts.get(class_id, 0) + 1
                        total_objects += 1
                        class_counts[class_id] = class_counts.get(class_id, 0) + 1
            
            # Print distribution
            for class_id in sorted(split_class_counts.keys()):
                count = split_class_counts[class_id]
                percentage = (count / total_objects * 100) if total_objects > 0 else 0
                bar_length = int(percentage / 2)
                bar = '█' * bar_length
                print(f"  Class {class_id}: {count:6d} ({percentage:5.1f}%) {bar}")
        
        print(f"\n{'='*60}")
        print("Overall Class Distribution:")
        print("-" * 60)
        total_objects = sum(class_counts.values())
        for class_id in sorted(class_counts.keys()):
            count = class_counts[class_id]
            percentage = (count / total_objects * 100) if total_objects > 0 else 0
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            print(f"  Class {class_id}: {count:6d} ({percentage:5.1f}%) {bar}")
        
        return class_counts
    
    def print_summary(self):
        """Print validation summary"""
        print(f"\n\n📋 Validation Summary")
        print("=" * 60)
        print(f"Total images found:     {self.stats['total_images']}")
        print(f"Valid labels:           {self.stats['valid_labels']}")
        print(f"Invalid labels:         {self.stats['invalid_labels']}")
        print(f"Missing labels:         {self.stats['missing_labels']}")
        
        if self.stats['total_images'] > 0:
            valid_pct = (self.stats['valid_labels'] / self.stats['total_images']) * 100
            print(f"\n✓ Overall validity:     {valid_pct:.1f}%")
            
            if valid_pct == 100:
                print("✅ Dataset is valid and ready for training!")
            elif valid_pct >= 95:
                print("⚠️  Dataset is mostly valid, fix the above errors for best results")
            else:
                print("❌ Dataset has too many errors, fix before training")
        
        print("=" * 60)
    
    def export_report(self, output_file="validation_report.json"):
        """Export validation report as JSON"""
        report = {
            'timestamp': str(Path()),
            'statistics': self.stats,
            'total_images': self.stats['total_images'],
            'valid_percentage': (self.stats['valid_labels'] / self.stats['total_images'] * 100) 
                              if self.stats['total_images'] > 0 else 0
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved to: {output_file}")


def main():
    """Main validation function"""
    validator = LabelValidator(
        dataset_path="./dataset",
        num_classes=11  # barcode, cap, condenser_stud, dust_cap, fan_chip, flap, grommet, leak_test_mark, locking_nut, mickey_mouse, wire
    )
    
    # Run validation
    validator.validate_dataset()
    
    # Analyze class distribution
    validator.analyze_class_distribution()
    
    # Print summary
    validator.print_summary()
    
    # Export report
    validator.export_report("validation_report.json")


if __name__ == "__main__":
    main()
