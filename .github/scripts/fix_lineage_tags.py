"""
Fix Duplicate LineageTags in TMDL Files (Universal Tool)

This script regenerates all lineageTag GUIDs in TMDL files with unique UUID v4 values.
It scans all .tmdl files in the semantic model definition folder and replaces each
lineageTag with a cryptographically random UUID.

This is a universal tool that works on any PBIP project regardless of the model name.

Usage:
    python .github/scripts/fix_lineage_tags.py <ProjectName>
    python .github/scripts/fix_lineage_tags.py <ProjectName> --dry-run

Arguments:
    ProjectName: Name of the project folder (e.g., SalesOverviewFYTD)
                 Script looks for: <ProjectName>/PBIP/*.SemanticModel/definition/
"""

import argparse
import os
import re
import uuid
from pathlib import Path


def find_definition_folder(project_name: str) -> Path:
    """Auto-discover the TMDL definition folder for a project."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    pbip_folder = repo_root / project_name / "PBIP"

    if not pbip_folder.exists():
        raise FileNotFoundError(f"Project PBIP folder not found: {pbip_folder}")

    # Find *.SemanticModel folder
    sm_folders = list(pbip_folder.glob("*.SemanticModel"))
    if not sm_folders:
        raise FileNotFoundError(f"No *.SemanticModel folder found in: {pbip_folder}")

    definition_folder = sm_folders[0] / "definition"
    if not definition_folder.exists():
        raise FileNotFoundError(f"Definition folder not found: {definition_folder}")

    return definition_folder

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
    parser = argparse.ArgumentParser(
        description='Fix duplicate lineageTags in TMDL files (universal tool)'
    )
    parser.add_argument(
        'project',
        help='Project folder name (e.g., SalesOverviewFYTD). '
             'Script searches: <project>/PBIP/*.SemanticModel/definition/'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("LineageTag Fix Utility - TMDL Model Repair (Universal)")
    print("=" * 80)
    print()

    try:
        definition_folder = find_definition_folder(args.project)
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        return 1

    print(f"📂 Scanning TMDL files in: {definition_folder}")
    print()
    
    # Find all TMDL files
    tmdl_files = find_tmdl_files(definition_folder)

    if not tmdl_files:
        print("⚠️  No TMDL files found.")
        return 0

    print(f"📄 Found {len(tmdl_files)} TMDL files:")
    for file in tmdl_files:
        relative_path = file.relative_to(definition_folder)
        print(f"   • {relative_path}")
    print()

    if args.dry_run:
        print("🔍 DRY RUN mode — no files will be modified\n")

    # Process each file
    total_replacements = 0
    print("🔄 Processing files...")
    print()

    for file_path in tmdl_files:
        relative_path = file_path.relative_to(definition_folder)
        if args.dry_run:
            # Count without modifying
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            pattern = r'(lineageTag:\s+)([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})'
            matches = len(re.findall(pattern, content, flags=re.IGNORECASE))
            if matches > 0:
                print(f"🔍 {relative_path}: {matches} lineageTags would be replaced")
                total_replacements += matches
            else:
                print(f"⏭️  {relative_path}: no lineageTags found")
        else:
            replacements = replace_lineage_tags(file_path)
            total_replacements += replacements
            if replacements > 0:
                print(f"✅ {relative_path}: {replacements} lineageTags replaced")
            else:
                print(f"⏭️  {relative_path}: no lineageTags found")

    print()
    print("=" * 80)
    if args.dry_run:
        print(f"🔍 DRY RUN: {total_replacements} lineageTags would be regenerated")
    else:
        print(f"✨ COMPLETED: {total_replacements} lineageTags regenerated with unique UUIDs")
    print("=" * 80)
    print()
    print("Next steps:")
    print(f"1. Open Power BI Desktop")
    print(f"2. File > Open > Browse")
    print(f"3. Navigate to {args.project}/PBIP/*.pbip")
    print(f"4. The model should now load without errors")
    print()

    return 0

if __name__ == "__main__":
    exit(main())
