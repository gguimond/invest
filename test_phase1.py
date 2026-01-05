#!/usr/bin/env python3
"""
Test script to verify Phase 1 installation
Tests without downloading full 20 years of data
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError as e:
        print(f"✗ pandas: {e}")
        return False
    
    try:
        import numpy
        print("✓ numpy")
    except ImportError as e:
        print(f"✗ numpy: {e}")
        return False
    
    try:
        import yfinance
        print("✓ yfinance")
    except ImportError as e:
        print(f"✗ yfinance: {e}")
        return False
    
    try:
        from rich.console import Console
        print("✓ rich")
    except ImportError as e:
        print(f"✗ rich: {e}")
        return False
    
    try:
        import click
        print("✓ click")
    except ImportError as e:
        print(f"✗ click: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv")
    except ImportError as e:
        print(f"✗ python-dotenv: {e}")
        return False
    
    return True

def test_project_structure():
    """Test that project structure is correct"""
    print("\nTesting project structure...")
    
    required_files = [
        "invest_advisor.py",
        "requirements.txt",
        "README.md",
        ".gitignore",
        ".env.example",
        "src/__init__.py",
        "src/config.py",
        "src/database.py",
        "src/data_collector.py",
    ]
    
    required_dirs = [
        "data",
        "reports",
        "src"
    ]
    
    base_dir = Path(__file__).parent
    
    for file in required_files:
        if (base_dir / file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} - MISSING")
            return False
    
    for dir in required_dirs:
        if (base_dir / dir).is_dir():
            print(f"✓ {dir}/")
        else:
            print(f"✗ {dir}/ - MISSING")
            return False
    
    return True

def test_modules():
    """Test that our modules can be imported"""
    print("\nTesting custom modules...")
    
    try:
        from src import config
        print("✓ src.config")
    except Exception as e:
        print(f"✗ src.config: {e}")
        return False
    
    try:
        from src import database
        print("✓ src.database")
    except Exception as e:
        print(f"✗ src.database: {e}")
        return False
    
    try:
        from src import data_collector
        print("✓ src.data_collector")
    except Exception as e:
        print(f"✗ src.data_collector: {e}")
        return False
    
    return True

def test_database_creation():
    """Test database creation (without data)"""
    print("\nTesting database creation...")
    
    try:
        from src.database import Database
        from src.config import DATA_DIR
        
        test_db = DATA_DIR / "test.db"
        
        # Remove test db if exists
        if test_db.exists():
            test_db.unlink()
        
        with Database(str(test_db)) as db:
            db.initialize_schema()
            
            if db.database_exists():
                print("✓ Database creation successful")
                
                # Clean up
                test_db.unlink()
                return True
            else:
                print("✗ Database creation failed")
                return False
                
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Phase 1 Installation Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Custom Modules", test_modules),
        ("Database Creation", test_database_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Phase 1 installation complete.")
        print("\nNext steps:")
        print("  1. Run: python invest_advisor.py --init")
        print("     (Downloads 20 years of market data)")
        print("  2. Run: python invest_advisor.py --stats")
        print("     (View database statistics)")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        print("\nMake sure you've run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
