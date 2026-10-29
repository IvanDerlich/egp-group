#!/usr/bin/env python3
"""
Site integrity tests for EGP Group website.
Verifies:
- All referenced assets exist
- All in-page anchors resolve
- Every <img> has alt text
"""

import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser


class SiteChecker(HTMLParser):
    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path
        self.errors = []
        self.warnings = []
        self.images = []
        self.links = []
        self.ids = set()
        self.anchors = set()
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        # Collect IDs
        if 'id' in attrs_dict:
            self.ids.add(attrs_dict['id'])
        
        # Check images
        if tag == 'img':
            self.images.append(attrs_dict)
            
            # Check for alt text
            if 'alt' not in attrs_dict:
                self.errors.append(f"Image missing alt text: {attrs_dict.get('src', 'unknown')}")
            elif not attrs_dict['alt'].strip():
                self.errors.append(f"Image has empty alt text: {attrs_dict['src']}")
            
            # Check if src exists
            if 'src' in attrs_dict:
                src = attrs_dict['src']
                if not src.startswith(('http://', 'https://', 'data:')):
                    file_path = self.base_path / src
                    if not file_path.exists():
                        self.errors.append(f"Image file not found: {src}")
            
            # Check srcset
            if 'srcset' in attrs_dict:
                srcset = attrs_dict['srcset']
                # Parse srcset (format: "path 1x, path 2x" or "path 100w, path 200w")
                for item in srcset.split(','):
                    parts = item.strip().split()
                    if parts:
                        src_path = parts[0]
                        if not src_path.startswith(('http://', 'https://', 'data:')):
                            file_path = self.base_path / src_path
                            if not file_path.exists():
                                self.errors.append(f"Srcset file not found: {src_path}")
        
        # Check source tags (for picture elements)
        if tag == 'source':
            if 'srcset' in attrs_dict:
                srcset = attrs_dict['srcset']
                if not srcset.startswith(('http://', 'https://', 'data:')):
                    file_path = self.base_path / srcset
                    if not file_path.exists():
                        self.errors.append(f"Source file not found: {srcset}")
        
        # Check links
        if tag == 'a':
            if 'href' in attrs_dict:
                href = attrs_dict['href']
                if href.startswith('#'):
                    # Internal anchor
                    anchor = href[1:]
                    if anchor:  # Skip empty anchors like href="#"
                        self.anchors.add(anchor)
                elif not href.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                    # Relative link to file
                    file_path = self.base_path / href
                    if not file_path.exists():
                        self.errors.append(f"Linked file not found: {href}")
        
        # Check link tags (CSS, favicons, etc.)
        if tag == 'link':
            if 'href' in attrs_dict:
                href = attrs_dict['href']
                if not href.startswith(('http://', 'https://', 'data:')):
                    file_path = self.base_path / href
                    if not file_path.exists():
                        self.errors.append(f"Linked resource not found: {href}")
        
        # Check script tags
        if tag == 'script':
            if 'src' in attrs_dict:
                src = attrs_dict['src']
                if not src.startswith(('http://', 'https://', '//')):
                    file_path = self.base_path / src
                    if not file_path.exists():
                        self.errors.append(f"Script file not found: {src}")


def check_site(html_path):
    """Check the site for issues."""
    print(f"Checking site: {html_path}")
    print("=" * 60)
    
    base_path = html_path.parent
    
    # Read HTML
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse HTML
    checker = SiteChecker(base_path)
    checker.feed(html_content)
    
    # Check that all anchors resolve to IDs
    print("\n1. Checking in-page anchors...")
    anchor_errors = []
    for anchor in checker.anchors:
        if anchor not in checker.ids:
            anchor_errors.append(f"Anchor #{anchor} does not resolve to any element ID")
    
    if anchor_errors:
        checker.errors.extend(anchor_errors)
        print(f"   ❌ {len(anchor_errors)} unresolved anchor(s)")
        for error in anchor_errors:
            print(f"      - {error}")
    else:
        print(f"   ✓ All {len(checker.anchors)} anchors resolve correctly")
    
    # Report image checks
    print(f"\n2. Checking images...")
    image_errors = [e for e in checker.errors if 'Image' in e or 'image' in e]
    if image_errors:
        print(f"   ❌ {len(image_errors)} image issue(s)")
        for error in image_errors:
            print(f"      - {error}")
    else:
        print(f"   ✓ All {len(checker.images)} images have alt text and exist")
    
    # Report asset checks
    print(f"\n3. Checking assets...")
    asset_errors = [e for e in checker.errors if e not in image_errors and e not in anchor_errors]
    if asset_errors:
        print(f"   ❌ {len(asset_errors)} asset issue(s)")
        for error in asset_errors:
            print(f"      - {error}")
    else:
        print(f"   ✓ All referenced assets exist")
    
    # Check LinkedIn link
    print(f"\n4. Checking LinkedIn link...")
    linkedin_link_found = False
    linkedin_errors = []
    
    for tag, attrs_dict in [(tag, dict(attrs)) for tag, attrs in [(checker.links[i][0], checker.links[i][1]) for i in range(len(checker.links))] if dict(attrs).get('href', '').startswith('https://www.linkedin.com/company/egp-group-mendoza')]:
        linkedin_link_found = True
        # Check target and rel attributes
        if attrs_dict.get('target') != '_blank':
            linkedin_errors.append("LinkedIn link missing target='_blank'")
        if attrs_dict.get('rel') != 'noopener':
            linkedin_errors.append("LinkedIn link missing rel='noopener'")
        if 'aria-label' not in attrs_dict:
            linkedin_errors.append("LinkedIn link missing aria-label")
        elif 'LinkedIn de EGP Group' not in attrs_dict.get('aria-label', ''):
            linkedin_errors.append(f"LinkedIn link has incorrect aria-label: {attrs_dict.get('aria-label')}")
    
    # Also check by parsing HTML directly since we may not have stored links
    if not linkedin_link_found:
        import re
        linkedin_pattern = r'<a[^>]*href="https://www\.linkedin\.com/company/egp-group-mendoza/"[^>]*>'
        if re.search(linkedin_pattern, html_content):
            linkedin_link_found = True
            # Verify attributes in the matched link
            match = re.search(r'<a([^>]*href="https://www\.linkedin\.com/company/egp-group-mendoza/"[^>]*)>', html_content)
            if match:
                attrs = match.group(1)
                if 'target="_blank"' not in attrs:
                    linkedin_errors.append("LinkedIn link missing target='_blank'")
                if 'rel="noopener"' not in attrs:
                    linkedin_errors.append("LinkedIn link missing rel='noopener'")
                if 'aria-label=' not in attrs:
                    linkedin_errors.append("LinkedIn link missing aria-label")
                elif 'aria-label="LinkedIn de EGP Group"' not in attrs:
                    linkedin_errors.append("LinkedIn link has incorrect aria-label")
    
    if not linkedin_link_found:
        linkedin_errors.append("LinkedIn link to egp-group-mendoza not found")
    
    if linkedin_errors:
        checker.errors.extend(linkedin_errors)
        print(f"   ❌ {len(linkedin_errors)} LinkedIn link issue(s)")
        for error in linkedin_errors:
            print(f"      - {error}")
    else:
        print(f"   ✓ LinkedIn link present with correct attributes")
    
    # Summary
    print("\n" + "=" * 60)
    total_errors = len(checker.errors)
    if total_errors == 0:
        print("✅ All checks passed!")
        return 0
    else:
        print(f"❌ {total_errors} error(s) found")
        return 1


if __name__ == '__main__':
    html_path = Path(__file__).parent.parent / 'index.html'
    
    if not html_path.exists():
        print(f"Error: {html_path} not found")
        sys.exit(1)
    
    exit_code = check_site(html_path)
    sys.exit(exit_code)
