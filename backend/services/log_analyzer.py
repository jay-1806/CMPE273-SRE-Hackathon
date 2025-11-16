"""
Log analyzer service to find top error IPs and analyze system logs
"""
import re
from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
from datetime import datetime
from backend.core.config import settings


class LogAnalyzer:
    """Service for analyzing system logs"""

    @staticmethod
    def parse_log_line(line: str) -> Dict[str, Any]:
        """Parse a single log line"""
        # Common log format patterns
        patterns = [
            # Apache/Nginx format: IP - - [timestamp] "REQUEST" status size
            r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?\[(?P<timestamp>.*?)\].*?"(?P<request>.*?)".*?(?P<status>\d{3})',
            # Syslog format: timestamp hostname service: message
            r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*?(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            # Custom format with ERROR/WARN
            r'(?P<level>ERROR|WARN|INFO|DEBUG).*?(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
        ]

        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.groupdict()

        # Fallback: try to extract IP
        ip_match = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
        if ip_match:
            return {"ip": ip_match.group(), "raw": line}

        return {"raw": line}

    @staticmethod
    def analyze_log_file(file_path: str) -> Dict[str, Any]:
        """Analyze a log file and extract insights"""
        try:
            error_ips = Counter()
            warning_ips = Counter()
            all_ips = Counter()
            error_messages = []
            status_codes = Counter()
            hourly_errors = defaultdict(int)

            total_lines = 0
            error_lines = 0

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    total_lines += 1
                    parsed = LogAnalyzer.parse_log_line(line)

                    # Count IPs
                    if 'ip' in parsed:
                        ip = parsed['ip']
                        all_ips[ip] += 1

                        # Check for errors
                        if 'status' in parsed:
                            status = int(parsed['status'])
                            status_codes[status] += 1

                            if status >= 400:
                                error_ips[ip] += 1
                                error_lines += 1

                                if status >= 500:
                                    error_messages.append({
                                        "ip": ip,
                                        "status": status,
                                        "line": line.strip()[:200]
                                    })

                        # Check error level
                        if 'level' in parsed:
                            if parsed['level'] in ['ERROR', 'CRITICAL']:
                                error_ips[ip] += 1
                                error_lines += 1
                            elif parsed['level'] == 'WARN':
                                warning_ips[ip] += 1

            return {
                "summary": {
                    "total_lines": total_lines,
                    "error_lines": error_lines,
                    "error_rate": round(error_lines / total_lines * 100, 2) if total_lines > 0 else 0,
                    "unique_ips": len(all_ips),
                    "unique_error_ips": len(error_ips)
                },
                "top_error_ips": [
                    {"ip": ip, "count": count, "percentage": round(count / error_lines * 100, 2)}
                    for ip, count in error_ips.most_common(10)
                ] if error_lines > 0 else [],
                "top_warning_ips": [
                    {"ip": ip, "count": count}
                    for ip, count in warning_ips.most_common(10)
                ],
                "top_active_ips": [
                    {"ip": ip, "count": count}
                    for ip, count in all_ips.most_common(10)
                ],
                "status_code_distribution": dict(status_codes.most_common()),
                "recent_errors": error_messages[-20:],  # Last 20 errors
            }

        except FileNotFoundError:
            return {
                "error": f"Log file not found: {file_path}",
                "summary": {"total_lines": 0, "error_lines": 0}
            }
        except Exception as e:
            return {
                "error": f"Error analyzing log file: {str(e)}",
                "summary": {"total_lines": 0, "error_lines": 0}
            }

    @staticmethod
    def get_ip_details(file_path: str, ip_address: str) -> Dict[str, Any]:
        """Get detailed information about a specific IP"""
        try:
            activities = []
            error_count = 0
            warning_count = 0
            total_requests = 0

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if ip_address in line:
                        total_requests += 1
                        parsed = LogAnalyzer.parse_log_line(line)

                        activity = {
                            "timestamp": parsed.get("timestamp", "unknown"),
                            "line": line.strip()[:200]
                        }

                        if 'status' in parsed and int(parsed['status']) >= 400:
                            error_count += 1
                            activity["type"] = "error"
                        elif 'level' in parsed:
                            if parsed['level'] in ['ERROR', 'CRITICAL']:
                                error_count += 1
                                activity["type"] = "error"
                            elif parsed['level'] == 'WARN':
                                warning_count += 1
                                activity["type"] = "warning"

                        activities.append(activity)

            return {
                "ip": ip_address,
                "total_requests": total_requests,
                "error_count": error_count,
                "warning_count": warning_count,
                "error_rate": round(error_count / total_requests * 100, 2) if total_requests > 0 else 0,
                "activities": activities[-50:]  # Last 50 activities
            }

        except Exception as e:
            return {
                "error": f"Error getting IP details: {str(e)}",
                "ip": ip_address
            }

    @staticmethod
    def generate_sample_log(output_path: str = "sample_log.txt", num_lines: int = 1000):
        """Generate a sample log file for testing"""
        import random

        ips = [f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}" for _ in range(50)]
        status_codes = [200, 200, 200, 200, 201, 304, 400, 401, 403, 404, 500, 502, 503]
        log_levels = ["INFO", "INFO", "INFO", "WARN", "ERROR", "ERROR", "CRITICAL"]

        with open(output_path, 'w') as f:
            for i in range(num_lines):
                ip = random.choice(ips)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                status = random.choice(status_codes)
                level = random.choice(log_levels)

                # Mix different log formats
                format_type = random.randint(1, 3)
                if format_type == 1:
                    # Apache format
                    f.write(f'{ip} - - [{timestamp}] "GET /api/devices HTTP/1.1" {status} 1234\n')
                elif format_type == 2:
                    # Application log
                    f.write(f'[{timestamp}] {level}: Request from {ip} - Status: {status}\n')
                else:
                    # Custom format
                    f.write(f'{timestamp} device-monitor {level}: IP {ip} accessed endpoint, response {status}\n')

        return f"Generated {num_lines} log lines at {output_path}"


# Export singleton instance
log_analyzer = LogAnalyzer()
