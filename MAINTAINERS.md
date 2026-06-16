# Maintainer Guide

This document is for maintainers and release managers of pkstruct.

## Project Leadership

- **Founder & Maintainer**: [Prannavakhanth](https://github.com/prnvvv) — prannavakhanth12@gmail.com
- **Co-Founder & Maintainer**: [Priyanka Kaliraj](https://github.com/pri-23-k) — pri2303k@gmail.com

## Publishing a Release

```bash
# 1. Clean any previous builds
rm -rf dist/

# 2. Build distribution packages
python -m build

# 3. Verify distribution
twine check dist/*

# 4. Upload to PyPI
twine upload dist/*

# 5. Tag the release
git tag v$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
git push origin --tags
```

## Before a Release

- [ ] All tests pass: `python -m pytest`
- [ ] Type check passes: `mypy src/pkstruct`
- [ ] Lint passes: `ruff check src/pkstruct`
- [ ] CHANGELOG.md is up to date
- [ ] Version is bumped in `pyproject.toml`
- [ ] README example code is verified against release

## Versioning

pkstruct follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **Patch** (`0.1.0` → `0.1.1`): Bug fixes, minor improvements, no breaking API changes.
- **Minor** (`0.1.0` → `0.2.0`): New features, deprecations, no breaking API changes (once stable).
- **Major** (`1.0.0`): Breaking API changes.

## Managing Issues

- Apply appropriate labels: `bug`, `enhancement`, `question`, `good first issue`.
- Respond to new issues within 48 hours.
- Close resolved issues with a comment linking to the PR.

## Managing Pull Requests

- Review within 5 business days.
- Ensure all CI checks pass before merging.
- Use **Squash and Merge** for feature branches.
- Update CHANGELOG.md when merging user-facing changes.

## Security Vulnerabilities

See [SECURITY.md](SECURITY.md) for the reporting process.
