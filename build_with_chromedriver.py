#!/usr/bin/env python3
"""
Build script voor Sint Maarten Campus Autologin Tool

webdriver_manager handelt chromedriver beheer automatisch af.
Dit script runnen: python build_with_chromedriver.py
"""
import os
import sys
from pathlib import Path

def main():
    scripts_dir = Path(__file__).parent

    print("Build script voor Sint Maarten Campus Autologin Tool v2.0.3")
    print("=" * 60)
    print("✓ webdriver_manager staat in requirements.txt")
    print("✓ ChromeDriverManager is geïntegreerd in browser_session.py")
    print("✓ ChromeDriver wordt automatisch gedownload bij eerste use")
    print("=" * 60)

    # Zorg dat spec file clean is (geen hardcoded chromedriver paden)
    spec_file = scripts_dir / "SintMaartenCampusAutologin.spec"
    spec_content = spec_file.read_text()

    # Controleer dat binaries leeg is
    if "binaries=[]," not in spec_content and "binaries = []," not in spec_content:
        print("\n⚠ WAARSCHUWING: Spec file kan hardcoded chromedriver-paden bevatten.")
        print("Dit kan problemen geven op verschillende systemen.")
        print("Reset de spec file naar: binaries=[],")
    else:
        print("\n✓ Spec file is correct (binaries leeg)")

    # Nu pyinstaller runnen
    print("\n[Building executable...]\n")
    os.system("pyinstaller SintMaartenCampusAutologin.spec --clean --noconfirm")

if __name__ == "__main__":
    main()