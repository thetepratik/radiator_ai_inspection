
#"""
#     Data Augmentation Script for Radiator Dataset
#     Applies various transformations to increase dataset diversity
#     """

# import os
# import cv2
# import numpy as np
# import shutil
# from pathlib import Path
# from albumentations import (
#     Compose, HorizontalFlip, VerticalFlip, Rotate, 
#     GaussNoise, Blur, RandomBrightnessContrast,
#     Resize, PadIfNeeded
# )

# class RadiatorAugmenter:
#     """Augment radiator images while preserving YOLO labels"""
    
#     def __init__(self, dataset_path, output_factor=3):
#         """
#         Args:
#             dataset_path: Path to dataset folder
#             output_factor: How many augmented versions per image (3 = 3x dataset size)
#         """
#         self.dataset_path = Path(dataset_path)
#         self.output_factor = output_factor
#         self.augmentations = self.get_augmentation_pipeline()
    
#     def get_augmentation_pipeline(self):
#         """Define augmentation pipeline"""
#         return Compose([
#             HorizontalFlip(p=0.5),
#             VerticalFlip(p=0.3),
#             Rotate(limit=15, p=0.5),
#             GaussNoise(p=0.3),
#             Blur(blur_limit=3, p=0.3),
#             RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
#         ], bbox_params={"format": "yolo", "min_area": 0, "min_visibility": 0})
    
#     def augment_image(self, image_path, label_path):
#         """Augment single image and return variations"""
#         # Read image
#         image = cv2.imread(str(image_path))
#         if image is None:
#             print(f"Error reading {image_path}")
#             return []
        
#         # Read labels
#         with open(label_path, 'r') as f:
#             bboxes = [line.strip().split() for line in f.readlines()]
        
#         augmented_samples = []
        
#         for i in range(self.output_factor):
#             try:
#                 # Apply augmentation
#                 classes = []
#                 bboxes_list = []

#                 for bbox in bboxes:
#                     if len(bbox) < 5:
#                         print(f"Warning: skipping invalid label line in {label_path}: {' '.join(bbox)}")
#                         continue

#                     classes.append(int(bbox[0]))
#                     bboxes_list.append([float(x) for x in bbox[1:5]])

#                 if bboxes_list:
#                     transformed = self.augmentations(
#                         image=image,
#                         bboxes=bboxes_list
#                     )
#                     aug_image = transformed['image']
#                     aug_bboxes = transformed['bboxes']
#                 else:
#                     aug_image = self.augmentations(image=image)['image']
#                     aug_bboxes = []
                
#                 augmented_samples.append((aug_image, aug_bboxes, classes))
#             except Exception as e:
#                 print(f"Error augmenting {image_path}: {e}")
#                 continue
        
#         return augmented_samples
    
#     def save_augmented_data(self, image_path, label_path, augmented_samples):
#         """Save augmented images and labels"""
#         image_name = image_path.stem
#         image_ext = image_path.suffix
#         label_dir = label_path.parent
        
#         saved_files = []
        
#         for i, (aug_image, aug_bboxes, classes) in enumerate(augmented_samples, 1):
#             # Save image
#             new_image_name = f"{image_name}_aug{i}{image_ext}"
#             new_image_path = image_path.parent / new_image_name
#             cv2.imwrite(str(new_image_path), aug_image)
            
#             # Save labels
#             new_label_name = f"{image_name}_aug{i}.txt"
#             new_label_path = label_dir / new_label_name
            
#             with open(new_label_path, 'w') as f:
#                 for bbox, class_id in zip(aug_bboxes, classes):
#                     if len(bbox) == 4:
#                         f.write(f"{int(class_id)} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")
            
#             saved_files.append((new_image_path, new_label_path))
        
#         return saved_files
    
#     def augment_dataset(self):
#         """Augment entire dataset"""
#         train_images = list((self.dataset_path / 'images' / 'train').glob('*.jpg'))
#         train_images += list((self.dataset_path / 'images' / 'train').glob('*.png'))
        
#         print(f"Found {len(train_images)} training images")
        
#         augmented_count = 0
        
#         for image_path in train_images:
#             label_path = self.dataset_path / 'labels' / 'train' / f"{image_path.stem}.txt"
            
#             if not label_path.exists():
#                 print(f"Warning: No labels for {image_path.name}")
#                 continue
            
#             augmented_samples = self.augment_image(image_path, label_path)
            
#             if augmented_samples:
#                 self.save_augmented_data(image_path, label_path, augmented_samples)
#                 augmented_count += len(augmented_samples)
#                 print(f"✓ Augmented {image_path.name}: {len(augmented_samples)} variations")
        
#         print(f"\n✓ Total augmented: {augmented_count} images")
#         print(f"✓ Dataset expanded to ~{len(train_images) * (1 + self.output_factor)} images")


# if __name__ == "__main__":
#     # Usage
#     dataset_path = "./dataset"
    
#     augmenter = RadiatorAugmenter(dataset_path, output_factor=3)
#     augmenter.augment_dataset()
    
#     print("\n✓ Augmentation complete!")

#     """
# """
# Data Augmentation Script for Radiator Dataset
# Applies various transformations to increase dataset diversity


import os
import cv2
import numpy as np
import shutil
from pathlib import Path
from albumentations import (
    Compose, HorizontalFlip, VerticalFlip, Rotate, 
    GaussNoise, Blur, RandomBrightnessContrast,
    Resize, PadIfNeeded, BboxParams
)

class RadiatorAugmenter:
    """Augment radiator images while preserving YOLO labels"""
    
    def __init__(self, dataset_path, output_factor=3):
        """
        Args:
            dataset_path: Path to dataset folder
            output_factor: How many augmented versions per image (3 = 3x dataset size)
        """
        self.dataset_path = Path(dataset_path)
        self.output_factor = output_factor
        self.augmentations = self.get_augmentation_pipeline()
    
    def get_augmentation_pipeline(self):
        """Define augmentation pipeline"""
        return Compose([
            HorizontalFlip(p=0.5),
            VerticalFlip(p=0.3),
            Rotate(limit=15, p=0.5),
            GaussNoise(p=0.3),
            Blur(blur_limit=3, p=0.3),
            RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
        ], bbox_params=BboxParams(
            format="yolo",
            label_fields=["class_labels"],   # ✅ FIX ADDED
            min_area=0,
            min_visibility=0
        ))
    
    def augment_image(self, image_path, label_path):
        """Augment single image and return variations"""
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Error reading {image_path}")
            return []
        
        # Read labels
        with open(label_path, 'r') as f:
            bboxes = [line.strip().split() for line in f.readlines()]
        
        augmented_samples = []
        
        for i in range(self.output_factor):
            try:
                # Apply augmentation
                classes = []
                bboxes_list = []

                for bbox in bboxes:
                    if len(bbox) < 5:
                        print(f"Warning: skipping invalid label line in {label_path}: {' '.join(bbox)}")
                        continue

                    classes.append(int(bbox[0]))
                    bboxes_list.append([float(x) for x in bbox[1:5]])

                if bboxes_list:
                    transformed = self.augmentations(
                        image=image,
                        bboxes=bboxes_list,
                        class_labels=classes   # ✅ FIX ADDED
                    )
                    aug_image = transformed['image']
                    aug_bboxes = transformed['bboxes']
                    aug_classes = transformed['class_labels']  # ✅ FIX ADDED
                else:
                    aug_image = self.augmentations(image=image)['image']
                    aug_bboxes = []
                    aug_classes = []
                
                augmented_samples.append((aug_image, aug_bboxes, aug_classes))
            except Exception as e:
                print(f"Error augmenting {image_path}: {e}")
                continue
        
        return augmented_samples
    
    def save_augmented_data(self, image_path, label_path, augmented_samples):
        """Save augmented images and labels"""
        image_name = image_path.stem
        image_ext = image_path.suffix
        label_dir = label_path.parent
        
        saved_files = []
        
        for i, (aug_image, aug_bboxes, classes) in enumerate(augmented_samples, 1):
            # Save image
            new_image_name = f"{image_name}_aug{i}{image_ext}"
            new_image_path = image_path.parent / new_image_name
            cv2.imwrite(str(new_image_path), aug_image)
            
            # Save labels
            new_label_name = f"{image_name}_aug{i}.txt"
            new_label_path = label_dir / new_label_name
            
            with open(new_label_path, 'w') as f:
                for bbox, class_id in zip(aug_bboxes, classes):
                    if len(bbox) == 4:
                        f.write(f"{int(class_id)} {bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}\n")
            
            saved_files.append((new_image_path, new_label_path))
        
        return saved_files
    
    def augment_dataset(self):
        """Augment entire dataset"""
        train_images = list((self.dataset_path / 'images' / 'train').glob('*.jpg'))
        train_images += list((self.dataset_path / 'images' / 'train').glob('*.png'))
        
        print(f"Found {len(train_images)} training images")
        
        augmented_count = 0
        
        for image_path in train_images:
            label_path = self.dataset_path / 'labels' / 'train' / f"{image_path.stem}.txt"
            
            if not label_path.exists():
                print(f"Warning: No labels for {image_path.name}")
                continue
            
            augmented_samples = self.augment_image(image_path, label_path)
            
            if augmented_samples:
                self.save_augmented_data(image_path, label_path, augmented_samples)
                augmented_count += len(augmented_samples)
                print(f"✓ Augmented {image_path.name}: {len(augmented_samples)} variations")
        
        print(f"\n✓ Total augmented: {augmented_count} images")
        print(f"✓ Dataset expanded to ~{len(train_images) * (1 + self.output_factor)} images")


if __name__ == "__main__":
    # Usage
    dataset_path = "./dataset"
    
    augmenter = RadiatorAugmenter(dataset_path, output_factor=3)
    augmenter.augment_dataset()
    
    print("\n✓ Augmentation complete!")