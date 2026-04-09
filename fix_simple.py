#!/usr/bin/env python3
"""Fix corrupted lines in simple_app.py"""

with open("/home/runner/workspace/src/simple_app.py", "r") as f:
    lines = f.readlines()

# Remove any line containing XML artifacts
cleaned = [line for line in lines if "<parameter" not in line]

with open("/home/runner/workspace/src/simple_app.py", "w") as f:
    f.writelines(cleaned)

print(f"Removed {len(lines) - len(cleaned)} corrupted lines")
print(f"File now has {len(cleaned)} lines")
