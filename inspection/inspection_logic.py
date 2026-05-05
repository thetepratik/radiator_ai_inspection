"""
Radiator Inspection Logic Engine
Applies business rules to component detections to determine OK/NOT OK status
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import json
from datetime import datetime

@dataclass
class Detection:
    """Component detection result"""
    class_name: str
    confidence: float
    bbox: Tuple[float, float, float, float]  # x_center, y_center, width, height


class InspectionEngine:
    """Main inspection logic engine"""
    
    def __init__(self, config: Dict = None):
        """
        Initialize inspection engine
        
        Args:
            config: Configuration dictionary with inspection rules
        """
        self.config = config or self.default_config()
        self.all_required_components = self.config.get('required_components', [])
        self.min_confidence = self.config.get('min_confidence', 0.5)
        self.max_defects = self.config.get('max_defects', 0)
        self.views = self.config.get('views', {})
    
    @staticmethod
    def default_config():
        """Default inspection configuration"""
        return {
            'required_components': ['fan', 'pipe', 'connector'],
            'min_confidence': 0.5,
            'max_defects': 0,
            'component_rules': {
                'fan': {'required': True, 'min_count': 1},
                'pipe': {'required': True, 'min_count': 2},
                'connector': {'required': True, 'min_count': 1},
                'drain_plug': {'required': True, 'min_count': 1},
                'rubber_grommet': {'required': True, 'min_count': 3},
                'clip': {'required': True, 'min_count': 4},
                'radiator_fin': {'required': False, 'min_count': 0},
            },
            'damage_detection': {
                'radiator_fin': {'max_damage_ratio': 0.1},  # Allow up to 10% damaged
                'pipe': {'max_damage_ratio': 0.0},  # No damage allowed
            }
        }
    
    def check_component_presence(self, detections: List[Detection], view: str = None) -> Dict:
        """
        Check if all required components are present
        
        Args:
            detections: List of detected components
            view: Optional specific view/side to check against
            
        Returns:
            Dictionary with component presence check results
        """
        # Determine required components for this view
        required_components = self.all_required_components
        if view and view in self.views:
            required_components = self.views[view].get('required_components', required_components)
        elif view == 'default':
            required_components = self.all_required_components
        component_counts = {}
        component_detections = {}
        
        # Count detections per component
        for detection in detections:
            if detection.confidence >= self.min_confidence:
                component_counts[detection.class_name] = component_counts.get(detection.class_name, 0) + 1
                if detection.class_name not in component_detections:
                    component_detections[detection.class_name] = []
                component_detections[detection.class_name].append(detection)
        
        results = {
            'present_components': {},
            'missing_components': [],
            'count_mismatches': [],
            'all_required_present': True
        }
        
        # Check each required component
        for component in required_components:
            count = component_counts.get(component, 0)
            min_required = self.config['component_rules'].get(component, {}).get('min_count', 1)
            
            if count > 0:
                results['present_components'][component] = {
                    'count': count,
                    'expected': min_required,
                    'status': 'OK' if count >= min_required else 'COUNT_MISMATCH',
                    'confidence': max([d.confidence for d in component_detections[component]])
                }
                
                if count < min_required:
                    results['count_mismatches'].append(component)
                    results['all_required_present'] = False
            else:
                results['missing_components'].append(component)
                results['all_required_present'] = False
        
        return results
    
    def check_component_condition(self, detections: List[Detection]) -> Dict:
        """
        Check condition of components for defects
        
        Args:
            detections: List of detected components
            
        Returns:
            Dictionary with component condition check results
        """
        condition_results = {
            'damaged_components': [],
            'normal_components': [],
            'total_defects': 0
        }
        
        # For now, we assume detections are normal components
        # In a real scenario, you'd have separate detections for damaged parts
        
        for detection in detections:
            if detection.confidence >= self.min_confidence:
                condition_results['normal_components'].append({
                    'component': detection.class_name,
                    'confidence': detection.confidence
                })
        
        return condition_results
    
    def check_installation_rules(self, detections: List[Detection]) -> Dict:
        """
        Check if components are installed correctly
        
        Args:
            detections: List of detected components
            
        Returns:
            Dictionary with installation check results
        """
        installation_results = {
            'correct_installation': True,
            'issues': []
        }
        
        # Rule 1: Pipe routing check (pipes should be in valid positions)
        pipes = [d for d in detections if d.class_name == 'pipe' and d.confidence >= self.min_confidence]
        if pipes:
            # Check if pipes are properly spaced
            positions = [p.bbox[1] for p in pipes]  # Y-center positions
            if len(positions) > 1:
                min_spacing = 0.1  # Minimum 10% vertical spacing
                for i in range(len(positions) - 1):
                    if abs(positions[i] - positions[i+1]) < min_spacing:
                        installation_results['issues'].append({
                            'issue': 'Improper pipe spacing',
                            'severity': 'WARNING'
                        })
        
        # Rule 2: Connector positioning (should be near top)
        connectors = [d for d in detections if d.class_name == 'connector' and d.confidence >= self.min_confidence]
        if connectors:
            for conn in connectors:
                if conn.bbox[1] > 0.7:  # Connector Y-position > 70% means it's too low
                    installation_results['issues'].append({
                        'issue': 'Connector positioned incorrectly',
                        'severity': 'WARNING'
                    })
        
        # Rule 3: Drain plug should be at bottom
        drain_plugs = [d for d in detections if d.class_name == 'drain_plug' and d.confidence >= self.min_confidence]
        if drain_plugs:
            for plug in drain_plugs:
                if plug.bbox[1] < 0.6:  # Drain plug Y-position < 60% means it's too high
                    installation_results['issues'].append({
                        'issue': 'Drain plug positioned incorrectly',
                        'severity': 'ERROR'
                    })
                    installation_results['correct_installation'] = False
        
        return installation_results
    
    def generate_final_decision(self, detections: List[Detection], view: str = None) -> Dict:
        """
        Generate final OK/NOT OK decision based on all checks
        
        Args:
            detections: List of detected components
            view: Optional specific view/side to check against
            
        Returns:
            Final inspection result dictionary
        """
        # Perform all checks
        presence_check = self.check_component_presence(detections, view=view)
        condition_check = self.check_component_condition(detections)
        installation_check = self.check_installation_rules(detections)
        
        # Determine final status
        final_status = "OK"
        failures = []
        warnings = []
        
        # Check 1: All required components present
        if not presence_check['all_required_present']:
            final_status = "NOT OK"
            if presence_check['missing_components']:
                failures.append(f"Missing components: {', '.join(presence_check['missing_components'])}")
            if presence_check['count_mismatches']:
                failures.append(f"Component count mismatch: {', '.join(presence_check['count_mismatches'])}")
        
        # Check 2: Component condition
        if condition_check['total_defects'] > self.max_defects:
            final_status = "NOT OK"
            failures.append(f"Too many defects detected: {condition_check['total_defects']} (max: {self.max_defects})")
        
        # Check 3: Installation
        if not installation_check['correct_installation']:
            final_status = "NOT OK"
            for issue in installation_check['issues']:
                if issue['severity'] == 'ERROR':
                    failures.append(issue['issue'])
                else:
                    warnings.append(issue['issue'])
        
        # Build result
        result = {
            'status': final_status,
            'timestamp': datetime.now().isoformat(),
            'component_presence': presence_check,
            'component_condition': condition_check,
            'installation_check': installation_check,
            'failures': failures,
            'warnings': warnings,
            'confidence_score': self.calculate_confidence(detections)
        }
        
        return result
    
    def calculate_confidence(self, detections: List[Detection]) -> float:
        """Calculate overall confidence score"""
        if not detections:
            return 0.0
        
        valid_detections = [d for d in detections if d.confidence >= self.min_confidence]
        if not valid_detections:
            return 0.0
        
        return sum(d.confidence for d in valid_detections) / len(valid_detections)
    
    def format_inspection_report(self, detections: List[Detection]) -> str:
        """Generate human-readable inspection report"""
        result = self.generate_final_decision(detections)
        
        report = []
        report.append("="*60)
        report.append("RADIATOR INSPECTION REPORT")
        report.append("="*60)
        report.append(f"Timestamp: {result['timestamp']}")
        report.append(f"Final Status: {result['status']}")
        report.append(f"Confidence: {result['confidence_score']:.2%}")
        report.append("")
        
        # Component presence
        report.append("COMPONENT PRESENCE CHECK:")
        report.append("-"*60)
        for component, details in result['component_presence']['present_components'].items():
            status_icon = "✓" if details['status'] == 'OK' else "✗"
            report.append(f"  {status_icon} {component.upper()}: {details['count']} detected (expected: {details['expected']}, confidence: {details['confidence']:.2%})")
        
        if result['component_presence']['missing_components']:
            for component in result['component_presence']['missing_components']:
                report.append(f"  ✗ {component.upper()}: MISSING")
        report.append("")
        
        # Installation check
        if result['installation_check']['issues']:
            report.append("INSTALLATION ISSUES:")
            report.append("-"*60)
            for issue in result['installation_check']['issues']:
                report.append(f"  [{issue['severity']}] {issue['issue']}")
            report.append("")
        
        # Final verdict
        report.append("FINAL VERDICT:")
        report.append("-"*60)
        if result['status'] == 'OK':
            report.append("✓ RADIATOR PASSED INSPECTION")
        else:
            report.append("✗ RADIATOR FAILED INSPECTION")
            if result['failures']:
                report.append("\nFailure reasons:")
                for failure in result['failures']:
                    report.append(f"  - {failure}")
        
        if result['warnings']:
            report.append("\nWarnings:")
            for warning in result['warnings']:
                report.append(f"  ⚠ {warning}")
        
        report.append("="*60)
        
        return "\n".join(report)


# Example usage
def test_inspection_engine():
    """Test the inspection engine"""
    
    # Create mock detections
    detections = [
        Detection('fan', 0.92, (0.5, 0.3, 0.3, 0.4)),
        Detection('pipe', 0.85, (0.3, 0.5, 0.2, 0.5)),
        Detection('pipe', 0.88, (0.7, 0.6, 0.2, 0.5)),
        Detection('connector', 0.95, (0.5, 0.1, 0.15, 0.1)),
        Detection('drain_plug', 0.78, (0.5, 0.9, 0.1, 0.08)),
        Detection('rubber_grommet', 0.82, (0.2, 0.4, 0.08, 0.08)),
        Detection('rubber_grommet', 0.80, (0.8, 0.4, 0.08, 0.08)),
        Detection('rubber_grommet', 0.79, (0.5, 0.7, 0.08, 0.08)),
        Detection('clip', 0.90, (0.1, 0.2, 0.06, 0.06)),
        Detection('clip', 0.88, (0.9, 0.2, 0.06, 0.06)),
        Detection('clip', 0.87, (0.1, 0.8, 0.06, 0.06)),
        Detection('clip', 0.89, (0.9, 0.8, 0.06, 0.06)),
    ]
    
    engine = InspectionEngine()
    report = engine.format_inspection_report(detections)
    print(report)
    
    result = engine.generate_final_decision(detections)
    print("\nJSON Result:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    test_inspection_engine()
