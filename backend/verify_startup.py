import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    import main
    print("Import successful")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Import failed: {e}")
    sys.exit(1)
