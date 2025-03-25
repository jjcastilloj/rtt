Installation Guide
================

This guide provides detailed instructions for installing and setting up the NIST SP 800-22 Randomness Test Tool.

Prerequisites
------------

Before installing the application, ensure you have the following prerequisites:

* Python 3.8 or higher
* Redis server
* Nginx web server (recommended)
* NIST SP 800-22 test suite implementation

System Requirements
-----------------

* Linux/Unix operating system
* At least 2GB of RAM
* Sufficient disk space for storing test files and results
* Internet connection for downloading dependencies

Installation Steps
----------------

1. Clone the Repository
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   git clone <repository-url>
   cd rtt

2. Install Python Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -r requirements.txt

3. Configure Redis
~~~~~~~~~~~~~~~~

Install Redis if not already installed:

.. code-block:: bash

   sudo apt-get install redis-server

Start Redis service:

.. code-block:: bash

   sudo systemctl start redis-server
   sudo systemctl enable redis-server

4. Configure Nginx
~~~~~~~~~~~~~~~~

Install Nginx:

.. code-block:: bash

   sudo apt-get install nginx

Create Nginx configuration file:

.. code-block:: nginx

   server {
       listen 443 ssl;
       server_name your_domain.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       location /static {
           alias /path/to/web_app/static;
       }
   }

5. Set Up Application Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create necessary directories:

.. code-block:: bash

   sudo mkdir -p /tmp/rtt
   sudo chown -R $USER:$USER /tmp/rtt

6. Configure Application
~~~~~~~~~~~~~~~~~~~~~~

Set up environment variables:

.. code-block:: bash

   export FLASK_APP=web_app/app.py
   export FLASK_ENV=production
   export SECRET_KEY=your_secret_key

7. Start the Application
~~~~~~~~~~~~~~~~~~~~~~

Using Gunicorn:

.. code-block:: bash

   gunicorn -w 4 -b 127.0.0.1:8000 web_app.app:app

Verification
-----------

To verify the installation:

1. Access the web interface at https://your_domain.com
2. Try uploading a sample binary file
3. Run a basic test
4. Check if results are generated correctly

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~

1. Redis Connection Error
   - Ensure Redis is running: ``sudo systemctl status redis-server``
   - Check Redis configuration: ``redis-cli ping``

2. Permission Issues
   - Verify directory permissions: ``ls -la /tmp/rtt``
   - Check file ownership: ``sudo chown -R $USER:$USER /tmp/rtt``

3. Nginx Configuration
   - Test Nginx configuration: ``sudo nginx -t``
   - Check Nginx logs: ``sudo tail -f /var/log/nginx/error.log``

4. Application Logs
   - Check application logs for errors
   - Verify environment variables are set correctly

Getting Help
~~~~~~~~~~

If you encounter issues:

1. Check the application logs
2. Review the Nginx error logs
3. Verify Redis connection
4. Ensure all dependencies are installed correctly
5. Check file permissions and ownership 