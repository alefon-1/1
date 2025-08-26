# Repository "1" - Development Instructions

**ALWAYS follow these instructions first and only fallback to additional search and context gathering if the information here is incomplete or found to be in error.**

## Current Repository State

This repository is currently in a minimal state with no buildable code. It contains:
- A basic README.md with minimal content ("# 1")
- A comprehensive .gitignore file configured for Python development
- No source code, build scripts, or project configuration files

## Working Effectively

### Repository Structure
```
.
├── README.md          # Basic project title only ("#1")
├── .gitignore         # Python-focused gitignore (4688 bytes)
└── .github/
    └── copilot-instructions.md  # This file
```

Expected output from `ls -la`:
```
total 28
drwxr-xr-x 4 runner docker 4096 [date] .
drwxr-xr-x 3 runner docker 4096 [date] ..
drwxr-xr-x 7 runner docker 4096 [date] .git
drwxr-xr-x 2 runner docker 4096 [date] .github
-rw-r--r-- 1 runner docker 4688 [date] .gitignore
-rw-r--r-- 1 runner docker    3 [date] README.md
```

### Current Capabilities
- **Cannot build**: No source code or build configuration exists
- **Cannot test**: No test files or test configuration exists  
- **Cannot run**: No executable code exists
- **Cannot lint**: No code to lint and no linting configuration

### Repository Analysis Commands
Run these commands to understand the current state:
```bash
# List all files (excluding .git)
find . -type f -not -path "./.git/*"

# Check repository history
git --no-pager log --oneline -10

# Examine existing files
cat README.md
head -20 .gitignore
```

### Technology Stack Indicators
Based on the .gitignore file, this repository is prepared for Python development with support for:
- Python packages and virtual environments
- Poetry, PDM, Pipenv package managers
- pytest testing framework
- mypy type checking
- Various Python IDEs (PyCharm, VS Code)

### Environment Available
- **Python**: 3.12.3 (located at /usr/bin/python3)
- **pip**: 24.0 available for package installation
- **Not pre-installed**: poetry, pytest, mypy (can be installed via pip when needed)
- Ready for Python development when code is added

## Development Guidance

### When Adding Code
Once code is added to this repository, update these instructions with:

1. **Build Instructions**: Add exact commands to build the project
2. **Test Instructions**: Add commands to run tests with appropriate timeout values
3. **Run Instructions**: Add commands to start/run the application
4. **Validation Scenarios**: Define specific user workflows to test after changes

### Recommended Next Steps
If developing a Python project:
```bash
# Create basic Python project structure
mkdir src
touch src/__init__.py

# Add project configuration (choose one)
# For poetry: poetry init
# For pip: touch requirements.txt
# For modern Python: touch pyproject.toml

# Add basic test structure
mkdir tests
touch tests/__init__.py
touch tests/test_basic.py
```

### Common File Locations
When code is added, look for these important files:
- `src/` or project root: Main source code
- `tests/`: Test files
- `requirements.txt`, `pyproject.toml`, or `Pipfile`: Dependencies
- `Makefile`, `setup.py`, or build scripts: Build configuration
- `.github/workflows/`: CI/CD pipelines

## Validation

### Current Repository Validation
```bash
# Verify repository structure
ls -la

# Check git status
git --no-pager status

# Verify no uncommitted changes
git --no-pager diff
```

### Future Code Validation
When code is added, always:
1. **Build the project** using the established build process
2. **Run all tests** with appropriate timeout values (document expected time)
3. **Execute end-to-end scenarios** to verify functionality
4. **Run linting/formatting** if configured
5. **Check CI/CD compatibility** by running equivalent local commands

## Time Expectations

### Current Operations
- Repository exploration: < 1 minute
- File examination: < 30 seconds per file
- Git operations: < 30 seconds

### Future Operations (when code exists)
- **NEVER CANCEL builds or tests** - document actual timing once established
- Set timeouts generously (60+ minutes for builds, 30+ minutes for tests)
- Always include "NEVER CANCEL" warnings for long-running operations

## Important Notes

- This repository currently has no functional code to build, test, or run
- All development must start from scratch or by adding initial project files
- Update these instructions immediately when adding build processes, tests, or runnable code
- The .gitignore suggests Python development - leverage Python tooling when adding code
- Always validate that new instructions work by testing them completely before documenting

## Critical Reminders

- **NO BUILD PROCESS EXISTS** - any build instructions added later must be thoroughly tested
- **NO TEST FRAMEWORK EXISTS** - test setup will need to be created from scratch
- **VALIDATE EVERYTHING** - when adding code and processes, test every command before documenting it
- **MEASURE TIMING** - document actual time taken for builds/tests and add 50% buffer for timeouts
- **MANUAL TESTING REQUIRED** - always run through complete user scenarios after changes