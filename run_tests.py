#!/usr/bin/env python3
"""Test runner script for PDF file renamer."""
import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run the complete test suite."""
    print("🧪 Running PDF File Renamer Test Suite")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    
    # Test commands to run
    test_commands = [
        # Run basic tests
        ["python", "-m", "pytest", "tests/", "-v"],
        
        # Run with coverage
        ["python", "-m", "pytest", "tests/", "--cov=file_renamer", "--cov-report=term-missing"],
        
        # Run performance tests (if they exist)
        ["python", "-m", "pytest", "tests/test_performance.py", "-v", "-m", "not slow"],
    ]
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n📋 Running test command {i}/{len(test_commands)}")
        print(f"Command: {' '.join(cmd)}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=False,
                check=False
            )
            
            if result.returncode != 0:
                print(f"❌ Test command {i} failed with exit code {result.returncode}")
                return False
            else:
                print(f"✅ Test command {i} passed")
                
        except Exception as e:
            print(f"❌ Error running test command {i}: {e}")
            return False
    
    print(f"\n🎉 All tests passed successfully!")
    return True


def install_test_dependencies():
    """Install test dependencies."""
    print("📦 Installing test dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-e", ".[test]"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Test dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install test dependencies: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main test runner."""
    print("PDF File Renamer - Test Runner")
    print("=" * 50)
    
    # Check if we should install dependencies
    if "--install" in sys.argv:
        if not install_test_dependencies():
            sys.exit(1)
    
    # Run tests
    if not run_tests():
        sys.exit(1)


if __name__ == "__main__":
    main()