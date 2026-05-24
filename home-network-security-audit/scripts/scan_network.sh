#!/bin/bash
# =============================================================================
#  Home Network Security Audit — Network Scanner
#  Script: scan_network.sh
#  Author: [Your Name]
#  Description: Comprehensive Nmap scanning of home network
# =============================================================================

set -e

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ─── Config ───────────────────────────────────────────────────────────────────
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="../reports"
OUTPUT_XML="${OUTPUT_DIR}/scan_results_${TIMESTAMP}.xml"
OUTPUT_TXT="${OUTPUT_DIR}/scan_results_${TIMESTAMP}.txt"
TARGET="${1:-192.168.1.0/24}"

# ─── Banner ───────────────────────────────────────────────────────────────────
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║       HOME NETWORK SECURITY AUDIT SCANNER       ║"
echo "║              Powered by Nmap                     ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Checks ───────────────────────────────────────────────────────────────────
if ! command -v nmap &> /dev/null; then
    echo -e "${RED}[ERROR] Nmap is not installed.${NC}"
    echo "Install it with: sudo apt-get install nmap"
    exit 1
fi

if [[ $EUID -ne 0 ]]; then
    echo -e "${YELLOW}[WARNING] Some scans require root privileges. Run with sudo.${NC}"
fi

mkdir -p "$OUTPUT_DIR"

echo -e "${BOLD}[*] Target Network: ${CYAN}$TARGET${NC}"
echo -e "${BOLD}[*] Output Files:   ${CYAN}$OUTPUT_XML${NC}"
echo -e "${BOLD}[*] Timestamp:      ${CYAN}$TIMESTAMP${NC}"
echo ""

# ─── Phase 1: Host Discovery ──────────────────────────────────────────────────
echo -e "${GREEN}[Phase 1/4] Host Discovery...${NC}"
nmap -sn "$TARGET" -oG - 2>/dev/null | grep "Up" | awk '{print $2}' > /tmp/live_hosts.txt
HOST_COUNT=$(wc -l < /tmp/live_hosts.txt)
echo -e "  → Found ${BOLD}${HOST_COUNT}${NC} active hosts"
echo ""

# ─── Phase 2: Port Scan ───────────────────────────────────────────────────────
echo -e "${GREEN}[Phase 2/4] Port Scanning (Top 1000 ports)...${NC}"
nmap -sS -sV -O \
    --top-ports 1000 \
    --open \
    -iL /tmp/live_hosts.txt \
    -oX "$OUTPUT_XML" \
    -oN "$OUTPUT_TXT" \
    2>/dev/null
echo -e "  → Port scan complete"
echo ""

# ─── Phase 3: Vulnerability Scripts ───────────────────────────────────────────
echo -e "${GREEN}[Phase 3/4] Running NSE Vulnerability Scripts...${NC}"
nmap -sC \
    --script=vuln,auth,default \
    -iL /tmp/live_hosts.txt \
    -oX "${OUTPUT_DIR}/vuln_scan_${TIMESTAMP}.xml" \
    2>/dev/null || echo -e "  ${YELLOW}→ Script scan skipped (requires root)${NC}"
echo ""

# ─── Phase 4: Specific Dangerous Ports ────────────────────────────────────────
echo -e "${GREEN}[Phase 4/4] Checking High-Risk Ports...${NC}"
DANGEROUS_PORTS="21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,3306,3389,5900,8080,8443"
nmap -sS -p "$DANGEROUS_PORTS" \
    -iL /tmp/live_hosts.txt \
    -oN "${OUTPUT_DIR}/risky_ports_${TIMESTAMP}.txt" \
    2>/dev/null
echo -e "  → High-risk port scan complete"
echo ""

# ─── Summary ──────────────────────────────────────────────────────────────────
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${BOLD}  SCAN COMPLETE${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "  Active Hosts Found : ${BOLD}${HOST_COUNT}${NC}"
echo -e "  Full Report (XML)  : ${BOLD}${OUTPUT_XML}${NC}"
echo -e "  Full Report (TXT)  : ${BOLD}${OUTPUT_TXT}${NC}"
echo ""
echo -e "${YELLOW}[*] Next Step: Run the Python analyzer:${NC}"
echo -e "    ${BOLD}python3 analyze_results.py --input ${OUTPUT_XML}${NC}"
echo ""

# Cleanup
rm -f /tmp/live_hosts.txt
