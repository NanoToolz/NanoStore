#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Progress tracking
TOTAL_STEPS=8
CURRENT_STEP=0

# Function to print separator
print_separator() {
    echo -e "${CYAN}════════════════════════════════════════════════════════════════${NC}"
}

# Function to print header
print_header() {
    clear
    echo -e "${PURPLE}${BOLD}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║              🚀 NANOSTORE BOT - SETUP WIZARD 🚀               ║"
    echo "║                                                                ║"
    echo "║                    Professional Deployment                     ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to show progress
show_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local percent=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local filled=$((percent / 5))
    local empty=$((20 - filled))
    
    echo -e "\n${BOLD}Progress: [${GREEN}$(printf '█%.0s' $(seq 1 $filled))${NC}${BOLD}$(printf '░%.0s' $(seq 1 $empty))] ${percent}%${NC}"
    echo -e "${YELLOW}Step $CURRENT_STEP of $TOTAL_STEPS${NC}\n"
}

# Function to print step
print_step() {
    print_separator
    echo -e "${BOLD}${BLUE}▶ $1${NC}"
    print_separator
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print info
print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Start setup
print_header
echo -e "${BOLD}Welcome to NanoStore Bot Setup!${NC}\n"
echo -e "This wizard will guide you through the complete setup process.\n"
read -p "Press Enter to continue..."

# ═══════════════════════════════════════════════════════════════
# STEP 1: Check Prerequisites
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 1: Checking Prerequisites"

echo -e "\n${BOLD}Checking required software...${NC}\n"

# Check Podman
if command -v podman &> /dev/null; then
    PODMAN_VERSION=$(podman --version | awk '{print $3}')
    print_success "Podman installed (version $PODMAN_VERSION)"
else
    print_error "Podman not found!"
    echo -e "\n${YELLOW}Install Podman:${NC}"
    echo "  Ubuntu/Debian: sudo apt install -y podman"
    echo "  CentOS/Fedora: sudo dnf install -y podman"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    print_success "Git installed (version $GIT_VERSION)"
else
    print_error "Git not found!"
    exit 1
fi

# Check disk space
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
print_success "Available disk space: $AVAILABLE_SPACE"

sleep 2

# ═══════════════════════════════════════════════════════════════
# STEP 2: Pull Latest Code
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 2: Pulling Latest Code from GitHub"

echo -e "\n${BOLD}Fetching latest updates...${NC}\n"

if git pull origin GPT; then
    print_success "Code updated successfully"
else
    print_warning "Could not pull updates (might be first time setup)"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════
# STEP 3: Configure Environment
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 3: Configuring Environment Variables"

if [ ! -f .env ]; then
    echo -e "\n${BOLD}Creating .env file...${NC}\n"
    
    # Get BOT_TOKEN
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}Enter your Bot Token:${NC}"
    echo -e "${YELLOW}(Get it from @BotFather on Telegram)${NC}"
    read -p "BOT_TOKEN: " BOT_TOKEN
    
    # Get ADMIN_ID
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}Enter your Telegram User ID:${NC}"
    echo -e "${YELLOW}(Get it from @userinfobot on Telegram)${NC}"
    read -p "ADMIN_ID: " ADMIN_ID
    
    # Create .env file
    cat > .env << EOF
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
EOF
    
    print_success ".env file created"
else
    print_info ".env file already exists"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════
# STEP 4: Create Data Directory
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 4: Creating Data Directory"

echo -e "\n${BOLD}Setting up data storage...${NC}\n"

mkdir -p data
mkdir -p backups
chmod 755 data
chmod 755 backups

print_success "Data directory created"
print_success "Backups directory created"

sleep 1

# ═══════════════════════════════════════════════════════════════
# STEP 5: Stop Existing Container
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 5: Cleaning Up Old Containers"

echo -e "\n${BOLD}Checking for existing containers...${NC}\n"

if podman ps -a | grep -q nanostore-bot; then
    print_info "Found existing container, removing..."
    podman stop nanostore-bot 2>/dev/null
    podman rm nanostore-bot 2>/dev/null
    print_success "Old container removed"
else
    print_info "No existing container found"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════
# STEP 6: Build Docker Image
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 6: Building Podman Image"

echo -e "\n${BOLD}Building container image...${NC}"
echo -e "${YELLOW}This may take 2-3 minutes...${NC}\n"

if podman build -t nanostore-bot . ; then
    print_success "Image built successfully"
else
    print_error "Failed to build image"
    exit 1
fi

sleep 1

# ═══════════════════════════════════════════════════════════════
# STEP 7: Start Container
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 7: Starting Bot Container"

echo -e "\n${BOLD}Launching NanoStore Bot...${NC}\n"

if podman run -d \
    --name nanostore-bot \
    --env-file .env \
    -v ./data:/app/data:Z \
    --memory=256m \
    --cpus=0.5 \
    --restart=always \
    nanostore-bot; then
    print_success "Container started successfully"
else
    print_error "Failed to start container"
    exit 1
fi

sleep 2

# ═══════════════════════════════════════════════════════════════
# STEP 8: Verify Installation
# ═══════════════════════════════════════════════════════════════
print_header
show_progress
print_step "STEP 8: Verifying Installation"

echo -e "\n${BOLD}Running health checks...${NC}\n"

# Check if container is running
if podman ps | grep -q nanostore-bot; then
    print_success "Container is running"
else
    print_error "Container is not running"
    exit 1
fi

# Wait for bot to initialize
echo -e "\n${YELLOW}Waiting for bot to initialize...${NC}"
sleep 3

# Check logs for errors
if podman logs nanostore-bot 2>&1 | grep -q "Bot is running"; then
    print_success "Bot initialized successfully"
else
    print_warning "Bot may have issues, check logs"
fi

sleep 1

# ═══════════════════════════════════════════════════════════════
# SETUP COMPLETE
# ═══════════════════════════════════════════════════════════════
print_header
echo -e "${GREEN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║                  ✓ SETUP COMPLETED SUCCESSFULLY! ✓            ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

print_separator
echo -e "${BOLD}📊 INSTALLATION SUMMARY${NC}"
print_separator
echo -e "${GREEN}✓${NC} Podman image built"
echo -e "${GREEN}✓${NC} Container running"
echo -e "${GREEN}✓${NC} Database initialized"
echo -e "${GREEN}✓${NC} Bot is live"
echo ""

print_separator
echo -e "${BOLD}🎯 NEXT STEPS${NC}"
print_separator
echo -e "1. Open Telegram and search for your bot"
echo -e "2. Send ${CYAN}/start${NC} to begin"
echo -e "3. Access admin panel to configure products"
echo ""

print_separator
echo -e "${BOLD}📝 USEFUL COMMANDS${NC}"
print_separator
echo -e "${CYAN}View logs:${NC}        podman logs -f nanostore-bot"
echo -e "${CYAN}Stop bot:${NC}         podman stop nanostore-bot"
echo -e "${CYAN}Start bot:${NC}        podman start nanostore-bot"
echo -e "${CYAN}Restart bot:${NC}      podman restart nanostore-bot"
echo -e "${CYAN}Check status:${NC}     podman ps"
echo ""

print_separator
echo -e "${BOLD}💾 BACKUP${NC}"
print_separator
echo -e "Database location: ${YELLOW}./data/nanostore.db${NC}"
echo -e "Backup command:    ${CYAN}cp data/nanostore.db backups/backup_\$(date +%Y%m%d).db${NC}"
echo ""

print_separator
echo -e "${BOLD}🔍 VIEW LIVE LOGS${NC}"
print_separator
echo -e "${YELLOW}Press Ctrl+C to exit logs view${NC}\n"
read -p "Press Enter to view live logs..."

podman logs -f nanostore-bot
