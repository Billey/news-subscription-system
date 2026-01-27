try:
    from flask import Flask
    print("✅ Flask is available")
    print(f"Flask version: {Flask.__version__}")
except ImportError as e:
    print(f"❌ Flask import error: {e}")
    import sys
    print(f"Python path: {sys.path}")
