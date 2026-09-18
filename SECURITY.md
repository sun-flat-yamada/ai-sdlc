# Security Policy

## Supported Versions

| Version | Supported          | Security Fixes |
| ------- | ------------------ | -------------- |
| 0.2.x   | :white_check_mark: | Active         |
| < 0.2.0 | :x:                | End of Life    |

---

## Reporting a Vulnerability

We take the security and confidentiality of **ASDLC (AI-Software-Development-Life-Cycle) SDK** very seriously.

If you believe you have discovered a security vulnerability, prompt injection threat (e.g. Clinejection), or credential leak issue in this repository:

1. **DO NOT** create a public GitHub Issue.
2. Please report the security concern via **GitHub Private Vulnerability Reporting** by navigating to the **Security** tab of this repository and clicking **Report a vulnerability**.
3. Alternatively, contact the maintainers directly via private security advisory channels.

### Information to Include
- Detailed steps to reproduce the issue.
- Affected component (e.g. 4D Auto-Triage, Coding Agent, Aegis Audit Bridge, Secret Scanner).
- Impact assessment (e.g., potential unauthorized access, prompt escape, secret leakage).
- Remediation suggestions or proof of concept (if available).

We will acknowledge receipt of your vulnerability report within 48 hours and provide a timeline for resolution.

---

## Multi-Layered Secret & Privacy Protection Architecture (Defense-in-Depth)

This repository implements a 4-layered defense-in-depth security model based on industry best practices (GitHub Secret Scanning, Google Antigravity Agent Rules, Gitleaks, OWASP API Security, and proud-noether security standards):

### Layer 1: Agent Guardrails & Behavioral Rules (`.agents/rules/`, `docs/charter/MEISTERS_CHARTER.md`)
- Autonomous AI coding assistants are bound by always-on directives prohibiting hardcoded secrets, plain API tokens, and internal PII in code, commit messages, and prompt context.
- The **Threat Defense Meister** enforces a minimum 70.0-point passing score specifically targeting zero-secret exposure and defense against indirect prompt injections (Clinejection).

### Layer 2: Local & Git Exclusion Hygiene (`.gitignore`)
- Comprehensive OWASP-compliant exclusion covering private keys (`*.pem`, `id_rsa`), certificates (`*.crt`, `*.keystore`), cloud credentials (`.aws/`, `.gcp/`, `service_account*.json`), `.env*`, and vault dumps.

### Layer 3: ASDLC Built-in Secret Scanner (`asdlc scan-secrets`) & Static Evaluation Gate
- High-performance pattern & Shannon entropy scanner (`asdlc/security/secret_scanner.py`) scanning all code, docs, and configurations.
- Integrated into **Tier 1 Static Evaluation** (`asdlc eval`), ensuring zero secrets or private keys are permitted across the entire codebase.

### Layer 4: Automated CI/CD Enforcement (`.github/workflows/secret-scan.yml`)
- Dual-engine scanning (`asdlc scan-secrets --strict` + Gitleaks Action) running on every pull request and push to enforce branch protection and zero-leakage compliance before merge.
