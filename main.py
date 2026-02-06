"""
Entry point voor Sint Maarten Campus Autologin Tool
"""
import sys
from pathlib import Path

# Add current directory to path
SCRIPTS_DIR = Path(__file__).parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# Import and run main from desktop_app
from src.web.desktop_app import main

if __name__ == "__main__":
    main()
