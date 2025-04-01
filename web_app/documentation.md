# NIST Randomness Testing Tool (RTT) Web Application Documentation

## Overview
```python
"""
NIST Randomness Testing Tool (RTT) Web Application

This Flask web application provides a user interface for the NIST Statistical Test Suite (STS),
allowing users to perform various statistical tests on binary random number sequences.
The application supports file uploads, test execution, and result analysis with proper
statistical validation.

Key Features:
- Secure session management using Redis
- File upload and processing capabilities
- Statistical test execution and analysis
- Result visualization and download
- Entropy calculation
- Comprehensive statistical validation

Dependencies:
- Flask: Web framework
- Redis: Session management
- NumPy, Pandas, SciPy: Statistical analysis
- Werkzeug: Security utilities
"""
```

## Module Functions

### allowed_file(filename)
```python
"""
Check if the uploaded file has an allowed extension.

Args:
    filename (str): Name of the file to check
    
Returns:
    bool: True if the file extension is allowed, False otherwise
"""
```

### setup_session()
```python
"""
Initialize a new user session and create necessary directory structure.

Returns:
    JSON: Response containing session ID and status message
"""
```

### upload_file()
```python
"""
Handle file uploads for random number sequences.

Returns:
    JSON: Response containing upload status and filename
"""
```

### use_sample_file()
```python
"""
Set up the application to use the sample binary random numbers file.

Returns:
    JSON: Response containing the sample file information
"""
```

### test_process()
```python
"""
Process and execute statistical tests on the uploaded random number sequence.

Returns:
    JSON: Response containing test results and statistical measures
"""
```

### run_assess(params)
```python
"""
Execute the NIST STS assess command with specified parameters.

Args:
    params (dict): Dictionary containing test parameters
    
Returns:
    str: Command output or error message
"""
```

### fit_test(data_column: pd.Series)
```python
"""
Apply goodness-of-fit tests to the test results.

Args:
    data_column (pd.Series): Series containing test results
    
Returns:
    tuple: Statistical measures including chi-square, KS test, pass count,
           data size, proportion, pass rate, and overall result
"""
```

### process_results(test_name)
```python
"""
Process and analyze the results file from the NIST STS assessment.

Args:
    test_name (str): Name of the statistical test
    
Returns:
    tuple: Processed results including statistical measures and test outcome
"""
```

### create_tar_file(tar_file, test_list)
```python
"""
Create a compressed TAR file containing detailed test results.

Args:
    tar_file (str): Path to the output TAR file
    test_list (list): List of test indices to include
    
Returns:
    bool: True if successful, False otherwise
"""
```

### download_results()
```python
"""
Endpoint for downloading detailed test results as a compressed file.

Returns:
    File: Compressed TAR file containing test results
"""
```

### run_ent()
```python
"""
Calculate entropy of the uploaded binary file using the 'ent' utility.

Returns:
    JSON: Response containing entropy calculation results
"""
```

## API Endpoints

1. `/api/setup` (POST)
   - Initializes a new user session
   - Creates necessary directory structure
   - Returns session ID and status

2. `/api/upload` (POST, GET)
   - Handles file uploads for random number sequences
   - Validates file types and saves securely
   - Returns upload status and filename

3. `/api/sample` (POST)
   - Sets up sample binary random numbers file
   - Returns sample file information

4. `/api/test` (POST, GET)
   - Processes and executes statistical tests
   - Returns test results and measures

5. `/api/download_results` (POST)
   - Creates and serves compressed results file
   - Returns TAR file with detailed results

6. `/api/ent` (POST)
   - Calculates entropy of binary file
   - Returns entropy calculation results

## Configuration

The application uses Flask configuration with the following security settings:
```python
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'rtt:'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_PATH'] = '/'
```

## Statistical Tests Available

The application supports 15 NIST statistical tests:
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

## Security Considerations

1. Session Security:
   - Redis-based session management
   - Signed sessions
   - HTTPS preferred
   - Secure cookie settings
   - 30-minute session lifetime

2. File Security:
   - Restricted file extensions
   - Secure filename handling
   - Temporary file storage
   - Protected file operations

3. Important Note:
   - The SECRET_KEY is currently hardcoded and should be moved to environment variables
     or secure configuration management in production.

