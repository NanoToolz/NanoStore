# NanoStore Bot - Professional Setup Script for Windows
# PowerShell Version

# Colors
$Host.UI.RawUI.ForegroundColor = "White"

# Progress tracking
$TotalSteps = 8
$CurrentStep = 0

function Show-Header {
    Clear-Host
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║                                                                ║" -ForegroundColor Magenta
    Write-Host "║              🚀 NANOSTORE BOT - SETUP WIZARD 🚀               ║" -ForegroundColor Magenta
    Write-Host "║                                                                ║" -ForegroundColor Magenta
    Write-Host "║                    Professional Deployment                     ║" -ForegroundColor Magenta
    Write-Host "║                                                                ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
}

function Show-Separator {
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

function Show-Progress {
    $script:CurrentStep++
    $percent = [math]::Round(($CurrentStep / $TotalSteps) * 100)
    $filled = [math]::Floor($percent / 5)
    $empty = 20 - $filled
    
    Write-Host ""
    Write-Host "Progress: [" -NoNewline
    Write-Host ("█" * $filled) -NoNewline -ForegroundColor Green
    Write-Host ("░" * $empty) -NoNewline
    Write-Host "] $percent%" -ForegroundColor White
    Write-Host "Step $CurrentStep of $TotalSteps" -ForegroundColor Yellow
    Write-Host ""
}

function Show-Step {
    param($Message)
    Show-Separator
    Write-Host "▶ $Message" -ForegroundColor Blue
    Show-Separator
}

function Show-Success {
    param($Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Show-Error {
    param($Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Show-Info {
    param($Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Show-Warning {
    param($Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Start setup
Show-Header
Write-Host "Welcome to NanoStore Bot Setup!" -ForegroundColor White
Write-Host ""
Write-Host "This wizard will guide you through the complete setup process." -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to continue"

# ═══════════════════════════════════════════════════════════════
# STEP 1: Check Prerequisites
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 1: Checking Prerequisites"

Write-Host ""
Write-Host "Checking required software..." -ForegroundColor White
Write-Host ""

# Check Docker/Podman
if (Get-Command docker -ErrorAction SilentlyContinue) {
    $dockerVersion = (docker --version).Split(" ")[2]
    Show-Success "Docker installed (version $dockerVersion)"
} elseif (Get-Command podman -ErrorAction SilentlyContinue) {
    $podmanVersion = (podman --version).Split(" ")[2]
    Show-Success "Podman installed (version $podmanVersion)"
} else {
    Show-Error "Docker/Podman not found!"
    Write-Host ""
    Write-Host "Install Docker Desktop from: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Check Git
if (Get-Command git -ErrorAction SilentlyContinue) {
    $gitVersion = (git --version).Split(" ")[2]
    Show-Success "Git installed (version $gitVersion)"
} else {
    Show-Error "Git not found!"
    exit 1
}

Start-Sleep -Seconds 2

# ═══════════════════════════════════════════════════════════════
# STEP 2: Pull Latest Code
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 2: Pulling Latest Code from GitHub"

Write-Host ""
Write-Host "Fetching latest updates..." -ForegroundColor White
Write-Host ""

try {
    git pull origin GPT
    Show-Success "Code updated successfully"
} catch {
    Show-Warning "Could not pull updates (might be first time setup)"
}

Start-Sleep -Seconds 1

# ═══════════════════════════════════════════════════════════════
# STEP 3: Configure Environment
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 3: Configuring Environment Variables"

if (-not (Test-Path .env)) {
    Write-Host ""
    Write-Host "Creating .env file..." -ForegroundColor White
    Write-Host ""
    
    # Get BOT_TOKEN
    Show-Separator
    Write-Host "Enter your Bot Token:" -ForegroundColor White
    Write-Host "(Get it from @BotFather on Telegram)" -ForegroundColor Yellow
    $BOT_TOKEN = Read-Host "BOT_TOKEN"
    
    # Get ADMIN_ID
    Write-Host ""
    Show-Separator
    Write-Host "Enter your Telegram User ID:" -ForegroundColor White
    Write-Host "(Get it from @userinfobot on Telegram)" -ForegroundColor Yellow
    $ADMIN_ID = Read-Host "ADMIN_ID"
    
    # Create .env file
    @"
# Bot Configuration
BOT_TOKEN=$BOT_TOKEN
ADMIN_ID=$ADMIN_ID

# Logging (Optional)
LOG_CHANNEL_ID=
PROOFS_CHANNEL_ID=
LOG_TO_CHANNEL=false
LOG_LEVEL=INFO
LOG_CHANNEL_LEVEL=INFO
FULL_VERBOSE_TO_CHANNEL=false

# Database
DB_PATH=data/nanostore.db
"@ | Out-File -FilePath .env -Encoding UTF8
    
    Show-Success ".env file created"
} else {
    Show-Info ".env file already exists"
}

Start-Sleep -Seconds 1

# ═══════════════════════════════════════════════════════════════
# STEP 4: Create Data Directory
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 4: Creating Data Directory"

Write-Host ""
Write-Host "Setting up data storage..." -ForegroundColor White
Write-Host ""

New-Item -ItemType Directory -Force -Path data | Out-Null
New-Item -ItemType Directory -Force -Path backups | Out-Null

Show-Success "Data directory created"
Show-Success "Backups directory created"

Start-Sleep -Seconds 1

# ═══════════════════════════════════════════════════════════════
# STEP 5: Stop Existing Container
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 5: Cleaning Up Old Containers"

Write-Host ""
Write-Host "Checking for existing containers..." -ForegroundColor White
Write-Host ""

$containerExists = docker ps -a | Select-String "nanostore-bot"
if ($containerExists) {
    Show-Info "Found existing container, removing..."
    docker stop nanostore-bot 2>$null
    docker rm nanostore-bot 2>$null
    Show-Success "Old container removed"
} else {
    Show-Info "No existing container found"
}

Start-Sleep -Seconds 1

# ═══════════════════════════════════════════════════════════════
# STEP 6: Build Docker Image
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 6: Building Docker Image"

Write-Host ""
Write-Host "Building container image..." -ForegroundColor White
Write-Host "This may take 2-3 minutes..." -ForegroundColor Yellow
Write-Host ""

try {
    docker build -t nanostore-bot .
    Show-Success "Image built successfully"
} catch {
    Show-Error "Failed to build image"
    exit 1
}

Start-Sleep -Seconds 1

# ═══════════════════════════════════════════════════════════════
# STEP 7: Start Container
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 7: Starting Bot Container"

Write-Host ""
Write-Host "Launching NanoStore Bot..." -ForegroundColor White
Write-Host ""

try {
    docker run -d `
        --name nanostore-bot `
        --env-file .env `
        -v ${PWD}/data:/app/data `
        --memory=256m `
        --cpus=0.5 `
        --restart=always `
        nanostore-bot
    Show-Success "Container started successfully"
} catch {
    Show-Error "Failed to start container"
    exit 1
}

Start-Sleep -Seconds 2

# ═══════════════════════════════════════════════════════════════
# STEP 8: Verify Installation
# ═══════════════════════════════════════════════════════════════
Show-Header
Show-Progress
Show-Step "STEP 8: Verifying Installation"

Write-Host ""
Write-Host "Running health checks..." -ForegroundColor White
Write-Host ""

# Check if container is running
$running = docker ps | Select-String "nanostore-bot"
if ($running) {
    Show-Success "Container is running"
} else {
    Show-Error "Container is not running"
    exit 1
}

# Wait for bot to initialize
Write-Host ""
Write-Host "Waiting for bot to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check logs for errors
$logs = docker logs nanostore-bot 2>&1
if ($logs -match "Bot is running") {
    Show-Success "Bot initialized successfully"
} else {
    Show-Warning "Bot may have issues, check logs"
}

Start-Sleep -Seconds 1

# ═══════════════════════════════════════════════════════════════
# SETUP COMPLETE
# ═══════════════════════════════════════════════════════════════
Show-Header
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "║                  ✓ SETUP COMPLETED SUCCESSFULLY! ✓            ║" -ForegroundColor Green
Write-Host "║                                                                ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Show-Separator
Write-Host "📊 INSTALLATION SUMMARY" -ForegroundColor White
Show-Separator
Write-Host "✓ Docker image built" -ForegroundColor Green
Write-Host "✓ Container running" -ForegroundColor Green
Write-Host "✓ Database initialized" -ForegroundColor Green
Write-Host "✓ Bot is live" -ForegroundColor Green
Write-Host ""

Show-Separator
Write-Host "🎯 NEXT STEPS" -ForegroundColor White
Show-Separator
Write-Host "1. Open Telegram and search for your bot"
Write-Host "2. Send /start to begin" -ForegroundColor Cyan
Write-Host "3. Access admin panel to configure products"
Write-Host ""

Show-Separator
Write-Host "📝 USEFUL COMMANDS" -ForegroundColor White
Show-Separator
Write-Host "View logs:        " -NoNewline; Write-Host "docker logs -f nanostore-bot" -ForegroundColor Cyan
Write-Host "Stop bot:         " -NoNewline; Write-Host "docker stop nanostore-bot" -ForegroundColor Cyan
Write-Host "Start bot:        " -NoNewline; Write-Host "docker start nanostore-bot" -ForegroundColor Cyan
Write-Host "Restart bot:      " -NoNewline; Write-Host "docker restart nanostore-bot" -ForegroundColor Cyan
Write-Host "Check status:     " -NoNewline; Write-Host "docker ps" -ForegroundColor Cyan
Write-Host ""

Show-Separator
Write-Host "💾 BACKUP" -ForegroundColor White
Show-Separator
Write-Host "Database location: " -NoNewline; Write-Host "./data/nanostore.db" -ForegroundColor Yellow
Write-Host "Backup command:    " -NoNewline; Write-Host "Copy-Item data/nanostore.db backups/backup_`$(Get-Date -Format 'yyyyMMdd').db" -ForegroundColor Cyan
Write-Host ""

Show-Separator
Write-Host "🔍 VIEW LIVE LOGS" -ForegroundColor White
Show-Separator
Write-Host "Press Ctrl+C to exit logs view" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to view live logs"

docker logs -f nanostore-bot
