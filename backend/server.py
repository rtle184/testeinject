from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime
import shutil

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class DownloadRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    user_agent: str
    ip_address: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DownloadRecordCreate(BaseModel):
    filename: str
    user_agent: str = ""
    ip_address: str = ""

# Add static files directory
STATIC_DIR = ROOT_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Routes
@api_router.get("/")
async def root():
    return {"message": "MSI Download Service Online"}

@api_router.get("/download/sample.msi")
async def download_sample_msi():
    """Download sample MSI file - replace with your actual MSI"""
    # For demo purposes, create a simple MSI file
    sample_msi_path = STATIC_DIR / "sample.msi"
    
    # Create a dummy MSI file if it doesn't exist
    if not sample_msi_path.exists():
        # In real implementation, you would have your actual MSI file here
        with open(sample_msi_path, "wb") as f:
            f.write(b"PK\x03\x04" + b"\x00" * 100)  # Dummy file content
    
    return FileResponse(
        path=sample_msi_path,
        filename="sample.msi",
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=sample.msi"}
    )

@api_router.get("/download/protocol-helper.reg")
async def download_protocol_helper():
    """Download the registry file to register custom protocol"""
    reg_content = '''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\\msiexec]
@="MSI Executor Protocol"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\\msiexec\\DefaultIcon]
@="C:\\\\Windows\\\\System32\\\\msiexec.exe,0"

[HKEY_CLASSES_ROOT\\msiexec\\shell]

[HKEY_CLASSES_ROOT\\msiexec\\shell\\open]

[HKEY_CLASSES_ROOT\\msiexec\\shell\\open\\command]
@="powershell.exe -WindowStyle Hidden -Command \\"$file = '%1' -replace 'msiexec://', ''; if (Test-Path $file) { Start-Process 'msiexec.exe' -ArgumentList '/i', $file -Verb RunAs } else { [System.Windows.Forms.MessageBox]::Show('File not found: ' + $file, 'Error', 'OK', 'Error') }\\""
'''
    
    reg_file_path = STATIC_DIR / "protocol-helper.reg"
    with open(reg_file_path, "w", encoding="utf-8") as f:
        f.write(reg_content)
    
    return FileResponse(
        path=reg_file_path,
        filename="protocol-helper.reg",
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=protocol-helper.reg"}
    )

@api_router.get("/download/installer-helper.ps1")
async def download_powershell_helper():
    """Download PowerShell script for easier setup"""
    ps_content = '''# MSI Auto-Installer Helper Script
# Run this script as Administrator

Write-Host "MSI Auto-Installer Setup" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "This script requires Administrator privileges. Please run as Administrator." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Register the protocol handler
Write-Host "Registering MSI protocol handler..." -ForegroundColor Yellow

$regPath = "HKCR:\\msiexec"
if (!(Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}

Set-ItemProperty -Path $regPath -Name "(Default)" -Value "MSI Executor Protocol"
Set-ItemProperty -Path $regPath -Name "URL Protocol" -Value ""

$iconPath = "$regPath\\DefaultIcon"
if (!(Test-Path $iconPath)) {
    New-Item -Path $iconPath -Force | Out-Null
}
Set-ItemProperty -Path $iconPath -Name "(Default)" -Value "C:\\Windows\\System32\\msiexec.exe,0"

$shellPath = "$regPath\\shell\\open\\command"
if (!(Test-Path $shellPath)) {
    New-Item -Path $shellPath -Force | Out-Null
}

$command = "powershell.exe -WindowStyle Hidden -Command \\"\\$file = '%1' -replace 'msiexec://', ''; if (Test-Path \\$file) { Start-Process 'msiexec.exe' -ArgumentList '/i', \\$file -Verb RunAs } else { Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('File not found: ' + \\$file, 'Error', 'OK', 'Error') }\\""
Set-ItemProperty -Path $shellPath -Name "(Default)" -Value $command

Write-Host "Protocol handler registered successfully!" -ForegroundColor Green
Write-Host "You can now use msiexec://path/to/file.msi URLs to auto-install MSI files." -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")'''
    
    ps_file_path = STATIC_DIR / "installer-helper.ps1"
    with open(ps_file_path, "w", encoding="utf-8") as f:
        f.write(ps_content)
    
    return FileResponse(
        path=ps_file_path,
        filename="installer-helper.ps1",
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=installer-helper.ps1"}
    )

@api_router.post("/track-download", response_model=DownloadRecord)
async def track_download(record: DownloadRecordCreate):
    """Track download statistics"""
    download_record = DownloadRecord(**record.dict())
    await db.downloads.insert_one(download_record.dict())
    return download_record

@api_router.get("/downloads", response_model=List[DownloadRecord])
async def get_downloads():
    """Get download statistics"""
    downloads = await db.downloads.find().to_list(1000)
    return [DownloadRecord(**download) for download in downloads]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()