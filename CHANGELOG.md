# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.3] - 2025-05-14

### Added
- Auto-revision feature to detect and generate migrations from manual changes to prompts.yaml
- File watching capability to detect changes in real-time
- New CLI command `auto-revision` with `--dry-run` and `--description` options
- Environment variables `PROMPTMIGRATE_AUTO_REVISION` and `PROMPTMIGRATE_AUTO_REVISION_WATCH` for configuration
- Python API via `enable_auto_revision()` function
- Comprehensive documentation for the auto-revision feature

## [0.3.0] - 2025-05-13

### Added
- Dynamic value placeholders for runtime variable substitution
  - Date placeholders with custom formatting
  - Random number generation with min/max values
  - Random choice selection from provided options
  - Text templates with variable substitution
- Added `list` command to CLI to show available migrations
- Added CI/CD pipeline via GitHub Actions for automated testing and release

### Changed
- Updated documentation for production use
- Removed development artifacts and debug files
- Improved examples with latest API patterns

## [0.2.0] - 2025-05-01

### Added
- Case-insensitive prompt lookup
- CLI command to show current migration state
- Support for Python 3.11 and 3.12

### Changed
- Improved error handling for missing migrations
- Enhanced documentation with more examples

## [0.1.0] - 2025-04-15

### Added
- Initial release
- Core migration functionality
- Command-line interface
- Basic prompt management with YAML storage
- Support for Python 3.9 and 3.10
