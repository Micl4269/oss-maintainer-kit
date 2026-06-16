# Contributing

Thanks for helping improve OSS Maintainer Kit.

## Setup

```bash
git clone https://github.com/Micl4269/oss-maintainer-kit.git
cd oss-maintainer-kit
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m oss_maintainer_kit audit --repo .
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
```

The project intentionally uses the Python standard library so new
contributors can run the tests without installing a dependency stack.

If Semgrep is installed, maintainers can also run:

```bash
semgrep scan --config .semgrep.yml --error .
```

## Contribution Scope

Good first contributions:

- Add a new repository-health check.
- Improve the markdown report.
- Add tests for a known edge case.
- Improve examples for GitHub Actions users.
- Improve docs for maintainer workflows.

Avoid large rewrites in a first PR. Open an issue first for changes that alter
the scoring model, CLI contract, or GitHub Action interface.

## Pull Requests

Before opening a PR:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m oss_maintainer_kit audit --repo .
PYTHONPATH=src python -m oss_maintainer_kit security-scan --repo .
```

Keep PRs focused. Include the problem, the change, verification commands, and
any follow-up work.
