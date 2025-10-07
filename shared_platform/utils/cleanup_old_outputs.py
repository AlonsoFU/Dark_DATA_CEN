"""
Cleanup Old Output Files - Remove files with garbage, keep only CLEAN versions
"""

import sys
from pathlib import Path


def cleanup_outputs(output_dir: str = "outputs", dry_run: bool = True):
    """
    Delete old output files (with garbage) and keep only CLEAN versions.

    Args:
        output_dir: Output directory to clean
        dry_run: If True, only show what would be deleted (default: True)
    """
    output_path = Path(output_dir)

    if not output_path.exists():
        print(f"❌ Output directory not found: {output_dir}")
        return

    print("=" * 80)
    if dry_run:
        print("🔍 DRY RUN - Showing what would be deleted (no files will be removed)")
    else:
        print("🗑️  CLEANUP MODE - Files will be deleted!")
    print("=" * 80)

    # Find all old files (ENHANCED.pdf = with garbage)
    old_enhanced_pdfs = list(output_path.glob("*_ENHANCED.pdf"))
    old_content_jsons = list(output_path.glob("*_content.json"))
    old_summary_txts = list(output_path.glob("*_summary.txt"))
    old_classification_pngs = list(output_path.glob("*_classification.png"))
    old_comparison_pngs = list(output_path.glob("*_comparison.png"))

    # Combine all old files
    old_files = (
        old_enhanced_pdfs +
        old_content_jsons +
        old_summary_txts +
        old_classification_pngs +
        old_comparison_pngs
    )

    if not old_files:
        print("\n✅ No old files found - directory is already clean!")
        return

    print(f"\n📦 Found {len(old_files)} old files to remove:")
    print("-" * 80)

    total_size = 0

    # Group by type
    files_by_type = {
        "Enhanced PDFs (with garbage)": old_enhanced_pdfs,
        "Old JSON extractions": old_content_jsons,
        "Old summaries": old_summary_txts,
        "Old classification images": old_classification_pngs,
        "Old comparison images": old_comparison_pngs,
    }

    for file_type, files in files_by_type.items():
        if files:
            print(f"\n{file_type}: {len(files)} files")
            for file in sorted(files):
                size_mb = file.stat().st_size / (1024 * 1024)
                total_size += size_mb
                print(f"   • {file.name} ({size_mb:.2f} MB)")

    print("\n" + "-" * 80)
    print(f"📊 Total space to be freed: {total_size:.2f} MB")

    # Show what will be kept
    clean_pdfs = list(output_path.glob("*_CLEAN.pdf"))
    clean_jsons = list(output_path.glob("*_CLEAN.json"))
    clean_summary = list(output_path.glob("*_CLEAN_SUMMARY.json"))

    kept_files = clean_pdfs + clean_jsons + clean_summary

    if kept_files:
        print("\n✅ Files that will be KEPT:")
        print("-" * 80)
        for file in sorted(kept_files):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   • {file.name} ({size_mb:.2f} MB)")

    # Delete files if not dry run
    if not dry_run:
        print("\n" + "=" * 80)
        print("🗑️  DELETING FILES...")
        print("=" * 80)

        deleted_count = 0
        deleted_size = 0

        for file in old_files:
            try:
                size_mb = file.stat().st_size / (1024 * 1024)
                file.unlink()
                deleted_count += 1
                deleted_size += size_mb
                print(f"✅ Deleted: {file.name}")
            except Exception as e:
                print(f"❌ Error deleting {file.name}: {str(e)}")

        print("\n" + "=" * 80)
        print("🎉 CLEANUP COMPLETED")
        print("=" * 80)
        print(f"📦 Deleted {deleted_count} files")
        print(f"💾 Freed {deleted_size:.2f} MB")
    else:
        print("\n" + "=" * 80)
        print("ℹ️  DRY RUN COMPLETED - No files were deleted")
        print("=" * 80)
        print("To actually delete these files, run:")
        print(f"   python cleanup_old_outputs.py --delete")


if __name__ == "__main__":
    output_dir = Path(__file__).parent / "outputs"

    if len(sys.argv) > 1 and sys.argv[1] in ["--delete", "-d", "--confirm"]:
        print("\n⚠️  WARNING: This will permanently delete old output files!")
        response = input("Are you sure you want to continue? (yes/no): ")

        if response.lower() in ["yes", "y"]:
            cleanup_outputs(str(output_dir), dry_run=False)
        else:
            print("❌ Cleanup cancelled")
    else:
        # Default: dry run
        cleanup_outputs(str(output_dir), dry_run=True)
        print("\n💡 TIP: To actually delete the files, run:")
        print("   python cleanup_old_outputs.py --delete")
