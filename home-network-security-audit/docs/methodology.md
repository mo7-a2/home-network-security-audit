# 📖 Audit Methodology

## Overview

This home network security audit follows a structured approach based on industry-standard penetration testing frameworks (PTES, OWASP) adapted for home network environments.

---

## Audit Phases

### Phase 1 — Reconnaissance & Scoping
- Define audit scope (IP range, specific devices)
- Document all known devices on the network
- Identify network topology (router, switches, access points)

### Phase 2 — Host Discovery
**Goal:** Identify all active devices on the network

```bash
# Ping sweep — find live hosts
nmap -sn 192.168.1.0/24

# ARP scan — more reliable on local network
nmap -PR -sn 192.168.1.0/24
```

### Phase 3 — Port Scanning
**Goal:** Identify open ports and running services

```bash
# SYN scan with service detection
sudo nmap -sS -sV --top-ports 1000 192.168.1.0/24

# Full port scan (slower)
sudo nmap -sS -p- 192.168.1.0/24

# UDP scan (critical for DNS, SNMP)
sudo nmap -sU --top-ports 100 192.168.1.0/24
```

### Phase 4 — OS & Service Fingerprinting
**Goal:** Identify software versions for vulnerability matching

```bash
sudo nmap -O -sV --version-intensity 5 192.168.1.0/24
```

### Phase 5 — Vulnerability Assessment
**Goal:** Check for known CVEs and misconfigurations

```bash
# Run NSE vulnerability scripts
sudo nmap --script=vuln 192.168.1.0/24

# Check for specific vulnerabilities
sudo nmap --script=smb-vuln-ms17-010 192.168.1.0/24  # EternalBlue
sudo nmap --script=ssl-heartbleed 192.168.1.0/24      # Heartbleed
```

### Phase 6 — Analysis & Risk Rating
Each finding is rated using the following framework:

| Factor | Description |
|--------|-------------|
| **Likelihood** | How likely is exploitation? (Network-accessible vs. auth required) |
| **Impact** | What's the blast radius? (Data loss, lateral movement, full compromise) |
| **Exploitability** | Is there a public exploit? (CVE, Metasploit module) |
| **Compensating Controls** | Are mitigating factors present? (Firewall, auth, encryption) |

### Phase 7 — Remediation
- Apply firewall rules (UFW/iptables)
- Disable unnecessary services
- Update software to patched versions
- Change default credentials
- Implement network segmentation (IoT VLAN)

---

## Tools Used

| Tool | Version | Purpose |
|------|---------|---------|
| Nmap | 7.94 | Network scanning & host discovery |
| Python | 3.10+ | Automated result analysis |
| UFW | 0.36 | Linux firewall management |
| fail2ban | 0.11 | Brute-force protection |
| iptables | 1.8 | Low-level packet filtering |

---

## References

- [Nmap Official Documentation](https://nmap.org/docs.html)
- [NIST SP 800-115 — Technical Guide to Information Security Testing](https://csrc.nist.gov/publications/detail/sp/800-115/final)
- [CIS Benchmarks for Linux](https://www.cisecurity.org/cis-benchmarks)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [CVE Database](https://cve.mitre.org/)

---

*This project is for educational purposes. Only audit networks you own or have explicit permission to test.*
