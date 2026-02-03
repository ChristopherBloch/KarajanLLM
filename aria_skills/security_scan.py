# aria_skills/security_scan.py
"""
🔒 Security Scanning Skill - DevSecOps Focus

Provides security scanning capabilities for Aria's DevSecOps persona.
Integrates with common security tools and performs code analysis.
"""
import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .base import BaseSkill, SkillConfig, SkillResult, SkillStatus


class SeverityLevel(Enum):
    """Security finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    """A security finding from a scan."""
    severity: SeverityLevel
    category: str
    title: str
    description: str
    location: Optional[str] = None
    line_number: Optional[int] = None
    remediation: Optional[str] = None
    cwe_id: Optional[str] = None


class SecurityScanSkill(BaseSkill):
    """
    Security scanning and vulnerability detection.
    
    Capabilities:
    - Static code analysis patterns
    - Dependency vulnerability checks
    - Secret detection
    - Configuration auditing
    - Docker security scanning
    """
    
    # Common secret patterns to detect
    SECRET_PATTERNS = [
        (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?[\w-]{20,}', "API Key"),
        (r'(?i)(secret|password|passwd|pwd)\s*[=:]\s*["\'][^"\']+["\']', "Hardcoded Secret"),
        (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*=', "AWS Credential"),
        (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token"),
        (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
        (r'(?i)bearer\s+[a-zA-Z0-9\-._~+/]+=*', "Bearer Token"),
        (r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----', "Private Key"),
    ]
    
    # SQL Injection patterns
    SQL_PATTERNS = [
        (r'f["\'].*SELECT.*WHERE.*{', "Potential SQL Injection (f-string)"),
        (r'\.format\(.*SELECT.*WHERE', "Potential SQL Injection (format)"),
        (r'%s.*SELECT.*WHERE.*%', "Potential SQL Injection (% format)"),
        (r'execute\([^,]+\+', "Potential SQL Injection (concatenation)"),
    ]
    
    # Command injection patterns
    CMD_PATTERNS = [
        (r'os\.system\s*\([^)]*\+', "Potential Command Injection (os.system)"),
        (r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True', "Shell=True risk"),
        (r'eval\s*\(', "Dangerous eval() usage"),
        (r'exec\s*\(', "Dangerous exec() usage"),
    ]
    
    @property
    def name(self) -> str:
        return "security_scan"
    
    async def initialize(self) -> bool:
        """Initialize security scanner."""
        self._status = SkillStatus.AVAILABLE
        self.logger.info("🔒 Security scanner initialized")
        return True
    
    async def health_check(self) -> SkillStatus:
        """Check scanner availability."""
        return self._status
    
    async def scan_file(self, file_path: str) -> SkillResult:
        """
        Scan a single file for security issues.
        
        Args:
            file_path: Path to file to scan
            
        Returns:
            SkillResult with list of SecurityFinding
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return SkillResult.fail(f"File not found: {file_path}")
            
            content = path.read_text(encoding='utf-8', errors='ignore')
            findings = []
            
            # Check secrets
            findings.extend(self._scan_secrets(content, str(path)))
            
            # Check SQL injection (Python files)
            if path.suffix == '.py':
                findings.extend(self._scan_sql_injection(content, str(path)))
                findings.extend(self._scan_cmd_injection(content, str(path)))
            
            return SkillResult.ok({
                "file": str(path),
                "findings": [self._finding_to_dict(f) for f in findings],
                "finding_count": len(findings),
                "scanned_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Scan failed: {str(e)}")
    
    async def scan_directory(
        self, 
        directory: str, 
        extensions: Optional[list[str]] = None,
        exclude_dirs: Optional[list[str]] = None
    ) -> SkillResult:
        """
        Scan a directory recursively for security issues.
        
        Args:
            directory: Root directory to scan
            extensions: File extensions to include (e.g., ['.py', '.js'])
            exclude_dirs: Directories to skip (e.g., ['node_modules', '.git'])
            
        Returns:
            SkillResult with aggregated findings
        """
        extensions = extensions or ['.py', '.js', '.ts', '.yaml', '.yml', '.json', '.env']
        exclude_dirs = exclude_dirs or ['node_modules', '.git', '__pycache__', 'venv', '.venv']
        
        try:
            root = Path(directory)
            if not root.exists():
                return SkillResult.fail(f"Directory not found: {directory}")
            
            all_findings = []
            files_scanned = 0
            
            for file_path in root.rglob('*'):
                # Skip excluded directories
                if any(exc in file_path.parts for exc in exclude_dirs):
                    continue
                
                # Check extension
                if file_path.is_file() and file_path.suffix in extensions:
                    result = await self.scan_file(str(file_path))
                    if result.success and result.data:
                        all_findings.extend(result.data.get("findings", []))
                        files_scanned += 1
            
            # Summarize by severity
            severity_counts = {}
            for finding in all_findings:
                sev = finding.get("severity", "unknown")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            return SkillResult.ok({
                "directory": str(root),
                "files_scanned": files_scanned,
                "total_findings": len(all_findings),
                "by_severity": severity_counts,
                "findings": all_findings,
                "scanned_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Directory scan failed: {str(e)}")
    
    async def check_dependencies(self, requirements_file: str) -> SkillResult:
        """
        Check Python dependencies for known vulnerabilities.
        
        Args:
            requirements_file: Path to requirements.txt or pyproject.toml
            
        Returns:
            SkillResult with vulnerability information
        """
        try:
            path = Path(requirements_file)
            if not path.exists():
                return SkillResult.fail(f"File not found: {requirements_file}")
            
            content = path.read_text()
            packages = self._parse_requirements(content, path.suffix)
            
            # In production, this would query vulnerability databases
            # For now, check against known problematic patterns
            warnings = []
            
            for pkg, version in packages:
                # Flag packages without version pinning
                if not version:
                    warnings.append({
                        "package": pkg,
                        "issue": "No version pinning",
                        "severity": "medium",
                        "recommendation": f"Pin {pkg} to a specific version"
                    })
                # Flag known problematic packages
                if pkg.lower() in ['pyyaml', 'pillow', 'lxml']:
                    if not version or self._is_old_version(pkg, version):
                        warnings.append({
                            "package": pkg,
                            "issue": f"{pkg} should be regularly updated",
                            "severity": "low",
                            "recommendation": f"Ensure {pkg} is at latest version"
                        })
            
            return SkillResult.ok({
                "file": str(path),
                "packages_checked": len(packages),
                "warnings": warnings,
                "checked_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Dependency check failed: {str(e)}")
    
    async def audit_docker(self, dockerfile_path: str) -> SkillResult:
        """
        Audit a Dockerfile for security best practices.
        
        Args:
            dockerfile_path: Path to Dockerfile
            
        Returns:
            SkillResult with audit findings
        """
        try:
            path = Path(dockerfile_path)
            if not path.exists():
                return SkillResult.fail(f"File not found: {dockerfile_path}")
            
            content = path.read_text()
            findings = []
            
            # Check for root user
            if not re.search(r'^\s*USER\s+\w+', content, re.MULTILINE):
                findings.append({
                    "severity": "high",
                    "issue": "No USER directive - runs as root",
                    "recommendation": "Add USER directive to run as non-root"
                })
            
            # Check for latest tag
            if re.search(r'FROM\s+\w+:latest', content, re.IGNORECASE):
                findings.append({
                    "severity": "medium",
                    "issue": "Using :latest tag",
                    "recommendation": "Pin base image to specific version"
                })
            
            # Check for secrets in ENV
            if re.search(r'ENV\s+\w*(PASSWORD|SECRET|KEY|TOKEN)\w*\s*=', content, re.IGNORECASE):
                findings.append({
                    "severity": "critical",
                    "issue": "Potential secret in ENV directive",
                    "recommendation": "Use Docker secrets or build args"
                })
            
            # Check for HEALTHCHECK
            if 'HEALTHCHECK' not in content:
                findings.append({
                    "severity": "low",
                    "issue": "No HEALTHCHECK directive",
                    "recommendation": "Add HEALTHCHECK for container health monitoring"
                })
            
            # Check for COPY instead of ADD
            add_count = len(re.findall(r'^\s*ADD\s+', content, re.MULTILINE))
            if add_count > 0:
                findings.append({
                    "severity": "low",
                    "issue": f"Using ADD ({add_count} times) instead of COPY",
                    "recommendation": "Prefer COPY over ADD unless extracting archives"
                })
            
            return SkillResult.ok({
                "file": str(path),
                "findings": findings,
                "finding_count": len(findings),
                "audited_at": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            return SkillResult.fail(f"Docker audit failed: {str(e)}")
    
    # === Private Helper Methods ===
    
    def _scan_secrets(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Scan content for potential secrets."""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in self.SECRET_PATTERNS:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        severity=SeverityLevel.CRITICAL,
                        category="secret",
                        title=f"Potential {desc} detected",
                        description=f"Found pattern matching {desc}",
                        location=file_path,
                        line_number=i,
                        remediation="Remove secret and rotate if exposed"
                    ))
        return findings
    
    def _scan_sql_injection(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Scan Python code for SQL injection vulnerabilities."""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in self.SQL_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        severity=SeverityLevel.HIGH,
                        category="injection",
                        title=desc,
                        description="SQL queries should use parameterized queries",
                        location=file_path,
                        line_number=i,
                        remediation="Use parameterized queries instead of string formatting",
                        cwe_id="CWE-89"
                    ))
        return findings
    
    def _scan_cmd_injection(self, content: str, file_path: str) -> list[SecurityFinding]:
        """Scan Python code for command injection vulnerabilities."""
        findings = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in self.CMD_PATTERNS:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        severity=SeverityLevel.HIGH,
                        category="injection",
                        title=desc,
                        description="Dangerous command execution pattern detected",
                        location=file_path,
                        line_number=i,
                        remediation="Use subprocess with shell=False and argument lists",
                        cwe_id="CWE-78"
                    ))
        return findings
    
    def _finding_to_dict(self, finding: SecurityFinding) -> dict:
        """Convert SecurityFinding to dictionary."""
        return {
            "severity": finding.severity.value,
            "category": finding.category,
            "title": finding.title,
            "description": finding.description,
            "location": finding.location,
            "line_number": finding.line_number,
            "remediation": finding.remediation,
            "cwe_id": finding.cwe_id
        }
    
    def _parse_requirements(self, content: str, suffix: str) -> list[tuple[str, Optional[str]]]:
        """Parse package names and versions from requirements."""
        packages = []
        
        if suffix == '.txt':
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Handle various formats: pkg, pkg==1.0, pkg>=1.0, etc.
                    match = re.match(r'^([a-zA-Z0-9_-]+)([<>=!]+)?(.+)?', line)
                    if match:
                        packages.append((match.group(1), match.group(3)))
        
        elif suffix == '.toml':
            # Simple TOML parsing for dependencies
            in_deps = False
            for line in content.split('\n'):
                if '[tool.poetry.dependencies]' in line or '[project.dependencies]' in line:
                    in_deps = True
                    continue
                if in_deps and line.startswith('['):
                    break
                if in_deps and '=' in line:
                    parts = line.split('=')
                    pkg = parts[0].strip().strip('"')
                    ver = parts[1].strip().strip('"') if len(parts) > 1 else None
                    packages.append((pkg, ver))
        
        return packages
    
    def _is_old_version(self, package: str, version: str) -> bool:
        """Check if a version is potentially outdated."""
        # Simplified check - in production, query PyPI or security DB
        return False


# Skill instance factory
def create_skill(config: SkillConfig) -> SecurityScanSkill:
    """Create a security scan skill instance."""
    return SecurityScanSkill(config)
