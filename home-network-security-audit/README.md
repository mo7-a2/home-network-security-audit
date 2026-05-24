# 🔒 Home Network Security Audit

A comprehensive home network security assessment toolkit using **Nmap**, **Python**, and **Linux firewall hardening** techniques.

![Security Audit](https://img.shields.io/badge/Security-Audit-red?style=for-the-badge&logo=shield)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Nmap](https://img.shields.io/badge/Nmap-7.0+-green?style=for-the-badge)
![Linux](https://img.shields.io/badge/Linux-UFW%2FIPTables-orange?style=for-the-badge&logo=linux)

---

## 📋 Project Overview

This project simulates a real-world home network security audit. It includes:

- 🔍 **Network Scanning** — Discover active hosts and open ports using Nmap
- 🐍 **Automated Analysis** — Python script to parse and categorize scan results
- 🛡️ **Firewall Hardening** — Linux UFW/iptables rules to close vulnerabilities
- 📄 **Security Report** — Structured findings with risk ratings and recommendations

---

## 🗂️ Project Structure

```
home-network-security-audit/
│
├── scripts/
│   ├── scan_network.sh         # Nmap scanning script
│   ├── analyze_results.py      # Python parser & risk analyzer
│   └── firewall_hardening.sh   # Linux firewall hardening script
│
├── reports/
│   ├── scan_results.xml        # Raw Nmap XML output (sample)
│   └── security_report.md      # Final security audit report
│
├── configs/
│   └── ufw_rules.txt           # UFW firewall rules reference
│
├── docs/
│   └── methodology.md          # Audit methodology documentation
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

```bash
# Install Nmap
sudo apt-get install nmap

# Install Python dependencies
pip install python-nmap prettytable colorama

# Install UFW (if not present)
sudo apt-get install ufw
```

### Step 1 — Scan Your Network

```bash
# Make script executable
chmod +x scripts/scan_network.sh

# Run network scan (replace with your network range)
sudo ./scripts/scan_network.sh 192.168.1.0/24
```

### Step 2 — Analyze Results

```bash
python3 scripts/analyze_results.py --input reports/scan_results.xml
```

### Step 3 — Apply Firewall Hardening

```bash
# Review rules first!
cat scripts/firewall_hardening.sh

# Apply hardening (requires root)
sudo chmod +x scripts/firewall_hardening.sh
sudo ./scripts/firewall_hardening.sh
```

---

## 🔍 Scan Coverage

| Scan Type | Description | Nmap Flag |
|-----------|-------------|-----------|
| Host Discovery | Find active devices | `-sn` |
| Port Scan | Identify open ports (1–1024) | `-p 1-1024` |
| Service Detection | Detect running services | `-sV` |
| OS Fingerprinting | Identify operating systems | `-O` |
| Script Scan | Run vulnerability scripts | `-sC` |

---

## ⚠️ Risk Classification

| Risk Level | Color | Description |
|------------|-------|-------------|
| 🔴 Critical | Red | Immediate action required |
| 🟠 High | Orange | Fix within 24 hours |
| 🟡 Medium | Yellow | Fix within 1 week |
| 🟢 Low | Green | Best practice improvement |
| ⚪ Info | Gray | Informational finding |

---

## 🛡️ Firewall Rules Applied

- Block all incoming traffic by default
- Allow outbound traffic
- Permit SSH only from trusted IPs
- Rate-limit connection attempts (brute-force protection)
- Block common vulnerable ports (23, 135, 139, 445, 3389)
- Enable logging for suspicious activity

---

## 📊 Sample Findings

| Port | Service | Risk | Status |
|------|---------|------|--------|
| 23 | Telnet | 🔴 Critical | Blocked |
| 80 | HTTP | 🟡 Medium | Monitored |
| 443 | HTTPS | 🟢 Low | Allowed |
| 3389 | RDP | 🔴 Critical | Blocked |
| 445 | SMB | 🔴 Critical | Blocked |
| 22 | SSH | 🟠 High | Restricted |

---

## ⚖️ Legal Disclaimer

> **This toolkit is for educational and authorized testing purposes only.**
> Only scan networks you own or have explicit written permission to test.
> Unauthorized network scanning may violate laws in your jurisdiction.

---

## 🧑‍💻 Author

**[Your Name]**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
