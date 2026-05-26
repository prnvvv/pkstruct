# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a Vulnerability

Please report vulnerabilities to **security@pkstruct.dev** (do not open public GitHub issues).

You will receive a response within 48 hours. If confirmed, a patch release will be issued within 7 days.

## Security Design

- No use of `eval` or `exec` anywhere in the codebase.
- JSON deserialization uses `json.loads` with strict type checking — no `pickle`.
- Thread safety provided by `threading.RLock` on mutable state.
- Input validation guards against type confusion, infinite loops (cycle detection), and resource exhaustion.
