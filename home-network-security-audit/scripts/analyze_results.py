#!/usr/bin/env python3
"""
==============================================================================
 Home Network Security Audit — Results Analyzer
 Script: analyze_results.py
 Author: [Your Name]
 Description: Parses Nmap XML output, classifies risk levels,
              and generates a structured security report.
==============================================================================
"""

import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict

try:
    from prettytable import PrettyTable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        RED = GREEN = YELLOW = CYAN = WHITE = BLUE = MAGENTA = ""
    class Style:
        BRIGHT = RESET_ALL = ""


# ─── Risk Database ────────────────────────────────────────────────────────────
PORT_RISK = {
    21:   ("FTP",          "CRITICAL", "Unencrypted file transfer — credentials sent in plaintext"),
    22:   ("SSH",          "MEDIUM",   "Secure shell — ensure strong auth, disable root login"),
    23:   ("Telnet",       "CRITICAL", "Unencrypted remote access — replace with SSH immediately"),
    25:   ("SMTP",         "HIGH",     "Mail server — check for open relay vulnerability"),
    53:   ("DNS",          "MEDIUM",   "DNS service — check for zone transfer vulnerability"),
    80:   ("HTTP",         "MEDIUM",   "Unencrypted web — check for sensitive data exposure"),
    110:  ("POP3",         "HIGH",     "Unencrypted mail retrieval — use POP3S (995) instead"),
    135:  ("MS-RPC",       "CRITICAL", "Windows RPC — frequently exploited, block externally"),
    139:  ("NetBIOS",      "CRITICAL", "Legacy Windows networking — disable if not needed"),
    143:  ("IMAP",         "HIGH",     "Unencrypted mail access — use IMAPS (993) instead"),
    443:  ("HTTPS",        "LOW",      "Encrypted web — verify TLS version and certificates"),
    445:  ("SMB",          "CRITICAL", "Windows file sharing — target of ransomware (EternalBlue)"),
    993:  ("IMAPS",        "LOW",      "Encrypted IMAP — ensure valid certificate"),
    995:  ("POP3S",        "LOW",      "Encrypted POP3 — ensure valid certificate"),
    1433: ("MSSQL",        "CRITICAL", "SQL Server — never expose to internet"),
    3306: ("MySQL",        "CRITICAL", "MySQL database — never expose to internet"),
    3389: ("RDP",          "CRITICAL", "Windows Remote Desktop — frequent brute-force target"),
    5900: ("VNC",          "CRITICAL", "Remote desktop — weak auth, often exploited"),
    8080: ("HTTP-Alt",     "MEDIUM",   "Alternative HTTP — check for admin panels"),
    8443: ("HTTPS-Alt",    "MEDIUM",   "Alternative HTTPS — verify authentication"),
}

RISK_COLORS = {
    "CRITICAL": Fore.RED,
    "HIGH":     Fore.MAGENTA,
    "MEDIUM":   Fore.YELLOW,
    "LOW":      Fore.GREEN,
    "INFO":     Fore.CYAN,
}

RISK_EMOJI = {
    "CRITICAL": "🔴",
    "HIGH":     "🟠",
    "MEDIUM":   "🟡",
    "LOW":      "🟢",
    "INFO":     "⚪",
}


# ─── Parser ───────────────────────────────────────────────────────────────────
def parse_nmap_xml(filepath: str) -> list[dict]:
    """Parse Nmap XML output and return list of host findings."""
    hosts = []
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"{Fore.RED}[ERROR] Could not parse XML: {e}{Style.RESET_ALL}")
        return []
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] File not found: {filepath}{Style.RESET_ALL}")
        return []

    for host in root.findall("host"):
        # Skip hosts that are down
        status = host.find("status")
        if status is not None and status.get("state") != "up":
            continue

        # Get IP address
        ip = ""
        hostname = ""
        for addr in host.findall("address"):
            if addr.get("addrtype") == "ipv4":
                ip = addr.get("addr", "")
            elif addr.get("addrtype") == "mac":
                pass  # Could grab MAC too

        # Get hostname
        hostnames = host.find("hostnames")
        if hostnames is not None:
            for hn in hostnames.findall("hostname"):
                hostname = hn.get("name", "")
                break

        # Get OS
        os_name = "Unknown"
        os_elem = host.find("os")
        if os_elem is not None:
            osmatch = os_elem.find("osmatch")
            if osmatch is not None:
                os_name = osmatch.get("name", "Unknown")

        # Get open ports
        open_ports = []
        ports_elem = host.find("ports")
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                state = port.find("state")
                if state is None or state.get("state") != "open":
                    continue

                portid = int(port.get("portid", 0))
                protocol = port.get("protocol", "tcp")

                service_elem = port.find("service")
                service_name = "unknown"
                service_version = ""
                if service_elem is not None:
                    service_name = service_elem.get("name", "unknown")
                    product = service_elem.get("product", "")
                    version = service_elem.get("version", "")
                    service_version = f"{product} {version}".strip()

                # Classify risk
                if portid in PORT_RISK:
                    known_service, risk, description = PORT_RISK[portid]
                else:
                    known_service = service_name
                    risk = "INFO"
                    description = "Unknown service — investigate manually"

                open_ports.append({
                    "port":        portid,
                    "protocol":    protocol,
                    "service":     known_service,
                    "version":     service_version,
                    "risk":        risk,
                    "description": description,
                })

        if ip:
            hosts.append({
                "ip":       ip,
                "hostname": hostname,
                "os":       os_name,
                "ports":    open_ports,
            })

    return hosts


# ─── Display ──────────────────────────────────────────────────────────────────
def print_banner():
    print(f"\n{Fore.CYAN}{Style.BRIGHT}")
    print("╔══════════════════════════════════════════════════════╗")
    print("║      HOME NETWORK SECURITY AUDIT — ANALYZER         ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")


def print_host_findings(hosts: list[dict]):
    if not hosts:
        print(f"{Fore.YELLOW}[!] No active hosts found in scan results.{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}{Style.BRIGHT}{'═'*60}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}  SCAN RESULTS — {len(hosts)} Host(s) Found{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}\n")

    for host in hosts:
        label = f"{host['ip']}"
        if host['hostname']:
            label += f" ({host['hostname']})"
        print(f"{Style.BRIGHT}  🖥  Host: {Fore.CYAN}{label}{Style.RESET_ALL}")
        print(f"      OS:   {host['os']}")
        print(f"      Open Ports: {len(host['ports'])}\n")

        if not host["ports"]:
            print(f"      {Fore.GREEN}  ✓ No open ports detected{Style.RESET_ALL}\n")
            continue

        if HAS_PRETTYTABLE:
            table = PrettyTable()
            table.field_names = ["Port", "Protocol", "Service", "Version", "Risk", "Description"]
            table.align = "l"
            for p in sorted(host["ports"], key=lambda x: (
                ["CRITICAL","HIGH","MEDIUM","LOW","INFO"].index(x["risk"])
            )):
                color = RISK_COLORS.get(p["risk"], "")
                emoji = RISK_EMOJI.get(p["risk"], "")
                table.add_row([
                    p["port"],
                    p["protocol"].upper(),
                    p["service"],
                    p["version"][:30] if p["version"] else "—",
                    f"{emoji} {p['risk']}",
                    p["description"][:50],
                ])
            print(table)
        else:
            for p in sorted(host["ports"], key=lambda x: x["port"]):
                color = RISK_COLORS.get(p["risk"], "")
                emoji = RISK_EMOJI.get(p["risk"], "")
                print(f"      {p['port']:<6} {p['service']:<12} {color}{emoji} {p['risk']}{Style.RESET_ALL}")
                print(f"             → {p['description']}")
        print()


def print_summary(hosts: list[dict]):
    risk_counts = defaultdict(int)
    all_ports = []

    for host in hosts:
        for port in host["ports"]:
            risk_counts[port["risk"]] += 1
            all_ports.append(port)

    print(f"{Fore.CYAN}{Style.BRIGHT}{'═'*60}{Style.RESET_ALL}")
    print(f"{Style.BRIGHT}  RISK SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*60}{Style.RESET_ALL}")
    print(f"  {'Total Hosts Scanned':<30} {len(hosts)}")
    print(f"  {'Total Open Ports':<30} {len(all_ports)}")
    print()

    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        count = risk_counts[level]
        color = RISK_COLORS[level]
        emoji = RISK_EMOJI[level]
        bar = "█" * count
        print(f"  {color}{emoji} {level:<12}{Style.RESET_ALL} {count:>3}  {color}{bar}{Style.RESET_ALL}")

    print()

    # Recommendations
    critical_ports = [p for p in all_ports if p["risk"] == "CRITICAL"]
    if critical_ports:
        print(f"{Fore.RED}{Style.BRIGHT}  ⚠  IMMEDIATE ACTION REQUIRED:{Style.RESET_ALL}")
        for p in critical_ports:
            print(f"  {Fore.RED}  • Port {p['port']} ({p['service']}): {p['description']}{Style.RESET_ALL}")
        print()

    print(f"{Fore.GREEN}  ✓ Next step: Run firewall_hardening.sh to mitigate findings{Style.RESET_ALL}")
    print()


def generate_report(hosts: list[dict], output_file: str):
    """Generate a Markdown security report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 🔒 Home Network Security Audit Report",
        f"\n**Date:** {now}",
        f"**Total Hosts:** {len(hosts)}",
        "\n---\n",
        "## Executive Summary\n",
    ]

    total_ports = sum(len(h["ports"]) for h in hosts)
    risk_counts = defaultdict(int)
    for h in hosts:
        for p in h["ports"]:
            risk_counts[p["risk"]] += 1

    lines.append(f"The audit scanned **{len(hosts)} active host(s)** and identified **{total_ports} open port(s)**.\n")
    lines.append("| Risk Level | Count |")
    lines.append("|------------|-------|")
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
        lines.append(f"| {RISK_EMOJI[level]} {level} | {risk_counts[level]} |")

    lines.append("\n---\n")
    lines.append("## Detailed Findings\n")

    for host in hosts:
        label = host["ip"]
        if host["hostname"]:
            label += f" ({host['hostname']})"
        lines.append(f"### 🖥 Host: `{label}`")
        lines.append(f"- **OS:** {host['os']}")
        lines.append(f"- **Open Ports:** {len(host['ports'])}\n")

        if host["ports"]:
            lines.append("| Port | Service | Risk | Description |")
            lines.append("|------|---------|------|-------------|")
            for p in sorted(host["ports"], key=lambda x: x["port"]):
                lines.append(f"| {p['port']} | {p['service']} | {RISK_EMOJI[p['risk']]} {p['risk']} | {p['description']} |")
        else:
            lines.append("_No open ports detected._")
        lines.append("")

    lines.append("\n---\n")
    lines.append("## Recommendations\n")
    lines.append("1. **Close all CRITICAL ports** or restrict to trusted IPs only")
    lines.append("2. **Replace Telnet/FTP** with SSH/SFTP")
    lines.append("3. **Enable UFW firewall** and apply hardening script")
    lines.append("4. **Disable SMB/RDP** if not required on the network")
    lines.append("5. **Enable fail2ban** to prevent brute-force attacks")
    lines.append("6. **Change default credentials** on all network devices")
    lines.append("7. **Keep systems updated** — apply security patches regularly")
    lines.append("\n---\n")
    lines.append("*Generated by Home Network Security Audit Toolkit*")

    with open(output_file, "w") as f:
        f.write("\n".join(lines))

    print(f"{Fore.GREEN}  ✓ Report saved to: {output_file}{Style.RESET_ALL}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Analyze Nmap scan results and generate security report"
    )
    parser.add_argument("--input",  required=True,  help="Path to Nmap XML output file")
    parser.add_argument("--output", default="../reports/security_report.md",
                        help="Path for generated Markdown report")
    args = parser.parse_args()

    print_banner()

    print(f"{Fore.CYAN}[*] Parsing scan file: {args.input}{Style.RESET_ALL}\n")
    hosts = parse_nmap_xml(args.input)

    if not hosts:
        print(f"{Fore.YELLOW}[!] No results to analyze. Check the input file.{Style.RESET_ALL}")
        return

    print_host_findings(hosts)
    print_summary(hosts)

    print(f"{Fore.CYAN}[*] Generating Markdown report...{Style.RESET_ALL}")
    generate_report(hosts, args.output)


if __name__ == "__main__":
    main()
