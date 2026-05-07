#!/usr/bin/env python3
"""
Build script voor Sint Maarten Campus Autologin Tool
Download chromedriver en update spec file dynamisch.
"""
import os
import sys
from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager

def main():
    scripts_dir = Path(__file__).parent

    # Download chromedriver
    chromedriver_path = ChromeDriverManager().install()
    print(f"Chromedriver gedownload naar: {chromedriver_path}")

    # Update spec file
    spec_file = scripts_dir / "SintMaartenCampusAutologin.spec"
    spec_content = spec_file.read_text()

    # Escape backslashes for Python string
    escaped_path = chromedriver_path.replace('\\', '\\\\')

    # Replace binaries line
    old_binaries = "    binaries=[],\n"
    new_binaries = f"    binaries=[('{escaped_path}', '.')],\n"

    if old_binaries in spec_content:
        spec_content = spec_content.replace(old_binaries, new_binaries)
        spec_file.write_text(spec_content)
        print("Spec file bijgewerkt met chromedriver pad.")
    else:
        print("Kon binaries niet vinden in spec file.")
        print("Huidige spec content rond binaries:")
        lines = spec_content.split('\n')
        for i, line in enumerate(lines):
            if 'binaries' in line:
                print(f"{i+1}: {line}")

    # Nu pyinstaller runnen
    os.system("pyinstaller SintMaartenCampusAutologin.spec --clean --noconfirm")

if __name__ == "__main__":
    main()