Configuration Guide
=================

This guide explains how to configure the NIST SP 800-22 Randomness Test Tool.

Application Configuration
-----------------------

Session Management
~~~~~~~~~~~~~~~

The application uses Redis for session management. Configure the following settings in ``app.py``:

.. code-block:: python

   app.config['SESSION_TYPE'] = 'redis'
   app.config['SECRET_KEY'] = 'your_secret_key'
   app.config['SESSION_USE_SIGNER'] = True
   app.config['SESSION_KEY_PREFIX'] = 'rtt:'
   app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
   app.config['SESSION_PERMANENT'] = False
   app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

Cookie Settings
~~~~~~~~~~~~

Configure cookie security settings:

.. code-block:: python

   app.config['PREFERRED_URL_SCHEME'] = 'https'
   app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
   app.config['SESSION_COOKIE_SECURE'] = True
   app.config['SESSION_COOKIE_HTTPONLY'] = True
   app.config['SESSION_COOKIE_PATH'] = '/'

File Management
~~~~~~~~~~~~

Configure file storage settings:

.. code-block:: python

   APP_ROOT = os.path.dirname(os.path.abspath(__file__))
   USER_FILES_DIR = '/tmp/rtt'
   ALLOWED_EXTENSIONS = {'tar', 'png', 'jpg', 'jpeg', 'gif', 'bin', 'txt'}

Nginx Configuration
----------------

Basic Configuration
~~~~~~~~~~~~~~~

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

SSL Configuration
~~~~~~~~~~~~~~

For secure HTTPS connections:

1. Obtain SSL certificates
2. Configure SSL parameters:

.. code-block:: nginx

   ssl_protocols TLSv1.2 TLSv1.3;
   ssl_ciphers HIGH:!aNULL:!MD5;
   ssl_prefer_server_ciphers on;
   ssl_session_cache shared:SSL:10m;
   ssl_session_timeout 10m;

Security Settings
--------------

File Permissions
~~~~~~~~~~~~~

Set appropriate file permissions:

.. code-block:: bash

   sudo chown -R $USER:$USER /tmp/rtt
   chmod 755 /tmp/rtt
   chmod 644 /tmp/rtt/*

Redis Configuration
----------------

Basic Settings
~~~~~~~~~~~

Configure Redis in ``/etc/redis/redis.conf``:

.. code-block:: conf

   bind 127.0.0.1
   port 6379
   requirepass your_redis_password
   maxmemory 2gb
   maxmemory-policy allkeys-lru

Security Settings
~~~~~~~~~~~~~

1. Enable password protection
2. Restrict network access
3. Configure memory limits
4. Set up persistence

Environment Variables
------------------

Required Variables
~~~~~~~~~~~~~~~

.. code-block:: bash

   export FLASK_APP=web_app/app.py
   export FLASK_ENV=production
   export SECRET_KEY=your_secret_key
   export REDIS_URL=redis://localhost:6379/0

Optional Variables
~~~~~~~~~~~~~~~

.. code-block:: bash

   export MAX_CONTENT_LENGTH=16777216  # 16MB
   export UPLOAD_FOLDER=/tmp/rtt
   export ALLOWED_EXTENSIONS=bin,txt,tar

Test Configuration
---------------

Default Parameters
~~~~~~~~~~~~~~

Configure default test parameters in the application:

.. code-block:: python

   DEFAULT_TEST_PARAMS = {
       'blockFreq': 128,
       'blockNon': 9,
       'blockOver': 9,
       'blockApprox': 10,
       'blockSerial': 16,
       'blockLinear': 500,
       'secNum': 100,
       'secSize': 1000000
   }

Test Selection
~~~~~~~~~~~

Configure available tests:

.. code-block:: python

   nist_test = [
       "Frequency",
       "BlockFrequency",
       "CumulativeSums",
       "Runs",
       "LongestRun",
       "Rank",
       "FFT",
       "NonOverlappingTemplate",
       "OverlappingTemplate",
       "Universal",
       "ApproximateEntropy",
       "RandomExcursions",
       "RandomExcursionsVariant",
       "Serial",
       "LinearComplexity"
   ]

Logging Configuration
------------------

Application Logs
~~~~~~~~~~~~

Configure logging in ``app.py``:

.. code-block:: python

   import logging

   logging.basicConfig(
       filename='app.log',
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

Nginx Logs
~~~~~~~~

Configure Nginx logging in ``/etc/nginx/nginx.conf``:

.. code-block:: nginx

   access_log /var/log/nginx/access.log combined buffer=512k flush=1m;
   error_log /var/log/nginx/error.log warn;

Performance Tuning
---------------

Gunicorn Settings
~~~~~~~~~~~~~

Configure Gunicorn for optimal performance:

.. code-block:: bash

   gunicorn -w 4 -b 127.0.0.1:8000 \
       --timeout 120 \
       --keep-alive 5 \
       --log-level info \
       --access-logfile /var/log/gunicorn/access.log \
       --error-logfile /var/log/gunicorn/error.log \
       web_app.app:app

Redis Optimization
~~~~~~~~~~~~~~

Configure Redis for better performance:

.. code-block:: conf

   maxmemory 2gb
   maxmemory-policy allkeys-lru
   appendonly yes
   appendfsync everysec
   no-appendfsync-on-rewrite yes
   auto-aof-rewrite-percentage 100
   auto-aof-rewrite-min-size 64mb

Monitoring
---------

System Monitoring
~~~~~~~~~~~~

Set up monitoring tools:

1. System metrics (CPU, memory, disk)
2. Application metrics (requests, response times)
3. Redis metrics (memory usage, connections)
4. Nginx metrics (requests, errors)

Log Monitoring
~~~~~~~~~~~

Configure log monitoring:

1. Application logs
2. Nginx access logs
3. Nginx error logs
4. Redis logs
5. System logs

Backup Configuration
-----------------

File Backups
~~~~~~~~~

Configure backup strategy:

1. Regular backups of:
   * Application files
   * Configuration files
   * User data
   * Test results

2. Backup schedule:
   * Daily incremental backups
   * Weekly full backups
   * Monthly archives

Database Backups
~~~~~~~~~~~~

For Redis data:

1. Enable AOF persistence
2. Configure RDB snapshots
3. Set up backup schedule
4. Test backup restoration 