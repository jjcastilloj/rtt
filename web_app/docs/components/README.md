# Components Documentation

## Core Components

### 1. Web Application (app.py)
The main Flask application that provides the web interface and API endpoints.

#### Key Features:
- Session management with Redis
- File upload handling
- Statistical test execution
- Result processing and analysis

#### Dependencies:
- Flask
- Redis
- NumPy/Pandas/SciPy
- Werkzeug

### 2. NIST STS Executable (assess)
The core statistical testing component.

#### Characteristics:
- 64-bit ELF executable
- Implements NIST statistical tests
- Command-line interface
- Dynamic linking

#### Supported Tests:
1. Frequency
2. BlockFrequency
3. CumulativeSums
4. Runs
5. LongestRun
6. Rank
7. FFT
8. NonOverlappingTemplate
9. OverlappingTemplate
10. Universal
11. ApproximateEntropy
12. RandomExcursions
13. RandomExcursionsVariant
14. Serial
15. LinearComplexity
