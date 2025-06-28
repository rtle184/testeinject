#!/usr/bin/env python3
import requests
import unittest
import json
import os
from dotenv import load_dotenv
import sys

# Load environment variables from frontend/.env to get the backend URL
load_dotenv('/app/frontend/.env')

# Get the backend URL from environment variables
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    print("Error: REACT_APP_BACKEND_URL not found in environment variables")
    sys.exit(1)

# Ensure the URL ends with /api
API_URL = f"{BACKEND_URL}/api" if not BACKEND_URL.endswith('/api') else BACKEND_URL

print(f"Testing backend API at: {API_URL}")

class MSIAutoInstallerBackendTest(unittest.TestCase):
    """Test suite for the MSI Auto-Installer backend system"""

    def test_root_endpoint(self):
        """Test the root endpoint returns the correct message"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "MSI Download Service Online")
        print("✅ Root endpoint test passed")

    def test_msi_download(self):
        """Test the MSI download endpoint returns the correct file with proper headers"""
        response = requests.get(f"{API_URL}/download/sample.msi")
        self.assertEqual(response.status_code, 200)
        
        # Check content type
        self.assertEqual(response.headers['Content-Type'], 'application/octet-stream')
        
        # Check content disposition header
        self.assertIn('attachment; filename=sample.msi', response.headers['Content-Disposition'])
        
        # Check that we received some content
        self.assertTrue(len(response.content) > 0)
        
        print("✅ MSI download endpoint test passed")

    def test_protocol_helper_reg_download(self):
        """Test the protocol helper registry file download endpoint"""
        response = requests.get(f"{API_URL}/download/protocol-helper.reg")
        self.assertEqual(response.status_code, 200)
        
        # Check content type
        self.assertEqual(response.headers['Content-Type'], 'application/octet-stream')
        
        # Check content disposition header
        self.assertIn('attachment; filename=protocol-helper.reg', response.headers['Content-Disposition'])
        
        # Check that we received some content
        self.assertTrue(len(response.content) > 0)
        
        # Check that the content contains expected registry entries
        content = response.content.decode('utf-8')
        self.assertIn('Windows Registry Editor Version 5.00', content)
        self.assertIn('[HKEY_CLASSES_ROOT\\msiexec]', content)
        
        print("✅ Protocol helper registry file download test passed")

    def test_powershell_helper_download(self):
        """Test the PowerShell helper script download endpoint"""
        response = requests.get(f"{API_URL}/download/installer-helper.ps1")
        self.assertEqual(response.status_code, 200)
        
        # Check content type
        self.assertEqual(response.headers['Content-Type'], 'application/octet-stream')
        
        # Check content disposition header
        self.assertIn('attachment; filename=installer-helper.ps1', response.headers['Content-Disposition'])
        
        # Check that we received some content
        self.assertTrue(len(response.content) > 0)
        
        # Check that the content contains expected PowerShell script content
        content = response.content.decode('utf-8')
        self.assertIn('MSI Auto-Installer Helper Script', content)
        self.assertIn('Run this script as Administrator', content)
        
        print("✅ PowerShell helper script download test passed")

    def test_download_tracking(self):
        """Test the download tracking functionality"""
        # Create a test download record
        test_record = {
            "filename": "test-file.msi",
            "user_agent": "Test User Agent",
            "ip_address": "127.0.0.1"
        }
        
        # Track a download
        response = requests.post(f"{API_URL}/track-download", json=test_record)
        self.assertEqual(response.status_code, 200)
        
        # Verify the response contains the tracked download
        data = response.json()
        self.assertEqual(data["filename"], test_record["filename"])
        self.assertEqual(data["user_agent"], test_record["user_agent"])
        self.assertEqual(data["ip_address"], test_record["ip_address"])
        self.assertIn("id", data)
        self.assertIn("timestamp", data)
        
        print("✅ Download tracking test passed")

    def test_get_downloads(self):
        """Test retrieving download statistics"""
        # First, create a test download record to ensure there's data
        test_record = {
            "filename": "test-file-stats.msi",
            "user_agent": "Test Stats Agent",
            "ip_address": "127.0.0.2"
        }
        
        # Track a download
        track_response = requests.post(f"{API_URL}/track-download", json=test_record)
        self.assertEqual(track_response.status_code, 200)
        
        # Now get the download statistics
        response = requests.get(f"{API_URL}/downloads")
        self.assertEqual(response.status_code, 200)
        
        # Verify we got a list of downloads
        data = response.json()
        self.assertIsInstance(data, list)
        
        # Verify our test record is in the list
        found = False
        for download in data:
            if (download["filename"] == test_record["filename"] and 
                download["user_agent"] == test_record["user_agent"] and
                download["ip_address"] == test_record["ip_address"]):
                found = True
                break
        
        self.assertTrue(found, "Test download record not found in downloads list")
        
        print("✅ Get downloads test passed")

    def test_all_endpoints_with_different_user_agents(self):
        """Test all download endpoints with different user agents"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
        ]
        
        endpoints = [
            "/download/sample.msi",
            "/download/protocol-helper.reg",
            "/download/installer-helper.ps1"
        ]
        
        for user_agent in user_agents:
            for endpoint in endpoints:
                headers = {"User-Agent": user_agent}
                response = requests.get(f"{API_URL}{endpoint}", headers=headers)
                self.assertEqual(response.status_code, 200)
                
                # Track the download
                test_record = {
                    "filename": endpoint.split("/")[-1],
                    "user_agent": user_agent,
                    "ip_address": "192.168.1.1"
                }
                
                track_response = requests.post(f"{API_URL}/track-download", json=test_record)
                self.assertEqual(track_response.status_code, 200)
        
        # Verify all downloads were tracked
        response = requests.get(f"{API_URL}/downloads")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # We should have at least len(user_agents) * len(endpoints) downloads
        self.assertTrue(len(data) >= len(user_agents) * len(endpoints))
        
        print("✅ Multi-user agent download test passed")

if __name__ == "__main__":
    # Run the tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)