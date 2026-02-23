"""
Fix TMDL Encoding - Remove UTF-8 BOM
Power BI Desktop requires TMDL files to be UTF-8 without BOM
"""

import os
from pathlib import Path

PROJECT_NAME = "SalesOverviewFYTD"
TMDL_DIR = Path(PROJECT_NAME) / "PBIP" / f"{PROJECT_NAME}.SemanticModel" / "definition"

print("=" * 65)
print("  FIX TMDL ENCODING - Remove UTF-8 BOM")
print("=" * 65)
print()

# Find all TMDL files
tmdl_files = list(TMDL_DIR.glob("**/*.tmdl"))

print(f"Found {len(tmdl_files)} TMDL files to process...")
print()

fixed_count = 0

for file_path in tmdl_files:
    try:
        # Read with UTF-8 (may have BOM)
        content = file_path.read_text(encoding='utf-8-sig')
        
        # Write without BOM
        file_path.write_text(content, encoding='utf-8')
        
        print(f"  + Fixed: {file_path.name}")
        fixed_count += 1
    except Exception as e:
        print(f"  - Error: {file_path.name} - {e}")

print()
print("=" * 65)
print(f"  COMPLETED: Fixed {fixed_count} TMDL files")
print("=" * 65)
print()
print(f"Next: Open {PROJECT_NAME}/PBIP/{PROJECT_NAME}.pbip in Power BI Desktop")
print()
