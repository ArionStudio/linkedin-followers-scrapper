#!/usr/bin/env python3
"""
Complete LinkedIn Followers Downloader and CSV Generator
Downloads follower data from LinkedIn and creates a comprehensive CSV file.
"""

import json
import csv
import os
import glob
import requests
import time
from typing import Dict, List, Any

# Configuration
TOTAL_FOLLOWERS = 2417
COUNT_PER_PAGE = 50
OUTPUT_FILE = "followers.csv"

# LinkedIn API Configuration

# --- How to get the COOKIE value ---
# 1. Log in to LinkedIn in your browser.
# 2. Open Developer Tools (F12), go to the Network tab.
# 3. Visit your company admin analytics followers page (e.g. https://www.linkedin.com/company/<company_id>/admin/analytics/followers/)
# 4. Find a request to 'voyager/api/graphql' (filter by 'graphql' in the network tab).
# 5. Click the request, go to the 'Headers' tab, and find the 'cookie' header.
# 6. Copy the entire value of the 'cookie' header and paste it below as the COOKIE variable.
COOKIE = 'YOUR_LINKEDIN_COOKIE_VALUE_HERE'

# --- How to get the CSRF_TOKEN value ---
# 1. In the same request as above (voyager/api/graphql), look for the 'csrf-token' header.
# 2. Copy the value (e.g. 'ajax:6143245474373924562') and paste it below.
CSRF_TOKEN = 'YOUR_CSRF_TOKEN_HERE'

# --- How to get the MAX_FOLLOW_TIMESTAMP value (optional, for pagination) ---
# 1. This is used for paginating through followers. For the first page, leave it empty.
# 2. For subsequent pages, you can extract the 'maxFollowTimestamp' from the request URL or response of the previous page.
# 3. If you want to start from a specific timestamp, set it here as a string (e.g. "1746598607000").
MAX_FOLLOW_TIMESTAMP = ""  # Leave empty for first page

# --- Company ID Configuration ---
# Replace with your actual LinkedIn company ID
COMPANY_ID = "YOUR_COMPANY_ID_HERE"  # e.g., "11799605"

def download_followers_page(page: int, start: int, count: int) -> Dict[str, Any]:
    """Download a single page of followers from LinkedIn."""
    
    # Build variables for the API call
    variables = f"(start:{start},count:{count},organizationalPage:urn%3Ali%3Afsd_organizationalPage%3A{COMPANY_ID},followerType:MEMBER"
    if MAX_FOLLOW_TIMESTAMP:
        variables += f",maxFollowTimestamp:{MAX_FOLLOW_TIMESTAMP}"
    variables += ")"
    
    url = f"https://www.linkedin.com/voyager/api/graphql?variables={variables}&queryId=voyagerOrganizationDashFollowers.36569e7e40afe58d8bc91299def4c53b"
    
    headers = {
        "accept": "application/vnd.linkedin.normalized+json+2.1",
        "accept-language": "en-US,en;q=0.9,pl;q=0.8",
        "cache-control": "no-cache",
        "csrf-token": CSRF_TOKEN,
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": f"https://www.linkedin.com/company/{COMPANY_ID}/admin/analytics/followers/",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "x-li-lang": "en_US",
        "x-li-page-instance": "urn:li:page:d_flagship3_company_admin;qkthnTTVRNKIhllpo+2mbQ==",
        "x-li-track": '{"clientVersion":"1.13.37013","mpVersion":"1.13.37013","osName":"web","timezoneOffset":2,"timezone":"Europe/Warsaw","deviceFormFactor":"DESKTOP","mpName":"voyager-web","displayDensity":1,"displayWidth":2560,"displayHeight":1440}',
        "x-restli-protocol-version": "2.0.0",
        "cookie": COOKIE
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error downloading page {page}: {e}")
        return {}

def save_page_data(page: int, data: Dict[str, Any]) -> str:
    """Save page data to a JSON file."""
    filename = f"followers_page_{page}.json"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return filename
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return ""

def download_all_followers() -> List[str]:
    """Download all follower pages and return list of saved filenames."""
    downloaded_files = []
    
    # Calculate number of pages needed
    num_pages = (TOTAL_FOLLOWERS + COUNT_PER_PAGE - 1) // COUNT_PER_PAGE
    
    print(f"Downloading {TOTAL_FOLLOWERS} followers in {num_pages} pages...")
    
    for page in range(num_pages):
        start = page * COUNT_PER_PAGE
        
        print(f"Downloading page {page + 1}/{num_pages} (followers {start}-{start + COUNT_PER_PAGE - 1})...")
        
        # Download page data
        data = download_followers_page(page, start, COUNT_PER_PAGE)
        
        if data:
            # Save to file
            filename = save_page_data(page, data)
            if filename:
                downloaded_files.append(filename)
                print(f"  ✅ Saved to {filename}")
            else:
                print(f"  ❌ Failed to save page {page}")
        else:
            print(f"  ❌ Failed to download page {page}")
        
        # Add delay to avoid rate limiting
        if page < num_pages - 1:
            time.sleep(1)
    
    print(f"Downloaded {len(downloaded_files)} pages")
    return downloaded_files

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
            "entityUrn": profile.get("entityUrn", element.get("entityUrn", "")),
        }
        
        return row
    
    except Exception as e:
        print(f"Error building row: {e}")
        return {}

def process_downloaded_pages() -> List[Dict[str, str]]:
    """Process all downloaded page files and return all follower rows."""
    all_rows = []
    all_profiles = {}
    
    # Find all page files
    page_files = sorted(glob.glob("followers_page_*.json"))
    
    if not page_files:
        print("No downloaded page files found")
        return []
    
    print(f"Processing {len(page_files)} downloaded page files...")
    
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
    """Main function to download and process LinkedIn follower data."""
    print("LinkedIn Followers Complete Downloader & CSV Generator")
    print("=" * 60)
    
    # Check if configuration is complete
    if COOKIE == 'YOUR_LINKEDIN_COOKIE_VALUE_HERE':
        print("❌ ERROR: Please configure your LinkedIn cookie value in the script.")
        print("   Follow the instructions in the comments above the COOKIE variable.")
        return
    
    if CSRF_TOKEN == 'YOUR_CSRF_TOKEN_HERE':
        print("❌ ERROR: Please configure your CSRF token in the script.")
        print("   Follow the instructions in the comments above the CSRF_TOKEN variable.")
        return
    
    if COMPANY_ID == "YOUR_COMPANY_ID_HERE":
        print("❌ ERROR: Please configure your company ID in the script.")
        print("   Replace 'YOUR_COMPANY_ID_HERE' with your actual LinkedIn company ID.")
        return
    
    if TOTAL_FOLLOWERS <= 0:
        print("❌ ERROR: Please set a valid TOTAL_FOLLOWERS count.")
        print("   Update the TOTAL_FOLLOWERS variable with your actual follower count.")
        return
    
    print("✅ Configuration validated successfully!")
    
    # Step 1: Download all follower data
    print("\n📥 STEP 1: Downloading follower data from LinkedIn...")
    downloaded_files = download_all_followers()
    
    if not downloaded_files:
        print("❌ No data downloaded. Exiting.")
        return
    
    # Step 2: Process downloaded data into CSV
    print("\n📊 STEP 2: Processing downloaded data into CSV...")
    rows = process_downloaded_pages()
    
    if not rows:
        print("❌ No data found to process")
        return
    
    # Step 3: Write CSV file
    print(f"\n💾 STEP 3: Writing CSV file...")
    if write_csv(OUTPUT_FILE, rows):
        print(f"\n✅ SUCCESS! Created {OUTPUT_FILE} with {len(rows)} followers")
        print(f"📊 CSV includes: LinkedIn URLs, names, headlines, and follow dates")
        print(f"📁 Downloaded {len(downloaded_files)} page files")
    else:
        print("\n❌ Failed to create CSV file")

if __name__ == "__main__":
    main() 
