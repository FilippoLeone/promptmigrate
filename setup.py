from setuptools import setup, find_packages

# This setup.py is primarily for development installations
# The package metadata is defined in pyproject.toml
setup(
    name="promptmigrate",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
