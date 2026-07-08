"""
Quick Start Workflow Script
Guides you through the entire process step-by-step
"""

import os
import sys
from pathlib import Path
import subprocess

class WorkflowGuide:
    """Interactive workflow guide"""
    
    def __init__(self):
        self.steps = [
            {
                'name': 'Setup Environment',
                'description': 'Create Python virtual environment and install dependencies',
                'commands': [
                    'python -m venv venv',
                    'pip install --upgrade pip',
                    'pip install -r requirements.txt'
                ],
                'verify': 'python -c "import torch, cv2, ultralytics; print(\"✓ All packages ready\")"'
            },
            {
                'name': 'Organize Images',
                'description': 'Sort your 300 images into train/val/test folders',
                'commands': ['python organize_dataset.py'],
                'verify': 'ls dataset/images/train/ | wc -l'
            },
            {
                'name': 'Annotate Images',
                'description': 'Add bounding boxes to all images using Label Studio or CVAT',
                'commands': ['label-studio'],  # or CVAT
                'manual': True,
                'duration': '3-4 days',
                'guide': 'ANNOTATION_GUIDE.md'
            },
            {
                'name': 'Validate Labels',
                'description': 'Check that all labels are in correct format',
                'commands': ['python validate_labels.py'],
                'verify': 'grep -r "class" dataset/labels/train/ | head -5'
            },
            {
                'name': 'Augment Dataset',
                'description': 'Expand dataset 3x using image augmentation',
                'commands': ['python augment_dataset.py'],
                'verify': 'ls dataset/images/train/ | wc -l'
            },
            {
                'name': 'Train Model',
                'description': 'Train YOLOv8 model on your annotated data',
                'commands': ['python train_model.py'],
                'duration': '1-3 hours (GPU) or 8+ hours (CPU)',
                'verify': 'ls models/radiator_detector/weights/best.pt'
            },
            {
                'name': 'Start Backend API',
                'description': 'Launch FastAPI server for inference',
                'commands': ['python server.py'],
                'note': 'Keep this running in a separate terminal'
            },
            {
                'name': 'Start Web UI',
                'description': 'Launch Streamlit interface',
                'commands': ['streamlit run streamlit_app.py'],
                'note': 'Open http://localhost:8501 in browser'
            }
        ]
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print("🚀 RADIATOR AI INSPECTION SYSTEM - QUICK START GUIDE")
        print("="*70)
        print("\nYour Situation:")
        print("  ✓ 300 images available")
        print("  ✓ Organized by view (front/back/side/top)")
        print("  ✓ Stored locally")
        print("  ❌ Not yet annotated")
        print("\nTimeline: 5-7 days")
        print("  Day 1: Setup (30 min)")
        print("  Days 2-4: Annotation (3 days)")
        print("  Day 5: Validate & Augment (2 hours)")
        print("  Day 6: Train (1-3 hours)")
        print("  Day 7: Deploy (30 min)")
        print("="*70 + "\n")
    
    def show_step(self, step_num, step):
        """Display step information"""
        print(f"\n{'='*70}")
        print(f"STEP {step_num}/{len(self.steps)}: {step['name'].upper()}")
        print(f"{'='*70}")
        print(f"\n📝 Description:")
        print(f"   {step['description']}")
        
        if 'duration' in step:
            print(f"\n⏱️  Expected Duration: {step['duration']}")
        
        if 'manual' in step and step['manual']:
            print(f"\n⚠️  Manual Step Required!")
            if 'guide' in step:
                print(f"📖 Read: {step['guide']}")
            return False
        
        print(f"\n🔧 Commands to Run:")
        for cmd in step['commands']:
            print(f"   $ {cmd}")
        
        if 'verify' in step:
            print(f"\n✓ Verification Command:")
            print(f"   $ {step['verify']}")
        
        if 'note' in step:
            print(f"\n💡 Note: {step['note']}")
        
        return True
    
    def run_workflow(self):
        """Run the complete workflow"""
        self.print_banner()
        
        print("\n🎯 Workflow Steps:\n")
        for i, step in enumerate(self.steps, 1):
            status = "⏳ Pending" if i > 1 else "🟢 Current"
            manual = " (Manual)" if 'manual' in step and step['manual'] else ""
            print(f"  {i}. [{status}] {step['name']}{manual}")
        
        print("\n" + "="*70)
        print("Starting workflow...\n")
        
        for step_num, step in enumerate(self.steps, 1):
            # Show step info
            is_automatic = self.show_step(step_num, step)
            
            # Ask user
            if is_automatic:
                print(f"\n{'─'*70}")
                proceed = input("\n👉 Ready to run this step? (yes/skip/quit): ").lower().strip()
                
                if proceed == 'quit':
                    print("\n❌ Workflow cancelled")
                    return
                elif proceed == 'skip':
                    print("\n⏭️  Skipped this step")
                    continue
                elif proceed == 'yes':
                    print("\n⏳ Running commands...\n")
                    self.run_commands(step['commands'])
                    
                    # Verify
                    if 'verify' in step:
                        print(f"\n✓ Verifying...")
                        self.run_commands([step['verify']])
                else:
                    print("⚠️  Please enter: yes, skip, or quit")
                    step_num -= 1
                    continue
            else:
                # Manual step
                print(f"\n{'─'*70}")
                proceed = input("\n👉 Completed this step? (yes/quit): ").lower().strip()
                
                if proceed == 'quit':
                    print("\n❌ Workflow cancelled")
                    return
                elif proceed == 'yes':
                    print("\n✓ Moving to next step...")
                else:
                    print("⚠️  Please enter: yes or quit")
                    step_num -= 1
                    continue
            
            print(f"\n✅ Step {step_num} complete!\n")
        
        # Final message
        print("\n" + "="*70)
        print("🎉 WORKFLOW COMPLETE!")
        print("="*70)
        print("\nYour radiator inspection system is ready!")
        print("\nAccess:")
        print("  🌐 Web UI: http://localhost:8501")
        print("  📡 API: http://localhost:8000")
        print("  📚 API Docs: http://localhost:8000/docs")
        print("\nNext:")
        print("  1. Upload a radiator image")
        print("  2. System will detect components")
        print("  3. Get OK/NOT OK decision with details")
        print("\nCongratulations! 🎊")
        print("="*70 + "\n")
    
    def run_commands(self, commands):
        """Execute shell commands"""
        for cmd in commands:
            print(f"$ {cmd}")
            result = os.system(cmd)
            if result != 0:
                print(f"\n⚠️  Command failed with code {result}")
                retry = input("Retry? (yes/skip): ").lower().strip()
                if retry == 'yes':
                    self.run_commands([cmd])
                else:
                    print("Skipped")
            print()


def main():
    """Main entry point"""
    try:
        guide = WorkflowGuide()
        guide.run_workflow()
    except KeyboardInterrupt:
        print("\n\n❌ Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
