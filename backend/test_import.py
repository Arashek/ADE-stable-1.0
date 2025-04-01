try:
    import sys
    import traceback
    
    print("Starting import test...")
    
    # Try importing individual components first
    print("Testing owner_panel_routes import...")
    from routes.owner_panel_routes import router as owner_panel_router
    print("Owner panel routes import successful")
    
    print("Testing owner_panel_service import...")
    from services.owner_panel_service import OwnerPanelService
    print("Owner panel service import successful")
    
    print("Testing coordination imports...")
    from services.coordination.agent_coordinator import AgentCoordinator
    print("Agent coordinator import successful")
    
    # Try importing the main module
    print("Testing main module import...")
    import main
    print("Main module import successful")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print("Traceback:")
    traceback.print_exc()
