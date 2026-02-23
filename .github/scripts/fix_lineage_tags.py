"""
Fix Duplicate LineageTags in TMDL Files

This script regenerates all lineageTag GUIDs in TMDL files with unique UUID v4 values.
It scans all .tmdl files in the semantic model definition folder and replaces each
lineageTag with a cryptographically random UUID.

Usage:
    python scripts/fix_lineage_tags.py

Author: AI Semantic Layer Builder Agent
Date: 2025-01-XX
"""

import os
import re
import uuid
from pathlib import Path

# Configuration
PBIP_ROOT = Path(__file__).parent.parent / "PBIP"
DEFINITION_FOLDER = PBIP_ROOT / "SalesOverviewFYTD.SemanticModel" / "definition"

def find_tmdl_files(root_path):
    """Find all .tmdl files recursively in the definition folder."""
    return list(Path(root_path).rglob("*.tmdl"))

def replace_lineage_tags(file_path):
    """Replace all lineageTag values in a TMDL file with unique UUIDs."""
    
    # Read file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track replacements
    replacements = 0
    
    # Pattern to match lineageTag: <guid>
    pattern = r'(lineageTag:\s+)([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
    
    def replace_with_uuid(match):
        nonlocal replacements
        replacements += 1
        prefix = match.group(1)
        new_uuid = str(uuid.uuid4())
        return f"{prefix}{new_uuid}"
    
    # Replace all lineageTags with unique UUIDs
    new_content = re.sub(pattern, replace_with_uuid, content, flags=re.IGNORECASE)
    
    # Write updated content back to file
    if replacements > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return replacements

def main():
    """Main execution function."""
    
    print("=" * 80)
    print("LineageTag Fix Utility - TMDL Model Repair")
    print("=" * 80)
    print()
    
    if not DEFINITION_FOLDER.exists():
        print(f"❌ ERROR: Definition folder not found: {DEFINITION_FOLDER}")
        return 1
    
    print(f"📂 Scanning TMDL files in: {DEFINITION_FOLDER}")
    print()
    
    # Find all TMDL files
    tmdl_files = find_tmdl_files(DEFINITION_FOLDER)
    
    if not tmdl_files:
        print("⚠️  No TMDL files found.")
        return 0
    
    print(f"📄 Found {len(tmdl_files)} TMDL files:")
    for file in tmdl_files:
        relative_path = file.relative_to(DEFINITION_FOLDER)
        print(f"   • {relative_path}")
    print()
    
    # Process each file
    total_replacements = 0
    print("🔄 Processing files...")
    print()
    
    for file_path in tmdl_files:
        relative_path = file_path.relative_to(DEFINITION_FOLDER)
        replacements = replace_lineage_tags(file_path)
        total_replacements += replacements
        
        if replacements > 0:
            print(f"✅ {relative_path}: {replacements} lineageTags replaced")
        else:
            print(f"⏭️  {relative_path}: no lineageTags found")
    
    print()
    print("=" * 80)
    print(f"✨ COMPLETED: {total_replacements} lineageTags regenerated with unique UUIDs")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Open Power BI Desktop")
    print("2. File > Open > Browse")
    print("3. Navigate to PBIP/SalesOverviewFYTD.pbip")
    print("4. The model should now load without errors")
    print()
    
    return 0

if __name__ == "__main__":
    exit(main())
