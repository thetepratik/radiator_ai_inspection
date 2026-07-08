"""
Image Organization Script
Automatically organizes images into train/val/test folders (70/15/15 split)
"""

import os
import shutil
from pathlib import Path
import random

class DatasetOrganizer:
    """Organize images into train/val/test folders by view"""
    
    def __init__(self, source_dir, target_dir="./dataset"):
        """
        Args:
            source_dir: Path containing your organized images (front/back/side/top folders)
            target_dir: Where to create train/val/test folders
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.views = ['front', 'back', 'side', 'top']
        
    def create_folder_structure(self):
        """Create train/val/test folder structure"""
        for split in ['train', 'val', 'test']:
            (self.target_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.target_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)
        
        print("✓ Folder structure created")
        print(f"  {self.target_dir}/")
        print(f"  ├── images/")
        print(f"  │   ├── train/")
        print(f"  │   ├── val/")
        print(f"  │   └── test/")
        print(f"  └── labels/")
        print(f"      ├── train/")
        print(f"      ├── val/")
        print(f"      └── test/")
    
    def get_image_files(self, view_folder):
        """Get all image files from a folder"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
        images = []
        
        folder = self.source_dir / view_folder
        if folder.exists():
            images = [f for f in folder.iterdir() if f.suffix in image_extensions]
        
        return sorted(images)
    
    def split_images(self, images, train_ratio=0.7, val_ratio=0.15):
        """Split images into train/val/test"""
        random.shuffle(images)
        
        total = len(images)
        train_count = int(total * train_ratio)
        val_count = int(total * val_ratio)
        
        train = images[:train_count]
        val = images[train_count:train_count + val_count]
        test = images[train_count + val_count:]
        
        return train, val, test
    
    def copy_images(self, images, split):
        """Copy images to target folder"""
        target_folder = self.target_dir / 'images' / split
        
        for image in images:
            try:
                shutil.copy2(image, target_folder / image.name)
            except Exception as e:
                print(f"⚠️  Error copying {image.name}: {e}")
    
    def organize_by_view(self):
        """Organize images by view into train/val/test"""
        print("\n📁 Organizing Images by View...")
        print("=" * 60)
        
        # Create folder structure
        self.create_folder_structure()
        
        total_images = 0
        view_stats = {}
        
        for view in self.views:
            print(f"\n📸 Processing {view.upper()} view:")
            print("-" * 60)
            
            # Get images from this view
            images = self.get_image_files(view)
            
            if not images:
                print(f"⚠️  No images found in {view} folder")
                continue
            
            print(f"  Found: {len(images)} images")
            
            # Split into train/val/test
            train, val, test = self.split_images(images)
            
            # Copy to target folders
            self.copy_images(train, 'train')
            self.copy_images(val, 'val')
            self.copy_images(test, 'test')
            
            # Stats
            view_stats[view] = {
                'total': len(images),
                'train': len(train),
                'val': len(val),
                'test': len(test)
            }
            
            total_images += len(images)
            
            print(f"  ✓ Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
        
        return total_images, view_stats
    
    def organize_random(self):
        """Organize all images randomly (ignore view separation)"""
        print("\n📁 Organizing Images (Random)...")
        print("=" * 60)
        
        # Create folder structure
        self.create_folder_structure()
        
        # Collect all images
        all_images = []
        for view in self.views:
            images = self.get_image_files(view)
            all_images.extend(images)
        
        print(f"Found: {len(all_images)} total images")
        
        # Split randomly
        train, val, test = self.split_images(all_images)
        
        # Copy to folders
        self.copy_images(train, 'train')
        self.copy_images(val, 'val')
        self.copy_images(test, 'test')
        
        print("\n✓ Image organization complete:")
        print(f"  Train: {len(train)} images (70%)")
        print(f"  Val:   {len(val)} images (15%)")
        print(f"  Test:  {len(test)} images (15%)")
        
        return len(all_images)
    
    def print_summary(self, total_images, view_stats=None):
        """Print organization summary"""
        print("\n" + "=" * 60)
        print("📊 ORGANIZATION SUMMARY")
        print("=" * 60)
        
        print(f"Total images: {total_images}")
        print(f"Target location: {self.target_dir.absolute()}")
        
        if view_stats:
            print("\nBreakdown by view:")
            for view, stats in view_stats.items():
                print(f"  {view.upper()}:")
                print(f"    Total: {stats['total']}")
                print(f"    Train: {stats['train']} | Val: {stats['val']} | Test: {stats['test']}")
        
        # Calculate actual distribution
        train_dir = self.target_dir / 'images' / 'train'
        val_dir = self.target_dir / 'images' / 'val'
        test_dir = self.target_dir / 'images' / 'test'
        
        if all(d.exists() for d in [train_dir, val_dir, test_dir]):
            train_count = len(list(train_dir.glob('*.*')))
            val_count = len(list(val_dir.glob('*.*')))
            test_count = len(list(test_dir.glob('*.*')))
            
            print(f"\nActual split:")
            print(f"  Train: {train_count} ({train_count/(train_count+val_count+test_count)*100:.1f}%)")
            print(f"  Val:   {val_count} ({val_count/(train_count+val_count+test_count)*100:.1f}%)")
            print(f"  Test:  {test_count} ({test_count/(train_count+val_count+test_count)*100:.1f}%)")
        
        print("=" * 60)
        print("\n✅ Ready for annotation!")
        print("\nNext steps:")
        print("1. Use CVAT or Label Studio to annotate images")
        print("2. Create .txt label files (YOLO format)")
        print("3. Place label files in dataset/labels/{train,val,test}/")
        print("4. Run: python validate_labels.py")
        print("5. Run: python augment_dataset.py")
        print("6. Run: python train_model.py")


def main():
    """Main organization workflow"""
    
    print("=" * 60)
    print("🗂️  RADIATOR IMAGE ORGANIZER")
    print("=" * 60)
    
    # Configuration
    # TODO: Update these paths based on YOUR folder structure
    source_directory = input("\n📍 Enter path to your images folder: ").strip()
    
    if not Path(source_directory).exists():
        print(f"❌ Error: Folder not found: {source_directory}")
        return
    
    target_directory = "./dataset"
    
    # Create organizer
    organizer = DatasetOrganizer(source_directory, target_directory)
    
    # Ask user preference
    print("\n📋 Organization Method:")
    print("1. By view (separate train/val/test by radiator view)")
    print("2. Random (mix all images randomly)")
    
    choice = input("Select (1 or 2): ").strip()
    
    if choice == "1":
        print("\n🔄 Organizing by view...")
        total, stats = organizer.organize_by_view()
        organizer.print_summary(total, stats)
    else:
        print("\n🔄 Organizing randomly...")
        total = organizer.organize_random()
        organizer.print_summary(total)


if __name__ == "__main__":
    main()
