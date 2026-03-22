"""
Setup script for EPA (Emergent Prompt Architecture)
Initializes the system and runs basic verification
"""

import sys
import os


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ EPA requires Python 3.8 or higher")
        return False

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ["fastapi", "uvicorn", "pydantic"]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"   pip install {' '.join(missing_packages)}")
        print(f"   or: pip install -r requirements.txt")
        return False

    return True


def verify_epa_modules():
    """Verify EPA modules can be imported"""
    try:
        from epa import Onton, OntologicalLattice, GenesisAssembler, SafetyValidator
        from epa.config import SystemMode

        print("✅ EPA core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import EPA modules: {e}")
        return False


def run_basic_test():
    """Run a basic functionality test"""
    try:
        from epa import Onton, OntologicalLattice, GenesisAssembler, SafetyValidator
        from epa.onton import OntonType

        # Create test Onton
        test_onton = Onton(
            id="test_onton",
            content="Test content for EPA verification",
            type=OntonType.PERSONA,
            weight=0.8,
        )

        # Create lattice and add Onton
        lattice = OntologicalLattice()
        lattice.add_onton(test_onton)

        # Test query
        results = lattice.query("test")

        # Test assembler
        assembler = GenesisAssembler(lattice)
        result = assembler.crystallize("test input", "test_session")

        # Test safety validator
        safety = SafetyValidator()
        is_safe, reason = safety.validate_input("Hello, world!")

        print("✅ Basic functionality test passed")
        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Main setup routine"""
    print("🌌 EPA (Emergent Prompt Architecture) Setup")
    print("=" * 50)

    # Run checks
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Module Import", verify_epa_modules),
        ("Basic Functionality", run_basic_test),
    ]

    all_passed = True
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}:")
        if not check_func():
            all_passed = False

    if all_passed:
        print("\n🎉 EPA setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the demo: python demo.py")
        print("2. Start the API server: python api_server.py")
        print("3. Visit http://localhost:8000/docs for API documentation")
        return 0
    else:
        print("\n❌ EPA setup failed. Please resolve the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
