"""
ADE Design Hub Test Script
This script tests the core functionality of the Design Hub component
"""

import os
import sys
import json
from pathlib import Path

# Mock design data
SAMPLE_DESIGN = {
    "id": "test-design-001",
    "name": "Test Design",
    "description": "A test design for validation",
    "components": [
        {
            "id": "btn1",
            "type": "button",
            "props": {
                "text": "Click Me",
                "variant": "contained",
                "color": "primary"
            }
        },
        {
            "id": "txt1",
            "type": "textfield",
            "props": {
                "label": "Name",
                "placeholder": "Enter your name"
            }
        }
    ],
    "styles": [
        {
            "id": "primary-button",
            "name": "Primary Button",
            "properties": {
                "backgroundColor": "#1976d2",
                "color": "#ffffff",
                "borderRadius": "4px",
                "padding": "8px 16px"
            }
        }
    ],
    "pages": [
        {
            "id": "home",
            "name": "Home",
            "components": ["btn1", "txt1"]
        }
    ],
    "theme": {
        "palette": {
            "primary": "#1976d2",
            "secondary": "#dc004e",
            "background": "#f5f5f5",
            "text": "#333333"
        },
        "typography": {
            "fontFamily": "Roboto, sans-serif",
            "fontSize": 16
        }
    },
    "version": "1.0.0"
}

def save_design(design, output_dir="designs"):
    """Save a design to a JSON file"""
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Save the design to a JSON file
    file_path = os.path.join(output_dir, f"{design['id']}.json")
    with open(file_path, 'w') as f:
        json.dump(design, f, indent=2)
    
    print(f"Design saved to {file_path}")
    return file_path

def load_design(design_id, input_dir="designs"):
    """Load a design from a JSON file"""
    file_path = os.path.join(input_dir, f"{design_id}.json")
    
    if not os.path.exists(file_path):
        print(f"Design {design_id} not found")
        return None
    
    with open(file_path, 'r') as f:
        design = json.load(f)
    
    print(f"Design loaded from {file_path}")
    return design

def validate_design(design):
    """Validate a design"""
    # Check required fields
    required_fields = ["id", "name", "components", "styles", "pages", "theme", "version"]
    for field in required_fields:
        if field not in design:
            return False, f"Missing required field: {field}"
    
    # Check component references in pages
    component_ids = [comp["id"] for comp in design["components"]]
    for page in design["pages"]:
        for comp_id in page["components"]:
            if comp_id not in component_ids:
                return False, f"Page {page['id']} references non-existent component: {comp_id}"
    
    return True, "Design is valid"

def generate_code_from_design(design):
    """Generate React code from a design"""
    # Generate imports
    code = """import React from 'react';
import { Button, TextField, Box, Typography } from '@mui/material';

"""
    
    # Generate component
    code += f"const {design['name'].replace(' ', '')} = () => {{\n"
    code += "  return (\n"
    code += "    <Box sx={{ padding: '20px' }}>\n"
    
    # Add components based on the first page
    if design["pages"]:
        first_page = design["pages"][0]
        code += f"      <Typography variant=\"h4\">{first_page['name']}</Typography>\n"
        
        for comp_id in first_page["components"]:
            # Find the component
            component = next((c for c in design["components"] if c["id"] == comp_id), None)
            if component:
                if component["type"] == "button":
                    code += f"      <Button variant=\"{component['props'].get('variant', 'contained')}\" color=\"{component['props'].get('color', 'primary')}\">\n"
                    code += f"        {component['props'].get('text', 'Button')}\n"
                    code += "      </Button>\n"
                elif component["type"] == "textfield":
                    code += f"      <TextField label=\"{component['props'].get('label', '')}\" placeholder=\"{component['props'].get('placeholder', '')}\" fullWidth />\n"
    
    code += "    </Box>\n"
    code += "  );\n"
    code += "};\n\n"
    code += f"export default {design['name'].replace(' ', '')};\n"
    
    return code

def main():
    """Main function"""
    print("ADE Design Hub Test")
    print("=" * 50)
    
    # Save the sample design
    file_path = save_design(SAMPLE_DESIGN)
    
    # Load the design
    design = load_design("test-design-001")
    
    if design:
        # Validate the design
        is_valid, message = validate_design(design)
        print(f"Design validation: {'✅ PASS' if is_valid else '❌ FAIL'} - {message}")
        
        # Generate code from the design
        if is_valid:
            code = generate_code_from_design(design)
            print("\nGenerated React Component:")
            print("-" * 50)
            print(code)
            
            # Save the generated code
            code_path = "designs/TestDesign.jsx"
            with open(code_path, 'w') as f:
                f.write(code)
            print(f"\nCode saved to {code_path}")

if __name__ == "__main__":
    main()
