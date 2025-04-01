# Setup Guide

## System Requirements
- Linux-based operating system
- Python 3.x
- Redis server
- Sufficient storage for temporary files

## Dependencies Installation
```bash
# System packages
sudo apt update
sudo apt install python3-pip redis-server

# Python packages
pip3 install flask redis numpy pandas scipy werkzeug
```

## Configuration

### Redis Configuration
1. Ensure Redis server is running:
```bash
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Application Configuration
1. Session settings:
```python
SESSION_TYPE = 'redis'
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = 30 minutes
```

2. Security settings:
```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
PREFERRED_URL_SCHEME = 'https'
```

### File Permissions
1. Ensure proper permissions for 'assess':
```bash
chmod 755 assess
```

2. Create and set permissions for temporary directory:
```bash
mkdir -p /tmp/rtt
chmod 755 /tmp/rtt
```
