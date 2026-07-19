# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Samrat seriously. If you believe you have found a
security vulnerability, please report it to us as described below.

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to [INSERT SECURITY EMAIL].

You should receive a response within 48 hours. If for some reason you do not,
please follow up via email to ensure we received your original message.

Please include the following information:

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Preferred Languages

We prefer all communications to be in English.

## Policy

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will send a more detailed response within 72 hours indicating next steps
- We will keep you informed of the progress towards a fix
- We will notify you when the vulnerability is fixed
- We will publicly acknowledge your responsible disclosure (if desired)

## Security Considerations for Samrat

### Code Execution
Samrat programs run in a sandboxed interpreter. However, the `import` system
can access Python standard library modules. Be cautious when running untrusted
Samrat code.

### File I/O
The `file_io` module allows reading and writing files. Ensure proper
permissions are set when running Samrat programs in production environments.

### Input Validation
The `input()` function reads from stdin. Always validate and sanitize input
when using Samrat in networked or multi-user environments.