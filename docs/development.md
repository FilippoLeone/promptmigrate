# Code Formatting

This project uses [Black](https://black.readthedocs.io/) for code formatting to maintain a consistent code style across the codebase.

## Running Formatter Locally

You can run the formatter locally before pushing your changes to avoid CI failures:

### Using pre-commit (recommended)

We've configured pre-commit hooks that will automatically format your code when you commit:

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install the git hooks
pre-commit install

# Now Black will run automatically when you commit
```

### Manual formatting

If you prefer to run the formatter manually:

```bash
# Using the provided script
python scripts/format.py

# Or directly with Black
black src tests
```

### Windows users

Windows users can run the PowerShell script:

```powershell
.\scripts\format.ps1
```

## CI Pipeline

Our CI pipeline includes a check that ensures all code is formatted according to Black's standards. If your build fails with messages like:

```
would reformat /path/to/file.py
...
Error: Process completed with exit code 1.
```

Simply run the formatter locally and commit the changes before pushing again.
