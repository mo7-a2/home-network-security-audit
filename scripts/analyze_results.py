#!/usr/bin/env python3
"""
==============================================================================
 Home Network Security Audit — Results Analyzer (Enhanced)
 Script: analyze_results.py
 Author: Mohamed Anwar Abdelhay Mahdy
 Description: Parses Nmap XML output, classifies risk levels,
              and generates a structured security report with logging.
==============================================================================
"""

import argparse
import xml.etree.ElementTree as ET
import logging
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional

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


# ─── Logging Configuration ────────────────────────────────────────────────────
def setup_logging(log_file: Optional[str] = None, verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the analysis script.

    Args:
        log_file: Optional path to log file
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("SecurityAudit")
    level = logging.DEBUG if verbose else logging.INFO

    logger.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


# ─── Risk Database ────────────────────────────────────────────────────────────
PORT_RISK: Dict[int, Tuple[str, str, str]] = {
    21: ("FTP", "CRITICAL", "Unencrypted file transfer — credentials sent in plaintext"),
    22: ("SSH", "MEDIUM", "Secure shell — ensure strong auth, disable root login"),
    23: ("Telnet", "CRITICAL", "Unencrypted remote access — replace with SSH immediately"),
    25: ("SMTP", "HIGH", "Mail server — check for open relay vulnerability"),
    53: ("DNS", "MEDIUM", "DNS service — check for zone transfer vulnerability"),
    80: ("HTTP", "MEDIUM", "Unencrypted web — check for sensitive data exposure"),
    110: ("POP3", "HIGH", "Unencrypted mail retrieval — use POP3S (995) instead"),
    135: ("MS-RPC", "CRITICAL", "Windows RPC — frequently exploited, block externally"),
    139: ("NetBIOS", "CRITICAL", "Legacy Windows networking — disable if not needed"),
    143: ("IMAP", "HIGH", "Unencrypted mail access — use IMAPS (993) instead"),
    443: ("HTTPS", "LOW", "Encrypted web — verify TLS version and certificates"),
    445: ("SMB", "CRITICAL", "Windows file sharing — target of ransomware (EternalBlue)"),
    993: ("IMAPS", "LOW", "Encrypted IMAP — ensure valid certificate"),
    995: ("POP3S", "LOW", "Encrypted POP3 — ensure valid certificate"),
    1433: ("MSSQL", "CRITICAL", "SQL Server — never expose to internet"),
    3306: ("MySQL", "CRITICAL", "MySQL database — never expose to internet"),
    3389: ("RDP", "CRITICAL", "Windows Remote Desktop — frequent brute-force target"),
    5900: ("VNC", "CRITICAL", "Remote desktop — weak auth, often exploited"),
    8080: ("HTTP-Alt", "MEDIUM", "Alternative HTTP — check for admin panels"),
    8443: ("HTTPS-Alt", "MEDIUM", "Alternative HTTPS — verify authentication"),
}

RISK_COLORS: Dict[str, str] = {
    "CRITICAL": Fore.RED,
    "HIGH": Fore.MAGENTA,
    "MEDIUM": Fore.YELLOW,
    "LOW": Fore.GREEN,
    "INFO": Fore.CYAN,
}

RISK_EMOJI: Dict[str, str] = {
    "CRITICAL": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "LOW": "🟢",
    "INFO": "⚪",
}

RISK_PRIORITY: Dict[str, int] = {
    "CRITICAL": 1,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 4,
    "INFO": 5,
}


class SecurityAnalyzer:
    """Main analyzer class for security audit results."""

    def __init__(self, logger: logging.Logger):
        """
        Initialize the analyzer.

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.findings: List[Dict] = []
        self.hosts: List[str] = []

    def parse_nmap_xml(self, xml_file: str) -> bool:
        """
        Parse Nmap XML output file.

        Args:
            xml_file: Path to Nmap XML output

        Returns:
            True if parsing successful, False otherwise
        """
        try:
            self.logger.info(f"Parsing Nmap XML: {xml_file}")
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for host in root.findall("host"):
                self._process_host(host)

            self.logger.info(f"Successfully parsed {len(self.hosts)} hosts")
            return True

        except ET.ParseError as e:
            self.logger.error(f"XML parsing error: {e}")
            return False
        except FileNotFoundError:
            self.logger.error(f"XML file not found: {xml_file}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error parsing XML: {e}")
            return False

    def _process_host(self, host_element: ET.Element) -> None:
        """Process a single host element from Nmap output."""
        host_ip = host_element.find("address").get("addr")
        self.hosts.append(host_ip)
        self.logger.debug(f"Processing host: {host_ip}")

        ports = host_element.find("ports")
        if ports is None:
            return

        for port in ports.findall("port"):
            self._process_port(port, host_ip)

    def _process_port(self, port_element: ET.Element, host_ip: str) -> None:
        """Process a single port element."""
        port_id = int(port_element.get("portid"))
        state = port_element.find("state").get("state")

        if state != "open":
            return

        service = port_element.find("service")
        service_name = service.get("name") if service else "unknown"

        risk_level, recommendation = self._get_risk_level(port_id)

        finding = {
            "host": host_ip,
            "port": port_id,
            "service": service_name,
            "risk": risk_level,
            "recommendation": recommendation,
            "timestamp": datetime.now().isoformat(),
        }

        self.findings.append(finding)
        self.logger.debug(f"Found open port {port_id}/{service_name} on {host_ip}: {risk_level}")

    def _get_risk_level(self, port: int) -> Tuple[str, str]:
        """Get risk level for a port."""
        if port in PORT_RISK:
            _, risk, rec = PORT_RISK[port]
            return risk, rec
        return "INFO", "Unknown service — verify purpose and security"

    def generate_report(self, output_format: str = "text") -> str:
        """
        Generate security report.

        Args:
            output_format: Report format (text, json, html)

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate text format report."""
        report = []
        report.append("\n" + "=" * 70)
        report.append("SECURITY AUDIT REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Hosts Scanned: {len(self.hosts)}")
        report.append(f"Total Findings: {len(self.findings)}\n")

        # Summary by risk level
        risk_summary = defaultdict(int)
        for finding in self.findings:
            risk_summary[finding["risk"]] += 1

        report.append("RISK SUMMARY:")
        for risk in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            count = risk_summary[risk]
            emoji = RISK_EMOJI.get(risk, "")
            color = RISK_COLORS.get(risk, "")
            report.append(f"  {emoji} {risk:10} : {count:3} findings")

        report.append("\n" + "=" * 70)
        report.append("DETAILED FINDINGS:")
        report.append("=" * 70)

        # Sort by risk level
        sorted_findings = sorted(
            self.findings, key=lambda x: RISK_PRIORITY.get(x["risk"], 99)
        )

        for finding in sorted_findings:
            risk = finding["risk"]
            emoji = RISK_EMOJI.get(risk, "")
            report.append(
                f"\n{emoji} {risk} | Host: {finding['host']} | "
                f"Port: {finding['port']} | Service: {finding['service']}"
            )
            report.append(f"   Recommendation: {finding['recommendation']}")

        report.append("\n" + "=" * 70 + "\n")
        return "\n".join(report)

    def _generate_json_report(self) -> str:
        """Generate JSON format report."""
        report_data = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "hosts_scanned": len(self.hosts),
                "total_findings": len(self.findings),
            },
            "hosts": self.hosts,
            "findings": self.findings,
        }
        return json.dumps(report_data, indent=2)

    def _generate_html_report(self) -> str:
        """Generate HTML format report."""
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>Security Audit Report</title>",
            "<style>",
            "body { font-family: Arial; margin: 20px; }",
            "table { border-collapse: collapse; width: 100%; margin: 20px 0; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #4CAF50; color: white; }",
            ".critical { color: red; }",
            ".high { color: orange; }",
            ".medium { color: gold; }",
            ".low { color: green; }",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Security Audit Report</h1>",
            f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            f"<p>Hosts Scanned: {len(self.hosts)}</p>",
            f"<p>Total Findings: {len(self.findings)}</p>",
            "<table>",
            "<tr><th>Host</th><th>Port</th><th>Service</th><th>Risk</th><th>Recommendation</th></tr>",
        ]

        for finding in self.findings:
            risk_class = finding["risk"].lower()
            html.append(
                f"<tr class='{risk_class}'>"
                f"<td>{finding['host']}</td>"
                f"<td>{finding['port']}</td>"
                f"<td>{finding['service']}</td>"
                f"<td>{finding['risk']}</td>"
                f"<td>{finding['recommendation']}</td>"
                f"</tr>"
            )

        html.extend(["</table>", "</body>", "</html>"])
        return "\n".join(html)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Home Network Security Audit — Results Analyzer"
    )
    parser.add_argument("--input", required=True, help="Path to Nmap XML output")
    parser.add_argument(
        "--format",
        choices=["text", "json", "html"],
        default="text",
        help="Output format",
    )
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument("--log", help="Log file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(args.log, args.verbose)
    logger.info("Starting security analysis...")

    # Analyze
    analyzer = SecurityAnalyzer(logger)
    if not analyzer.parse_nmap_xml(args.input):
        logger.error("Failed to parse Nmap XML")
        return 1

    # Generate report
    report = analyzer.generate_report(args.format)

    # Output
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            f.write(report)
        logger.info(f"Report saved to: {args.output}")
    else:
        print(report)

    logger.info("Analysis complete")
    return 0


if __name__ == "__main__":
    exit(main())
