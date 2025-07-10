#!/usr/bin/env python3
"""
LinkedIn Followers CSV Processor
Processes existing follower page JSON files into a comprehensive CSV.
Use this if you already have the downloaded files and just want to create the CSV.
"""

import json
import csv
import os
import glob
from typing import Dict, List, Any

# Configuration
INPUT_PATTERN = "followers_page_*.json"
OUTPUT_FILE = "followers.csv"

def extract_profiles_from_page(page_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Extract profiles from a single page's included section."""
    profiles = {}
    
    if "included" in page_data:
        for profile in page_data["included"]:
            if "entityUrn" in profile and "publicIdentifier" in profile:
                profiles[profile["entityUrn"]] = profile
    
    return profiles

def extract_elements_from_page(page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract follower elements from a single page."""
    elements = []
    
    try:
        # Navigate to the elements array
        if "data" in page_data and "data" in page_data["data"]:
            main_data = page_data["data"]["data"]
        elif "data" in page_data:
            main_data = page_data["data"]
        else:
            main_data = page_data
        
        # Find the follower elements
        if "organizationDashFollowersByOrganizationalPage" in main_data:
            follower_data = main_data["organizationDashFollowersByOrganizationalPage"]
            if "elements" in follower_data:
                elements = follower_data["elements"]
    
    except Exception as e:
        print(f"Error extracting elements: {e}")
    
    return elements

def build_follower_row(element: Dict[str, Any], profile_map: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """Build a single row for the CSV from a follower element."""
    try:
        # Get the profile URN from the follower element
        profile_urn = None
        if "followerV2" in element and "*profile" in element["followerV2"]:
            profile_urn = element["followerV2"]["*profile"]
        
        # Get the profile data
        profile = profile_map.get(profile_urn, {}) if profile_urn else {}
        
        # Extract followedAt information
        followed_at = element.get("followedAt", {})
        if isinstance(followed_at, dict):
            followed_text = followed_at.get("text", "")
            followed_accessibility = followed_at.get("accessibilityText", "")
        else:
            followed_text = str(followed_at) if followed_at else ""
            followed_accessibility = ""
        
        # Construct LinkedIn profile URL
        public_identifier = profile.get("publicIdentifier", "")
        linkedin_url = f"https://www.linkedin.com/in/{public_identifier}/" if public_identifier else ""
        
        # Build the row
        row = {
            "firstName": profile.get("firstName", ""),
            "lastName": profile.get("lastName", ""),
            "headline": profile.get("headline", ""),
            "publicIdentifier": public_identifier,
            "linkedinUrl": linkedin_url,
            "followedAt.text": followed_text,
            "followedAt.accessibilityText": followed_accessibility,
            "entityUrn": profile.get("entityUrn", ""),
        }
        
        return row
    
    except Exception as e:
        print(f"Error building row: {e}")
        return {}

def process_existing_pages() -> List[Dict[str, str]]:
    """Process all existing page files and return all follower rows."""
    all_rows = []
    all_profiles = {}
    
    # Find all page files
    page_files = sorted(glob.glob(INPUT_PATTERN))
    
    if not page_files:
        print(f"No files found matching pattern: {INPUT_PATTERN}")
        print("Make sure you have downloaded follower page files first.")
        return []
    
    print(f"Found {len(page_files)} page files to process...")
    
    # Process each page
    for i, filename in enumerate(page_files):
        print(f"Processing {filename}...")
        
        # Load page data
        try:
            with open(filename, "r", encoding="utf-8") as f:
                page_data = json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
        
        # Extract profiles from this page
        page_profiles = extract_profiles_from_page(page_data)
        all_profiles.update(page_profiles)
        print(f"  Found {len(page_profiles)} profiles")
        
        # Extract follower elements from this page
        elements = extract_elements_from_page(page_data)
        print(f"  Found {len(elements)} follower elements")
        
        # Build rows for this page
        for element in elements:
            row = build_follower_row(element, all_profiles)
            if row:
                all_rows.append(row)
    
    print(f"Total unique profiles: {len(all_profiles)}")
    print(f"Total follower rows: {len(all_rows)}")
    
    return all_rows

def write_csv(filename: str, rows: List[Dict[str, str]]) -> bool:
    """Write rows to a CSV file."""
    if not rows:
        print("No rows to write")
        return False
    
    fieldnames = [
        "firstName", 
        "lastName",
        "headline",
        "publicIdentifier",
        "linkedinUrl",
        "followedAt.text",
        "followedAt.accessibilityText",
        "entityUrn",
    ]
    
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"Successfully wrote {len(rows)} rows to {filename}")
        return True
    
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False

def main():
    """Main function to process existing LinkedIn follower data."""
    print("LinkedIn Followers CSV Processor")
    print("=" * 40)
    print("Processing existing downloaded page files...")
    
    # Process existing pages
    rows = process_existing_pages()
    
    if not rows:
        print("No data found to process")
        return
    
    # Write to CSV
    if write_csv(OUTPUT_FILE, rows):
        print(f"\n✅ Success! Created {OUTPUT_FILE} with {len(rows)} followers")
        print(f"📊 CSV includes: LinkedIn URLs, names, headlines, and follow dates")
    else:
        print("\n❌ Failed to create CSV file")

if __name__ == "__main__":
    main() 
