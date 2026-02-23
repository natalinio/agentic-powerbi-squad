"""
Remove all /// comments from TMDL files in the semantic model.

TMDL does NOT support comments of any kind. Comments cause parsing issues
and must be removed to ensure compatibility with all Power BI Desktop versions.
"""

import os
import re
from pathlib import Path

# Define the path to the TMDL tables folder
TMDL_TABLES_PATH = Path(__file__).parent.parent / "PBIP" / "SalesOverviewFYTD.SemanticModel" / "definition" / "tables"

def remove_comments_from_file(file_path: Path) -> tuple[int, list[str]]:
    """
    Remove all lines containing /// comments from a TMDL file.
    
    Args:
        file_path: Path to the TMDL file
        
    Returns:
        Tuple of (number of comments removed, list of removed comment lines)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    removed_comments = []
    comments_count = 0
    
    for line in lines:
        # Check if line contains /// comment (with or without leading tabs)
        if re.search(r'^\s*///', line):
            comments_count += 1
            removed_comments.append(line.strip())
            # Skip this line (don't add to cleaned_lines)
        else:
            cleaned_lines.append(line)
    
    # Write back the cleaned content
    if comments_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
    
    return comments_count, removed_comments

def main():
    """Process all TMDL files and remove comments."""
    print("=" * 80)
    print("TMDL Comment Removal Script")
    print("=" * 80)
    print(f"\nScanning directory: {TMDL_TABLES_PATH}\n")
    
    if not TMDL_TABLES_PATH.exists():
        print(f"ERROR: Directory not found: {TMDL_TABLES_PATH}")
        return
    
    total_files = 0
    total_comments_removed = 0
    files_with_comments = []
    
    # Process each .tmdl file
    for tmdl_file in sorted(TMDL_TABLES_PATH.glob("*.tmdl")):
        total_files += 1
        comments_count, removed_comments = remove_comments_from_file(tmdl_file)
        
        if comments_count > 0:
            files_with_comments.append((tmdl_file.name, comments_count, removed_comments))
            total_comments_removed += comments_count
            print(f"✅ {tmdl_file.name}: Removed {comments_count} comment(s)")
        else:
            print(f"✓  {tmdl_file.name}: No comments found")
    
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
            for i, comment in enumerate(comments[:3], 1):  # Show first 3 comments
                print(f"  {i}. {comment}")
            if count > 3:
                print(f"  ... and {count - 3} more")
    
    print("\n" + "=" * 80)
    print("✅ Comment removal complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Close Power BI Desktop (if open)")
    print("2. Delete Analysis Services cache:")
    print("   Remove-Item -Path \"$env:LOCALAPPDATA\\Microsoft\\Power BI Desktop\\AnalysisServicesWorkspaces\" -Recurse -Force")
    print("3. Re-open PBIP file in Power BI Desktop")
    print("4. Verify no warnings remain on DAX measures")

if __name__ == "__main__":
    main()
