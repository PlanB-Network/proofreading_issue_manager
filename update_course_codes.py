#!/usr/bin/env python3
"""
Script to update course codes in open GitHub issues.
Replaces specific course codes with their new identifiers.
"""

from github import Github
from config import Config
import os
import re


# Course code replacements (case-insensitive)
REPLACEMENTS = {
    'phi201': 'phi101',
    'btc302': 'btc304',
    'phi302': 'btc303',
    'btc305': 'POS305',
    'BTC401': 'PRO101',
    'ECO102': 'ECO203'
}


def replace_course_codes(text):
    """
    Replace course codes in text (case-insensitive).
    Returns tuple: (modified_text, was_modified, changes_made)
    """
    if not text:
        return text, False, []

    modified_text = text
    changes_made = []

    for old_code, new_code in REPLACEMENTS.items():
        # Create case-insensitive pattern
        pattern = re.compile(re.escape(old_code), re.IGNORECASE)
        matches = pattern.findall(modified_text)

        if matches:
            # Replace all occurrences
            modified_text = pattern.sub(new_code, modified_text)
            changes_made.append(f"{old_code} -> {new_code} ({len(matches)} occurrence(s))")

    was_modified = (modified_text != text)
    return modified_text, was_modified, changes_made


def update_open_issues(dry_run=True):
    """
    Update course codes in all open issues.

    Args:
        dry_run: If True, only print what would be changed without making actual updates
    """
    token = Config.GITHUB_TOKEN

    if not token:
        print("❌ Error: GITHUB_TOKEN not configured")
        print("Please set GITHUB_TOKEN in your .env file")
        return

    print(f"🔗 Connecting to GitHub...")
    github = Github(token)

    try:
        repo = github.get_repo(f"{Config.GITHUB_OWNER}/{Config.GITHUB_REPO}")
        print(f"✅ Connected to {Config.GITHUB_OWNER}/{Config.GITHUB_REPO}")
    except Exception as e:
        print(f"❌ Error connecting to repository: {e}")
        return

    print("\n📋 Fetching open issues...")

    try:
        open_issues = list(repo.get_issues(state='open'))
        print(f"✅ Found {len(open_issues)} open issue(s)")
    except Exception as e:
        print(f"❌ Error fetching issues: {e}")
        return

    if not open_issues:
        print("\nℹ️  No open issues to process")
        return

    print("\n" + "="*80)
    print(f"{'DRY RUN MODE' if dry_run else 'UPDATE MODE'}")
    print("="*80 + "\n")

    issues_to_update = []

    # Check each issue
    for issue in open_issues:
        print(f"\n🔍 Checking Issue #{issue.number}: {issue.title}")

        title = issue.title
        body = issue.body or ""

        # Check for replacements in title and body
        new_title, title_modified, title_changes = replace_course_codes(title)
        new_body, body_modified, body_changes = replace_course_codes(body)

        if title_modified or body_modified:
            print(f"   ✏️  Changes needed:")

            if title_modified:
                print(f"      📌 Title changes:")
                for change in title_changes:
                    print(f"         • {change}")
                print(f"         Old: {title}")
                print(f"         New: {new_title}")

            if body_modified:
                print(f"      📄 Body changes:")
                for change in body_changes:
                    print(f"         • {change}")

            issues_to_update.append({
                'issue': issue,
                'new_title': new_title,
                'new_body': new_body,
                'title_modified': title_modified,
                'body_modified': body_modified
            })
        else:
            print(f"   ✅ No changes needed")

    # Summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Total open issues: {len(open_issues)}")
    print(f"Issues to update: {len(issues_to_update)}")

    if issues_to_update:
        print("\nIssues that will be updated:")
        for item in issues_to_update:
            issue = item['issue']
            changes = []
            if item['title_modified']:
                changes.append("title")
            if item['body_modified']:
                changes.append("body")
            print(f"  • Issue #{issue.number}: {', '.join(changes)}")

    # Perform updates if not dry run
    if not dry_run and issues_to_update:
        print("\n" + "="*80)
        print("🚀 APPLYING UPDATES")
        print("="*80 + "\n")

        success_count = 0
        error_count = 0

        for item in issues_to_update:
            issue = item['issue']

            try:
                print(f"⏳ Updating Issue #{issue.number}...", end=" ")

                # Update the issue
                issue.edit(
                    title=item['new_title'],
                    body=item['new_body']
                )

                print(f"✅ Success")
                success_count += 1

            except Exception as e:
                print(f"❌ Failed: {e}")
                error_count += 1

        print("\n" + "="*80)
        print("✨ FINAL RESULTS")
        print("="*80)
        print(f"✅ Successfully updated: {success_count}")
        print(f"❌ Failed: {error_count}")

    elif dry_run and issues_to_update:
        print("\n⚠️  This was a DRY RUN - no actual changes were made")
        print("To apply these changes, run:")
        print("  python update_course_codes.py --apply")


if __name__ == "__main__":
    import sys

    # Check for --apply flag
    dry_run = "--apply" not in sys.argv

    if dry_run:
        print("=" * 80)
        print("🔍 DRY RUN MODE - No changes will be made")
        print("=" * 80)
        print("\nThis will show you what changes would be made without actually updating issues.")
        print("To apply the changes, run: python update_course_codes.py --apply\n")
    else:
        print("=" * 80)
        print("⚡ UPDATE MODE - Changes will be applied")
        print("=" * 80)
        print("\nThis will update all open issues with the new course codes.\n")

        confirmation = input("Are you sure you want to proceed? (yes/no): ")
        if confirmation.lower() not in ['yes', 'y']:
            print("\n❌ Update cancelled")
            sys.exit(0)

    update_open_issues(dry_run=dry_run)
