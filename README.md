# LinkedIn Followers CSV Generator

A Python utility for extracting LinkedIn company follower data and generating structured CSV output with comprehensive profile information.

**Version:** 1.0.0  
**Author:** ArionStudio  
**License:** Apache 2.0  
**Python Version:** 3.6+  
**Last Updated:** January 2025

## Overview

This tool provides a straightforward method for downloading LinkedIn company follower data and converting it into a structured CSV format suitable for analysis and reporting purposes.

## Features

- **Data Extraction**: Retrieves follower information from LinkedIn company pages
- **CSV Generation**: Produces structured CSV output with profile details
- **Rate Management**: Implements request delays to maintain API compliance
- **Flexible Processing**: Supports both fresh data retrieval and existing file processing
- **Error Management**: Includes comprehensive error handling and progress monitoring

## Requirements

### System Requirements
- **Python:** 3.6 or higher

### Python Dependencies
```
requests>=2.25.0
```

Install dependencies with:
```bash
pip install -r requirements.txt
```

## CSV Output Structure

The generated `followers.csv` file contains the following data fields:

| Field | Description | Sample Value |
|-------|-------------|--------------|
| `firstName` | Given name | "John" |
| `lastName` | Family name | "Doe" |
| `headline` | Professional title | "Software Engineer at Tech Corp" |
| `publicIdentifier` | LinkedIn username | "john-doe-123" |
| `linkedinUrl` | Profile URL | "https://www.linkedin.com/in/john-doe-123/" |
| `followedAt.text` | Follow date (abbreviated) | "May 2025" |
| `followedAt.accessibilityText` | Follow date (full description) | "Followed your page in May 2025" |
| `entityUrn` | LinkedIn internal identifier | "urn:li:fsd_profile:ACoAA..." |

## Installation

### Prerequisites

1. **Python 3.6 or higher**
2. **Required package**: `requests`

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ArionStudio/linkedin-followers-scrapper.git
   cd linkedin-followers-scrapper
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   ```

## Configuration

### Authentication Setup

Prior to execution, LinkedIn authentication credentials must be obtained:

#### Step 1: Retrieve Cookie Value
1. Access LinkedIn through your web browser
2. Open browser developer tools (F12) and navigate to the Network tab
3. Visit your company's follower analytics page: `https://www.linkedin.com/company/<company_id>/admin/analytics/followers/`
4. Locate a request to `voyager/api/graphql` (filter by 'graphql')
5. Select the request and examine the Headers tab
6. Copy the complete value from the 'cookie' header

#### Step 2: Obtain CSRF Token
1. Within the same request, locate the 'csrf-token' header
2. Copy the token value (format: `ajax:6143245474373924562`)

#### Step 3: Update Configuration
Modify `linkedin_followers_complete.py` with your credentials:

```python
COOKIE = 'your_cookie_value_here'
CSRF_TOKEN = 'your_csrf_token_here'
TOTAL_FOLLOWERS = 2417  # Adjust to your actual follower count
```

## Usage

### Method 1: Complete Data Retrieval

Execute the comprehensive download and processing script:

```bash
python3 linkedin_followers_complete.py
```

This process will:
1. Download all follower data pages from LinkedIn
2. Store individual JSON files (`followers_page_0.json`, `followers_page_1.json`, etc.)
3. Generate the final `followers.csv` output file

### Method 2: Process Existing Data

For processing previously downloaded files:

```bash
python3 process_existing_followers.py
```

This will:
1. Locate all `followers_page_*.json` files in the current directory
2. Process the data and generate `followers.csv`

## File Organization

```
linkedin-followers-scrapper/
├── README.md
├── requirements.txt
├── LICENSE
├── linkedin_followers_complete.py    # Primary download and processing script
├── process_existing_followers.py     # Secondary processing script
├── followers.csv                     # Output file (generated after execution)
└── followers_page_*.json            # Intermediate data files (generated after execution)
```

## Configuration Parameters

### Primary Script (`linkedin_followers_complete.py`)

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `TOTAL_FOLLOWERS` | Total follower count to retrieve | `2417` |
| `COUNT_PER_PAGE` | Followers per page (LinkedIn limit) | `50` |
| `OUTPUT_FILE` | Output CSV filename | `"followers.csv"` |
| `MAX_FOLLOW_TIMESTAMP` | Pagination timestamp (optional) | `"1746598607000"` |

### Secondary Script (`process_existing_followers.py`)

| Parameter | Purpose | Default Value |
|-----------|---------|---------------|
| `INPUT_PATTERN` | File pattern for page files | `"followers_page_*.json"` |
| `OUTPUT_FILE` | Output CSV filename | `"followers.csv"` |

## Output Example

```csv
firstName,lastName,headline,publicIdentifier,linkedinUrl,followedAt.text,followedAt.accessibilityText,entityUrn
John,Doe,Software Engineer at Tech Corp,john-doe-123,https://www.linkedin.com/in/john-doe-123/,May 2025,Followed your page in May 2025,urn:li:fsd_profile:ACoAA...
Jane,Smith,Marketing Manager,jane-smith-456,https://www.linkedin.com/in/jane-smith-456/,April 2025,Followed your page in April 2025,urn:li:fsd_profile:ACoBB...
```

## Important Considerations

### Rate Limiting
- The tool implements 1-second intervals between requests to maintain compliance
- LinkedIn may impose additional restrictions based on request volume
- Consider execution timing for large datasets

### Authentication
- Credential validity is time-limited and may require periodic renewal
- Maintain active LinkedIn session during data retrieval
- Refresh credentials if download operations fail

### Data Reliability
- Follower counts are subject to change
- Some profiles may be inaccessible or removed
- LinkedIn may restrict access to certain data elements

## Troubleshooting

### Common Issues

**Authentication Error (401 Unauthorized)**
- Credentials have expired
- Follow the configuration steps to obtain fresh credentials

**File Not Found Error**
- No downloaded JSON files present
- Execute the complete script first or verify file naming

**JSON Parsing Error**
- Downloaded file is incomplete or corrupted
- Remove the problematic file and re-execute download

### Debug Information

To enable detailed logging, modify the scripts:

```python
# Add debugging output
print(f"Request URL: {url}")
print(f"Response status: {response.status_code}")
```

## Changelog

### Version 1.0.0 (January 2025)
- Initial release
- Complete LinkedIn follower data extraction
- CSV generation with profile URLs
- Rate limiting and error handling
- Support for existing file processing

## License

This project is distributed under the Apache License 2.0. See the [LICENSE](LICENSE) file for complete terms.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Submit a Pull Request

### Development Setup
```bash
git clone https://github.com/ArionStudio/linkedin-followers-scrapper.git
cd linkedin-followers-scrapper
pip install -r requirements.txt
```

## Disclaimer

This utility is intended for educational and legitimate business applications. Users are responsible for compliance with LinkedIn's Terms of Service. The developers assume no liability for misuse of this tool.

## Support

For assistance or questions:

1. Review the troubleshooting section above
2. Verify LinkedIn's current API structure
3. Submit an issue with detailed error information

## Contact

- **Author:** ArionStudio
- **GitHub:** [https://github.com/ArionStudio](https://github.com/ArionStudio)
- **Repository:** [https://github.com/ArionStudio/linkedin-followers-scrapper](https://github.com/ArionStudio/linkedin-followers-scrapper)

---

**Developed for LinkedIn data analysis applications**
