# Contributing

We welcome contributions to the OpenTelemetry Gunicorn Instrumentation project!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Agent-Hellboy/opentelemetry-instrumentation-gunicorn.git
cd opentelemetry-instrumentation-gunicorn

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .[test,docs]

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
# Run unit tests
tox -e py

# Run e2e tests (requires Docker)
tox -e e2e

# Or run tests directly with pytest
pytest
pytest tests/test_e2e_metrics.py
```

## Development Workflow

1. **Choose an Issue** - Check [GitHub Issues](https://github.com/Agent-Hellboy/opentelemetry-instrumentation-gunicorn/issues)

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes** - Write tests, follow existing code style

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create Pull Request on GitHub
   ```

## Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Run `tox -e lint` before committing

## Getting Help

- [GitHub Issues](https://github.com/Agent-Hellboy/opentelemetry-instrumentation-gunicorn/issues) for bugs and features
- [OpenTelemetry Python Docs](https://opentelemetry-python.readthedocs.io/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

Thank you for contributing! 🚀
