"""
Remove all comments from TMDL files in a semantic model (Universal Tool).

TMDL does NOT support comments of any kind (///, //, /* */, <!-- -->).
Comments cause parsing issues and must be removed to ensure compatibility
with Power BI Desktop.

This script scans ALL .tmdl files (tables, relationships, expressions, etc.)
and removes any lines containing /// or // comments at the TMDL structure level.
DAX comments inside measure expressions are preserved.

Usage:
    python .github/scripts/remove_tmdl_comments.py <ProjectName>
    python .github/scripts/remove_tmdl_comments.py <ProjectName> --dry-run

Arguments:
    ProjectName: Name of the project folder (e.g., SalesOverviewFYTD)
                 Script looks for: <ProjectName>/PBIP/*.SemanticModel/definition/
"""

import argparse
import re
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


def remove_comments_from_file(file_path: Path, dry_run: bool = False) -> tuple:
    """
    Remove all lines containing /// comments from a TMDL file.
    Preserves DAX comments inside measure expressions.

    Returns:
        Tuple of (number of comments removed, list of removed comment lines)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    removed_comments = []
    comments_count = 0
    inside_expression = False

    for line in lines:
        stripped = line.strip()

        # Track if we're inside a measure/partition expression (DAX or M)
        # Expressions start with "measure 'Name' =" or "source =" patterns
        if re.match(r'^(measure|source)\s', stripped) and '=' in stripped:
            inside_expression = True
        elif stripped and not stripped.startswith('//') and not line.startswith('\t\t') and inside_expression:
            # We've left the expression block (back to property or object level)
            if not line.startswith('\t\t') and not line.startswith('\t\t\t'):
                inside_expression = False

        # Only remove comments at TMDL structure level (not inside expressions)
        if not inside_expression and re.search(r'^\s*///', line):
            comments_count += 1
            removed_comments.append(line.strip())
            continue  # Skip this line

        cleaned_lines.append(line)

    # Write back the cleaned content
    if comments_count > 0 and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

    return comments_count, removed_comments


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Remove TMDL comments from semantic model files (universal tool)'
    )
    parser.add_argument(
        'project',
        help='Project folder name (e.g., SalesOverviewFYTD). '
             'Script searches: <project>/PBIP/*.SemanticModel/definition/'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be removed without modifying files'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("TMDL Comment Removal Script (Universal)")
    print("=" * 80)

    try:
        definition_folder = find_definition_folder(args.project)
    except FileNotFoundError as e:
        print(f"\n❌ ERROR: {e}")
        return 1

    print(f"\n📂 Scanning TMDL files in: {definition_folder}")
    if args.dry_run:
        print("🔍 DRY RUN mode — no files will be modified\n")
    else:
        print()

    # Find all TMDL files recursively
    tmdl_files = sorted(definition_folder.rglob("*.tmdl"))

    if not tmdl_files:
        print("⚠️  No TMDL files found.")
        return 0

    total_files = 0
    total_comments_removed = 0
    files_with_comments = []

    for tmdl_file in tmdl_files:
        total_files += 1
        relative_path = tmdl_file.relative_to(definition_folder)
        comments_count, removed_comments = remove_comments_from_file(tmdl_file, dry_run=args.dry_run)

        if comments_count > 0:
            files_with_comments.append((relative_path, comments_count, removed_comments))
            total_comments_removed += comments_count
            action = "Would remove" if args.dry_run else "Removed"
            print(f"✅ {relative_path}: {action} {comments_count} comment(s)")
        else:
            print(f"✓  {relative_path}: No comments found")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files processed: {total_files}")
    print(f"Files with comments: {len(files_with_comments)}")
    print(f"Total comments removed: {total_comments_removed}")

    if files_with_comments:
        print("\n" + "-" * 80)
        print("DETAILED REPORT")
        print("-" * 80)
        for filename, count, comments in files_with_comments:
            print(f"\n{filename} ({count} comments):")
            for i, comment in enumerate(comments[:5], 1):
                print(f"  {i}. {comment}")
            if count > 5:
                print(f"  ... and {count - 5} more")

    print("\n" + "=" * 80)
    if args.dry_run:
        print("🔍 DRY RUN complete. No files were modified.")
    else:
        print("✅ Comment removal complete!")
    print("=" * 80)

    if total_comments_removed > 0 and not args.dry_run:
        print("\nNext steps:")
        print("1. Close Power BI Desktop (if open)")
        print("2. Delete Analysis Services cache:")
        print('   Remove-Item -Path "$env:LOCALAPPDATA\\Microsoft\\Power BI Desktop\\AnalysisServicesWorkspaces" -Recurse -Force')
        print("3. Re-open PBIP file in Power BI Desktop")
        print("4. Verify no warnings remain on DAX measures")

    return 0


if __name__ == "__main__":
    exit(main())
