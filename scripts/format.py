#!/usr/bin/env python
"""
Format code with Black.
"""
import subprocess
import sys


def main():
    """Run Black to format the codebase."""
    print("Running Black to format codebase...")
    try:
        result = subprocess.run(
            ["black", "src", "tests"], check=True, capture_output=True, text=True
        )
        print(result.stdout)
        print("✅ Formatting complete!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Black: {e}")
        print(e.stdout)
        print(e.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
