"""
ADE Validation Agent Test Script
This script tests the validation functionality of the Design Hub
"""

import os
import sys
import json
from pathlib import Path

def validate_component(component):
    """Validate a component"""
    issues = []
    
    # Check required fields
    required_fields = ["id", "type", "props"]
    for field in required_fields:
        if field not in component:
            issues.append(f"Component missing required field: {field}")
    
    # Validate specific component types
    if "type" in component:
        if component["type"] == "button":
            # Button-specific validation
            if "props" in component and "text" not in component["props"]:
                issues.append(f"Button component '{component['id']}' is missing 'text' property")
        
        elif component["type"] == "textfield":
            # TextField-specific validation
            if "props" in component and "label" not in component["props"]:
                issues.append(f"TextField component '{component['id']}' is missing 'label' property")
    
    return issues

def validate_style(style):
    """Validate a style"""
    issues = []
    
    # Check required fields
    required_fields = ["id", "name", "properties"]
    for field in required_fields:
        if field not in style:
            issues.append(f"Style missing required field: {field}")
    
    # Validate style properties
    if "properties" in style:
        properties = style["properties"]
        # Check for valid color formats in properties
        for prop, value in properties.items():
            if "color" in prop.lower() or "background" in prop.lower():
                if not (value.startswith("#") or value.startswith("rgb") or value.startswith("hsl")):
                    issues.append(f"Style '{style['id']}' has invalid color format for property '{prop}': {value}")
    
    return issues

def validate_design(design):
    """Validate a design and return validation results"""
    validation_results = {
        "isValid": True,
        "issues": [],
        "warnings": [],
        "suggestions": []
    }
    
    # Check required fields
    required_fields = ["id", "name", "components", "styles", "pages", "theme", "version"]
    for field in required_fields:
        if field not in design:
            validation_results["issues"].append(f"Design missing required field: {field}")
            validation_results["isValid"] = False
    
    # Validate components
    if "components" in design:
        for component in design["components"]:
            component_issues = validate_component(component)
            if component_issues:
                validation_results["issues"].extend(component_issues)
                validation_results["isValid"] = False
    
    # Validate styles
    if "styles" in design:
        for style in design["styles"]:
            style_issues = validate_style(style)
            if style_issues:
                validation_results["issues"].extend(style_issues)
                validation_results["isValid"] = False
    
    # Validate pages
    if "pages" in design and "components" in design:
        component_ids = [comp["id"] for comp in design["components"]]
        for page in design["pages"]:
            if "id" not in page:
                validation_results["issues"].append("Page missing 'id' field")
                validation_results["isValid"] = False
            
            if "components" not in page:
                validation_results["issues"].append(f"Page '{page.get('id', 'unknown')}' missing 'components' field")
                validation_results["isValid"] = False
            else:
                for comp_id in page["components"]:
                    if comp_id not in component_ids:
                        validation_results["issues"].append(f"Page '{page.get('id', 'unknown')}' references non-existent component: {comp_id}")
                        validation_results["isValid"] = False
    
    # Add suggestions for improvement
    if "components" in design and len(design["components"]) > 0:
        # Suggest adding more components for richer UI
        if len(design["components"]) < 3:
            validation_results["suggestions"].append("Consider adding more components to create a richer user interface")
        
        # Suggest using consistent naming conventions
        component_prefixes = set()
        for component in design["components"]:
            if "id" in component:
                prefix = ''.join([c for c in component["id"] if not c.isdigit()])
                component_prefixes.add(prefix)
        
        if len(component_prefixes) > 1:
            validation_results["suggestions"].append("Consider using consistent naming conventions for component IDs")
    
    # Add warnings about potential issues
    if "theme" in design and "palette" in design["theme"]:
        palette = design["theme"]["palette"]
        if "primary" in palette and "secondary" in palette:
            # Check for color contrast issues
            if palette["primary"] == palette["secondary"]:
                validation_results["warnings"].append("Primary and secondary colors are identical, which may cause visual confusion")
    
    return validation_results

def main():
    """Main function"""
    print("ADE Validation Agent Test")
    print("=" * 50)
    
    # Load the design
    design_path = "designs/test-design-001.json"
    if not os.path.exists(design_path):
        print(f"Design file not found: {design_path}")
        return
    
    with open(design_path, 'r') as f:
        design = json.load(f)
    
    print(f"Loaded design: {design['name']}")
    
    # Validate the design
    validation_results = validate_design(design)
    
    # Print validation results
    print("\nValidation Results:")
    print("-" * 50)
    print(f"Is Valid: {'✅ Yes' if validation_results['isValid'] else '❌ No'}")
    
    if validation_results["issues"]:
        print("\nIssues:")
        for issue in validation_results["issues"]:
            print(f"❌ {issue}")
    
    if validation_results["warnings"]:
        print("\nWarnings:")
        for warning in validation_results["warnings"]:
            print(f"⚠️ {warning}")
    
    if validation_results["suggestions"]:
        print("\nSuggestions:")
        for suggestion in validation_results["suggestions"]:
            print(f"💡 {suggestion}")
    
    # Save validation results
    results_path = "designs/validation-results.json"
    with open(results_path, 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\nValidation results saved to {results_path}")

if __name__ == "__main__":
    main()
