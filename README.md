# NIST Randomness Testing Tool (RTT)

## Overview
The NIST Randomness Testing Tool (RTT) is a web-based application that provides a user interface for the NIST Statistical Test Suite (STS). This tool allows users to perform various statistical tests on binary random number sequences, analyze their results, and generate comprehensive reports.

## Features
- **File Management**
  - Upload custom binary random number sequences
  - Use built-in sample files for testing
  - Support for various file formats (bin, txt, etc.)

- **Statistical Testing**
  - 15 different NIST statistical tests
  - Configurable test parameters
  - Real-time test execution
  - Comprehensive result analysis

- **Result Analysis**
  - Visual representation of test results
  - Statistical validation (chi-square, KS test)
  - Entropy calculation
  - Detailed result export (CSV, TAR)

- **Security**
  - Secure session management
  - File validation
  - HTTPS support
  - Protected endpoints

## Technical Architecture

### Backend (Python/Flask)
- **Framework**: Flask
- **Session Management**: Redis
- **Statistical Analysis**: NumPy, Pandas, SciPy
- **File Processing**: Built-in Python libraries

### Frontend (JavaScript)
- **Core Functionality**: Vanilla JavaScript
- **UI Components**: Custom implementation
- **Data Visualization**: Dynamic table updates
- **File Handling**: Native browser APIs

## Installation

### Prerequisites
- Python 3.x
- Redis server
- Modern web browser
- NIST STS binary

### Setup Steps
1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd rtt
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Redis:
   ```bash
   # Start Redis server
   redis-server
   ```

4. Set up environment variables:
   ```bash
   export FLASK_APP=web_app/app.py
   export FLASK_ENV=development
   ```

5. Run the application:
   ```bash
   flask run
   ```

## Usage

### Starting a Test Session
1. Access the web interface at `http://localhost:8000`
2. Click "Setup Environment" to initialize the session
3. Choose between uploading a custom file or using the sample file

### Running Tests
1. Select desired statistical tests
2. Configure test parameters:
   - Sequence size
   - Number of sequences
   - Block sizes (if applicable)
3. Click "Start Test" to begin analysis

### Viewing Results
- Results are displayed in real-time in the results table
- Each test shows:
  - Chi-square value
  - KS test value
  - Number of sequences
  - Pass/fail status
  - Proportion of passed tests
  - Pass rate

### Exporting Results
- Download results as CSV
- Export detailed results as TAR archive
- View entropy analysis

## API Documentation

### Endpoints

#### Session Management
- `POST /api/setup`
  - Initializes a new testing session
  - Creates necessary directory structure
  - Returns session ID and status

#### File Operations
- `POST /api/upload`
  - Handles file uploads
  - Validates file type and content
  - Returns upload status

- `POST /api/sample`
  - Sets up sample file usage
  - Returns sample file information

#### Testing
- `POST /api/test`
  - Executes statistical tests
  - Parameters:
    - test: Test number (1-15)
    - secSize: Sequence size
    - secNum: Number of sequences
    - blockFreq: Block frequency parameter
    - blockNon: Non-overlapping template parameter
    - blockOver: Overlapping template parameter
    - blockApprox: Approximate entropy parameter
    - blockSerial: Serial test parameter
    - blockLinear: Linear complexity parameter

#### Results
- `POST /api/download_results`
  - Downloads detailed test results
  - Returns TAR archive

- `POST /api/ent`
  - Calculates entropy
  - Returns entropy analysis results

## Statistical Tests

The tool implements the following NIST statistical tests:

1. Frequency (Monobit) Test
2. Block Frequency Test
3. Cumulative Sums Test
4. Runs Test
5. Longest Run of Ones Test
6. Rank Test
7. Discrete Fourier Transform Test
8. Non-overlapping Template Matching Test
9. Overlapping Template Matching Test
10. Universal Statistical Test
11. Approximate Entropy Test
12. Random Excursions Test
13. Random Excursions Variant Test
14. Serial Test
15. Linear Complexity Test

## Security Considerations

- All sessions are managed through Redis
- File uploads are validated and sanitized
- HTTPS is enforced for all communications
- Session cookies are secure and HTTP-only
- Input validation is performed on all parameters

## Error Handling

The application implements comprehensive error handling for:
- File upload failures
- Invalid test parameters
- Insufficient data
- Server communication errors
- Session management issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify License]

## Acknowledgments

- NIST Statistical Test Suite
- Flask web framework
- Redis for session management
- All contributors and maintainers

## Support

For support, please:
1. Check the documentation
2. Review existing issues
3. Create a new issue if needed

## Version History

- v1.0.0: Initial release
  - Basic test functionality
  - File upload support
  - Result visualization

[Add more versions as they are released] 