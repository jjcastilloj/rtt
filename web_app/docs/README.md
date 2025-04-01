# NIST Randomness Testing Tool (RTT) Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Documentation Sections](#documentation-sections)

## Introduction
Welcome to the NIST Randomness Testing Tool (RTT) documentation. This tool provides a web interface for the NIST Statistical Test Suite (STS), enabling users to perform statistical testing on binary random number sequences.

## Project Structure
```
/opt/web_app/
├── app.py              # Main Flask application
├── assess             # NIST STS executable
├── wsgi.py            # WSGI entry point
└── docs/              # Documentation directory
    ├── api/           # API documentation
    ├── components/    # Component documentation
    ├── setup/        # Setup and installation guides
    └── tests/        # Testing documentation
```

## Documentation Sections

### [API Documentation](api/README.md)
- Detailed API endpoint documentation
- Request/response formats
- Authentication and security

### [Components](components/README.md)
- Core components documentation
- Architecture overview
- Data flow diagrams

### [Setup Guide](setup/README.md)
- Installation instructions
- Configuration guide
- Dependencies management

### [Testing](tests/README.md)
- Test suite documentation
- Testing procedures
- Statistical test descriptions
