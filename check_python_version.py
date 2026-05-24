#!/usr/bin/env python3
"""Quick script to check Python version on EISY."""

import sys
import platform

print(f"Python Version: {sys.version}")
print(f"Python Version Info: {sys.version_info}")
print(f"Python Executable: {sys.executable}")
print(f"Platform: {platform.platform()}")
print(f"Python Implementation: {platform.python_implementation()}")

# Write to a file for easy viewing
with open('/tmp/eisy_python_version.txt', 'w') as f:
    f.write(f"Python Version: {sys.version}\n")
    f.write(f"Python Version Info: {sys.version_info}\n")
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Platform: {platform.platform()}\n")

print("\nVersion info written to /tmp/eisy_python_version.txt")
