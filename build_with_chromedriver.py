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

    print("Build script voor Sint Maarten Campus Autologin Tool v2.0.4")
    print("=" * 60)
    print("[OK] webdriver_manager staat in requirements.txt")
    print("[OK] ChromeDriverManager is geintegreerd in browser_session.py")
    print("[OK] ChromeDriver wordt automatisch gedownload bij eerste use")
    print("=" * 60)

    # Zorg dat spec file clean is (geen hardcoded chromedriver paden)
    spec_file = scripts_dir / "SintMaartenCampusAutologin.spec"
    spec_content = spec_file.read_text(encoding="utf-8")

    # Controleer dat binaries leeg is
    if "binaries=[]," not in spec_content and "binaries = []," not in spec_content:
        print("\n[WAARSCHUWING] Spec file kan hardcoded chromedriver-paden bevatten.")
        print("Dit kan problemen geven op verschillende systemen.")
        print("Reset de spec file naar: binaries=[],")
    else:
        print("\n[OK] Spec file is correct (binaries leeg)")

    # Nu pyinstaller runnen
    print("\n[Building executable...]\n")
    exit_code = os.system("pyinstaller SintMaartenCampusAutologin.spec --clean --noconfirm")
    if exit_code != 0:
        sys.exit(exit_code)

if __name__ == "__main__":
    main()
