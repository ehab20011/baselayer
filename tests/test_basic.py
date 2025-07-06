"""
Basic tests to verify project structure and imports work correctly
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that we can import the main modules"""
    try:
        from models import PPPLoanDataSchema
        assert PPPLoanDataSchema is not None
    except ImportError as e:
        pytest.fail(f"Failed to import PPPLoanDataSchema: {e}")

def test_python_version():
    """Test that we're running a supported Python version"""
    assert sys.version_info >= (3, 8), "Python 3.8+ required"

def test_project_structure():
    """Test that key project files exist"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_files = [
        "requirements.txt",
        "models.py",
        "server.py",
        "run.py"
    ]
    
    for file_path in required_files:
        full_path = os.path.join(project_root, file_path)
        assert os.path.exists(full_path), f"Required file {file_path} not found"

def test_requirements_file():
    """Test that requirements.txt contains expected dependencies"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_path = os.path.join(project_root, "requirements.txt")
    
    with open(requirements_path, 'r') as f:
        requirements = f.read().lower()
    
    expected_deps = ["fastapi", "uvicorn", "pydantic", "sqlalchemy", "pytest"]
    
    for dep in expected_deps:
        assert dep in requirements, f"Expected dependency {dep} not found in requirements.txt" 