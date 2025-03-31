import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

def test_check_python_installation():
    """Test Python installation check."""
    with patch('subprocess.run') as mock_run:
        # Test Python found
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = b"Python 3.8.0"
        assert check_python_installation() is True
        
        # Test Python not found
        mock_run.return_value.returncode = 1
        assert check_python_installation() is False

def test_check_virtual_environment():
    """Test virtual environment check."""
    with patch('os.path.exists') as mock_exists:
        # Test venv exists
        mock_exists.return_value = True
        assert check_virtual_environment() is True
        
        # Test venv doesn't exist
        mock_exists.return_value = False
        assert check_virtual_environment() is False

def test_create_virtual_environment():
    """Test virtual environment creation."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        assert create_virtual_environment() is True
        
        mock_run.return_value.returncode = 1
        assert create_virtual_environment() is False

def test_install_dependencies():
    """Test dependency installation."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        assert install_dependencies() is True
        
        mock_run.return_value.returncode = 1
        assert install_dependencies() is False

def test_check_aws_credentials():
    """Test AWS credentials check."""
    with patch('os.path.exists') as mock_exists:
        # Test credentials exist
        mock_exists.return_value = True
        assert check_aws_credentials() is True
        
        # Test credentials don't exist
        mock_exists.return_value = False
        assert check_aws_credentials() is False

def test_check_gcp_credentials():
    """Test Google Cloud credentials check."""
    with patch('os.path.exists') as mock_exists:
        # Test credentials exist
        mock_exists.return_value = True
        assert check_gcp_credentials() is True
        
        # Test credentials don't exist
        mock_exists.return_value = False
        assert check_gcp_credentials() is False

def test_check_ade_integration():
    """Test ADE integration configuration check."""
    with patch('os.path.exists') as mock_exists:
        # Test config exists
        mock_exists.return_value = True
        assert check_ade_integration() is True
        
        # Test config doesn't exist
        mock_exists.return_value = False
        assert check_ade_integration() is False

def test_create_aws_credentials():
    """Test AWS credentials file creation."""
    with patch('builtins.open', create=True) as mock_open:
        assert create_aws_credentials() is True
        mock_open.assert_called_once()

def test_create_gcp_credentials():
    """Test Google Cloud credentials file creation."""
    with patch('builtins.open', create=True) as mock_open:
        assert create_gcp_credentials() is True
        mock_open.assert_called_once()

def test_create_ade_integration():
    """Test ADE integration configuration file creation."""
    with patch('builtins.open', create=True) as mock_open:
        assert create_ade_integration() is True
        mock_open.assert_called_once()

def test_start_services():
    """Test starting all services."""
    with patch('subprocess.Popen') as mock_popen:
        mock_popen.return_value = MagicMock()
        assert start_services() is True
        
        mock_popen.side_effect = Exception("Test error")
        assert start_services() is False

def test_open_browser():
    """Test opening web browser."""
    with patch('webbrowser.open') as mock_open:
        mock_open.return_value = True
        assert open_browser() is True
        
        mock_open.return_value = False
        assert open_browser() is False

def test_main_success():
    """Test successful main execution."""
    with patch('ade_model_training.tests.test_launch.check_python_installation', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_virtual_environment', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_aws_credentials', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_gcp_credentials', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_ade_integration', return_value=True), \
         patch('ade_model_training.tests.test_launch.start_services', return_value=True), \
         patch('ade_model_training.tests.test_launch.open_browser', return_value=True):
        
        from ade_model_training.tests.test_launch import main
        assert main() == 0

def test_main_python_not_found():
    """Test main execution with Python not found."""
    with patch('ade_model_training.tests.test_launch.check_python_installation', return_value=False):
        from ade_model_training.tests.test_launch import main
        assert main() == 1

def test_main_venv_creation_failed():
    """Test main execution with virtual environment creation failure."""
    with patch('ade_model_training.tests.test_launch.check_python_installation', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_virtual_environment', return_value=False), \
         patch('ade_model_training.tests.test_launch.create_virtual_environment', return_value=False):
        
        from ade_model_training.tests.test_launch import main
        assert main() == 1

def test_main_dependency_installation_failed():
    """Test main execution with dependency installation failure."""
    with patch('ade_model_training.tests.test_launch.check_python_installation', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_virtual_environment', return_value=True), \
         patch('ade_model_training.tests.test_launch.install_dependencies', return_value=False):
        
        from ade_model_training.tests.test_launch import main
        assert main() == 1

def test_main_service_start_failed():
    """Test main execution with service start failure."""
    with patch('ade_model_training.tests.test_launch.check_python_installation', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_virtual_environment', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_aws_credentials', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_gcp_credentials', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_ade_integration', return_value=True), \
         patch('ade_model_training.tests.test_launch.start_services', return_value=False):
        
        from ade_model_training.tests.test_launch import main
        assert main() == 1

def test_main_browser_open_failed():
    """Test main execution with browser open failure."""
    with patch('ade_model_training.tests.test_launch.check_python_installation', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_virtual_environment', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_aws_credentials', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_gcp_credentials', return_value=True), \
         patch('ade_model_training.tests.test_launch.check_ade_integration', return_value=True), \
         patch('ade_model_training.tests.test_launch.start_services', return_value=True), \
         patch('ade_model_training.tests.test_launch.open_browser', return_value=False):
        
        from ade_model_training.tests.test_launch import main
        assert main() == 1 