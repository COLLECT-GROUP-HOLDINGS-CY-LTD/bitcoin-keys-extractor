#!/usr/bin/env python3
import os
import platform
import subprocess
import sys


def build():
    system = platform.system()
    name = "WIFtoPublicKey"

    if system == "Windows":
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', name,
            'wif_converter.py'
        ]
        exe_name = f"{name}.exe"

    elif system == "Darwin":  # macOS
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', name,
            '--osx-bundle-identifier', 'com.wiftools.converter',
            'wif_converter.py'
        ]
        exe_name = f"{name}.app"

    elif system == "Linux":
        cmd = [
            'pyinstaller',
            '--onefile',
            '--name', name.lower().replace(' ', '-'),
            'wif_converter.py'
        ]
        exe_name = name.lower().replace(' ', '-')

    print(f"Building for {system}...")
    print(f"Command: {' '.join(cmd)}")

    subprocess.run(cmd)

    print(f"\n✅ Build complete!")
    print(f"Executable: dist/{exe_name}")
    print(f"Size: {os.path.getsize(f'dist/{exe_name}') / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build()