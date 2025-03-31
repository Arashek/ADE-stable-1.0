#!/usr/bin/env python
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    from src.core.providers import (
        ProviderRegistry,
        ModelRouter,
        Capability,
        ProviderConfig
    )
    print("✅ Provider Registry modules imported successfully")
    
    # Create a registry
    registry = ProviderRegistry()
    print("✅ Provider Registry initialized successfully")
    
    # Check default providers
    print(f"Default providers: {list(registry.providers.keys())}")
    
    print("\nVerification complete. Provider Registry structure is correctly set up.")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please check that all required files are correctly implemented.")
except Exception as e:
    print(f"❌ Error during verification: {e}") 