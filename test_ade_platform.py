"""
ADE Platform Test Script
This script tests the core functionality of the ADE platform using Python requests
"""

import os
import sys
import json
import time
import requests
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_DESIGN = {
    "name": "Test Dashboard",
    "description": "A test dashboard design for validation",
    "components": [
        {
            "id": "header1",
            "type": "header",
            "props": {
                "title": "Dashboard",
                "showLogo": True
            }
        },
        {
            "id": "chart1",
            "type": "chart",
            "props": {
                "type": "bar",
                "data": {
                    "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
                    "datasets": [
                        {
                            "label": "Sales",
                            "data": [12, 19, 3, 5, 2]
                        }
                    ]
                }
            }
        },
        {
            "id": "table1",
            "type": "table",
            "props": {
                "headers": ["Name", "Email", "Status"],
                "rows": [
                    ["John Doe", "john@example.com", "Active"],
                    ["Jane Smith", "jane@example.com", "Inactive"]
                ]
            }
        }
    ],
    "styles": [
        {
            "id": "header-style",
            "name": "Header Style",
            "properties": {
                "backgroundColor": "#2196f3",
                "color": "#ffffff",
                "padding": "16px"
            }
        },
        {
            "id": "chart-style",
            "name": "Chart Style",
            "properties": {
                "backgroundColor": "#ffffff",
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                "padding": "16px"
            }
        }
    ],
    "pages": [
        {
            "id": "dashboard",
            "name": "Dashboard",
            "components": ["header1", "chart1", "table1"]
        }
    ],
    "theme": {
        "palette": {
            "primary": "#2196f3",
            "secondary": "#f50057",
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

def check_backend_status():
    """Check if the backend server is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            return True
        else:
            print(f"❌ Backend server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend server: {str(e)}")
        return False

def test_design_creation():
    """Test creating a new design"""
    print("\n--- Testing Design Creation ---")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/designs",
            json=TEST_DESIGN,
            timeout=10
        )
        
        if response.status_code in (200, 201):
            design = response.json()
            print(f"✅ Design created successfully with ID: {design.get('id')}")
            return design
        else:
            print(f"❌ Failed to create design: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating design: {str(e)}")
        return None

def test_design_validation(design):
    """Test design validation"""
    print("\n--- Testing Design Validation ---")
    if not design:
        print("❌ No design to validate")
        return None
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/validation/design",
            json=design,
            timeout=10
        )
        
        if response.status_code == 200:
            validation_result = response.json()
            print(f"✅ Design validation completed")
            print(f"Valid: {validation_result.get('isValid', False)}")
            
            if validation_result.get('issues'):
                print("\nIssues:")
                for issue in validation_result.get('issues', []):
                    print(f"- {issue}")
            
            if validation_result.get('warnings'):
                print("\nWarnings:")
                for warning in validation_result.get('warnings', []):
                    print(f"- {warning}")
            
            if validation_result.get('suggestions'):
                print("\nSuggestions:")
                for suggestion in validation_result.get('suggestions', []):
                    print(f"- {suggestion}")
            
            return validation_result
        else:
            print(f"❌ Failed to validate design: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error validating design: {str(e)}")
        return None

def test_code_generation(design):
    """Test code generation from design"""
    print("\n--- Testing Code Generation ---")
    if not design:
        print("❌ No design to generate code from")
        return None
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/designs/generate-code",
            json=design,
            timeout=30
        )
        
        if response.status_code == 200:
            code_result = response.json()
            print(f"✅ Code generation completed")
            
            # Save the generated code to a file
            code_dir = "generated_code"
            os.makedirs(code_dir, exist_ok=True)
            
            code_file = os.path.join(code_dir, f"{design.get('name', 'design').replace(' ', '')}.jsx")
            with open(code_file, 'w') as f:
                f.write(code_result.get('code', ''))
            
            print(f"✅ Generated code saved to {code_file}")
            return code_result
        else:
            print(f"❌ Failed to generate code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error generating code: {str(e)}")
        return None

def test_agent_capabilities():
    """Test agent capabilities"""
    print("\n--- Testing Agent Capabilities ---")
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/agents/capabilities",
            timeout=10
        )
        
        if response.status_code == 200:
            capabilities = response.json()
            print(f"✅ Agent capabilities retrieved")
            
            print("\nAvailable Agents:")
            for agent, capabilities in capabilities.items():
                print(f"\n{agent}:")
                for capability in capabilities:
                    print(f"- {capability}")
            
            return capabilities
        else:
            print(f"❌ Failed to get agent capabilities: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting agent capabilities: {str(e)}")
        return None

def run_local_tests():
    """Run local tests without requiring the backend server"""
    print("\n--- Running Local Tests ---")
    
    # Test design validation locally
    from test_validation_agent import validate_design
    validation_results = validate_design(TEST_DESIGN)
    
    print("\nLocal Design Validation:")
    print(f"Valid: {validation_results.get('isValid', False)}")
    
    if validation_results.get('issues'):
        print("\nIssues:")
        for issue in validation_results.get('issues', []):
            print(f"- {issue}")
    
    if validation_results.get('warnings'):
        print("\nWarnings:")
        for warning in validation_results.get('warnings', []):
            print(f"- {warning}")
    
    if validation_results.get('suggestions'):
        print("\nSuggestions:")
        for suggestion in validation_results.get('suggestions', []):
            print(f"- {suggestion}")
    
    # Test code generation locally
    from test_design_agent import DesignAgent
    
    agent = DesignAgent()
    code = agent.generate_code(TEST_DESIGN)
    
    print("\nLocal Code Generation:")
    print(f"✅ Code generated successfully")

def main():
    """Main function"""
    print("ADE Platform Test")
    print("=" * 50)
    
    # Check if backend server is running
    backend_running = check_backend_status()
    
    if backend_running:
        # Run tests against the backend API
        design = test_design_creation()
        if design:
            validation_result = test_design_validation(design)
            code_result = test_code_generation(design)
        
        # Test agent capabilities
        agent_capabilities = test_agent_capabilities()
    else:
        print("\n⚠️ Backend server is not running. Running local tests instead.")
        run_local_tests()
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
