#!/usr/bin/env python3
"""
Test email autoconfig files.
Verifies:
- Autoconfig XML files exist
- XML is well-formed
- Contains correct server configuration
"""

import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET


def test_autoconfig():
    """Test email autoconfig files."""
    print("Testing email autoconfig files...")
    print("=" * 60)
    
    errors = []
    base_path = Path(__file__).parent.parent
    
    # Test 1: Check mail/config-v1.1.xml exists
    print("\n1. Checking mail/config-v1.1.xml...")
    config_path = base_path / 'mail' / 'config-v1.1.xml'
    if not config_path.exists():
        errors.append("mail/config-v1.1.xml not found")
        print("   ❌ File not found")
    else:
        print("   ✓ File exists")
        
        # Parse and validate XML
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            
            # Check for required elements
            if root.tag != 'clientConfig':
                errors.append("Root element should be 'clientConfig'")
            
            # Check for IMAP server
            imap = root.find(".//incomingServer[@type='imap']")
            if imap is None:
                errors.append("IMAP server configuration not found")
            else:
                hostname = imap.find('hostname')
                port = imap.find('port')
                socketType = imap.find('socketType')
                
                if hostname is not None and hostname.text != 'business117.web-hosting.com':
                    errors.append(f"IMAP hostname incorrect: {hostname.text}")
                if port is not None and port.text != '993':
                    errors.append(f"IMAP port incorrect: {port.text}")
                if socketType is not None and socketType.text != 'SSL':
                    errors.append(f"IMAP should use SSL: {socketType.text}")
            
            # Check for SMTP server
            smtp = root.find(".//outgoingServer[@type='smtp']")
            if smtp is None:
                errors.append("SMTP server configuration not found")
            else:
                hostname = smtp.find('hostname')
                port = smtp.find('port')
                socketType = smtp.find('socketType')
                
                if hostname is not None and hostname.text != 'business117.web-hosting.com':
                    errors.append(f"SMTP hostname incorrect: {hostname.text}")
                if port is not None and port.text != '465':
                    errors.append(f"SMTP port incorrect: {port.text}")
                if socketType is not None and socketType.text != 'SSL':
                    errors.append(f"SMTP should use SSL: {socketType.text}")
            
            # Check for POP3 (should NOT exist)
            pop3 = root.find(".//incomingServer[@type='pop3']")
            if pop3 is not None:
                errors.append("POP3 configuration found but should not exist (IMAP/SMTP only)")
            
            if not errors:
                print("   ✓ XML is valid and contains correct configuration")
                
        except ET.ParseError as e:
            errors.append(f"XML parse error in mail/config-v1.1.xml: {e}")
            print(f"   ❌ XML parse error: {e}")
        except Exception as e:
            errors.append(f"Error reading mail/config-v1.1.xml: {e}")
            print(f"   ❌ Error: {e}")
    
    # Test 2: Check .well-known/autoconfig/mail/config-v1.1.xml exists
    print("\n2. Checking .well-known/autoconfig/mail/config-v1.1.xml...")
    wellknown_path = base_path / '.well-known' / 'autoconfig' / 'mail' / 'config-v1.1.xml'
    if not wellknown_path.exists():
        errors.append(".well-known/autoconfig/mail/config-v1.1.xml not found")
        print("   ❌ File not found")
    else:
        print("   ✓ File exists")
        # Verify it's the same as mail/config-v1.1.xml
        try:
            with open(config_path, 'r') as f1, open(wellknown_path, 'r') as f2:
                if f1.read() != f2.read():
                    errors.append(".well-known config differs from mail/config-v1.1.xml")
                    print("   ⚠ Content differs from mail/config-v1.1.xml")
                else:
                    print("   ✓ Content matches mail/config-v1.1.xml")
        except Exception as e:
            errors.append(f"Error comparing config files: {e}")
    
    # Test 3: Check autodiscover API exists
    print("\n3. Checking api/autodiscover.js...")
    autodiscover_path = base_path / 'api' / 'autodiscover.js'
    if not autodiscover_path.exists():
        errors.append("api/autodiscover.js not found")
        print("   ❌ File not found")
    else:
        print("   ✓ File exists")
        # Check for required content
        try:
            with open(autodiscover_path, 'r') as f:
                content = f.read()
                if 'business117.web-hosting.com' not in content:
                    errors.append("autodiscover.js missing correct server hostname")
                if 'IMAP' not in content:
                    errors.append("autodiscover.js missing IMAP configuration")
                if 'SMTP' not in content:
                    errors.append("autodiscover.js missing SMTP configuration")
                if '993' not in content:
                    errors.append("autodiscover.js missing IMAP port 993")
                if '465' not in content:
                    errors.append("autodiscover.js missing SMTP port 465")
                    
                if not any(err.startswith("autodiscover.js") for err in errors):
                    print("   ✓ Contains required configuration")
        except Exception as e:
            errors.append(f"Error reading api/autodiscover.js: {e}")
    
    # Test 4: Check vercel.json exists and has correct routing
    print("\n4. Checking vercel.json...")
    vercel_config_path = base_path / 'vercel.json'
    if not vercel_config_path.exists():
        errors.append("vercel.json not found")
        print("   ❌ File not found")
    else:
        print("   ✓ File exists")
        try:
            import json
            with open(vercel_config_path, 'r') as f:
                config = json.load(f)
                
            # Check for autodiscover route
            routes = config.get('routes', [])
            autodiscover_route = any('/autodiscover/autodiscover.xml' in r.get('src', '') for r in routes)
            if not autodiscover_route:
                errors.append("vercel.json missing autodiscover route")
                print("   ⚠ Missing autodiscover route")
            else:
                print("   ✓ Has autodiscover route")
                
        except json.JSONDecodeError as e:
            errors.append(f"vercel.json is not valid JSON: {e}")
            print(f"   ❌ Invalid JSON: {e}")
        except Exception as e:
            errors.append(f"Error reading vercel.json: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ {len(errors)} error(s) found:")
        for error in errors:
            print(f"   - {error}")
        return 1
    else:
        print("✅ All autoconfig tests passed!")
        return 0


if __name__ == '__main__':
    exit_code = test_autoconfig()
    sys.exit(exit_code)
