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

> **Note:** The installation and deployment instructions in this section are written for
> **Linux** (tested on Ubuntu). On Windows the procedure is different: for example,
> `systemd`, Nginx site paths such as `/etc/nginx/` and `/opt`, and the `export`/`sudo`
> commands do not apply. The production deployment section (systemd + Nginx) is Linux-only.

### Prerequisites
- Linux (tested on Ubuntu 24.04 LTS)
- Python 3.x (tested with Python 3.12)
- Redis server
- Modern web browser
- NIST STS binary
- For the production deployment only (see below):
  - systemd (tested with version 255)
  - Nginx (tested with version 1.24)
  - Certbot with its Nginx plugin, to obtain the Let's Encrypt HTTPS certificates
    (a domain name pointing to the server and open ports 80/443 are required)

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

### Production Deployment (systemd + Nginx)

The `configs/` directory contains the files used to run the application as a service
with Gunicorn behind Nginx. The commands below assume you are in the root of the cloned
repository (the directory that contains `configs/` and `web_app/`).

| File in repo | Destination |
|---|---|
| `configs/gunicorn/rtt.service` | `/etc/systemd/system/rtt.service` |
| `configs/nginx/nist-tests` | `/etc/nginx/sites-available/nist-tests` (enabled via a symlink in `/etc/nginx/sites-enabled/`) |

1. Make the application available at the path used by the service and Nginx
   (`/opt/web_app`):
   ```bash
   sudo ln -s "$PWD/web_app" /opt/web_app
   ```

2. Review the paths and the user in `configs/gunicorn/rtt.service` before installing it.
   `User`, `Group` and the `ExecStart` path to the virtual environment's `gunicorn`
   (`/home/jcastillo/nist/env-nist-tests/bin/gunicorn`) must match your machine.
   Also change `server_name` and the certificate paths in `configs/nginx/nist-tests`
   to your own domain.

3. Install and start the Gunicorn service:
   ```bash
   sudo cp configs/gunicorn/rtt.service /etc/systemd/system/rtt.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now rtt.service
   systemctl status rtt.service
   ```

4. Obtain the HTTPS certificates (Let's Encrypt).

   `configs/nginx/nist-tests` references certificates under
   `/etc/letsencrypt/live/<your-domain>/` and two helper files
   (`options-ssl-nginx.conf` and `ssl-dhparams.pem`) that Certbot's Nginx plugin creates.
   Nginx will not start with this site until they exist, so first serve a temporary
   HTTP-only site and let Certbot generate everything.

   Requirements: `<your-domain>` must resolve to the public IP of this server and ports
   80 and 443 must be reachable from the Internet (Let's Encrypt validates the domain
   through port 80).

   ```bash
   # Install Certbot and its Nginx plugin
   sudo apt install certbot python3-certbot-nginx

   # Temporary HTTP-only site (replace <your-domain>)
   sudo tee /etc/nginx/sites-available/nist-tests > /dev/null <<'EOF'
   server {
       listen 80;
       server_name <your-domain>;
       root /var/www/html;
   }
   EOF
   sudo ln -sf /etc/nginx/sites-available/nist-tests /etc/nginx/sites-enabled/nist-tests
   sudo nginx -t && sudo systemctl reload nginx

   # Request the certificate (Certbot edits the temporary site to add SSL)
   sudo certbot --nginx -d <your-domain>
   ```

   After this step `/etc/letsencrypt/live/<your-domain>/` exists. The next step replaces
   the temporary site with the real one.

5. Install the final Nginx site and reload Nginx (make sure `server_name` and the
   certificate paths in `configs/nginx/nist-tests` already use `<your-domain>`, see step 2):
   ```bash
   sudo cp configs/nginx/nist-tests /etc/nginx/sites-available/nist-tests
   sudo ln -sf /etc/nginx/sites-available/nist-tests /etc/nginx/sites-enabled/nist-tests
   sudo nginx -t && sudo systemctl reload nginx
   ```

6. Check that the automatic certificate renewal works. Certbot installs a systemd timer
   for this:
   ```bash
   systemctl status certbot.timer
   sudo certbot renew --dry-run
   ```

7. Useful commands after changing a file:
   ```bash
   sudo systemctl daemon-reload && sudo systemctl restart rtt.service   # after editing rtt.service
   sudo nginx -t && sudo systemctl reload nginx                          # after editing the Nginx site
   journalctl -u rtt.service -f                                          # follow the service logs
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