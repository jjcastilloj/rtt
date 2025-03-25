Welcome to NIST SP 800-22 Randomness Test Tool's documentation!
=============================================================

The NIST SP 800-22 Randomness Test Tool is a web application designed to run statistical tests
on binary sequences according to the NIST SP 800-22 specification. This tool provides a RESTful
API interface for uploading binary files, running various statistical tests, and analyzing the results.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   javascript
   installation
   usage
   configuration

Features
--------

* RESTful API interface
* Support for all NIST SP 800-22 statistical tests
* File upload and management
* Session-based user management
* Detailed test results and analysis
* Entropy analysis
* Results export functionality

Installation
-----------

To install the NIST SP 800-22 Randomness Test Tool:

1. Clone the repository
2. Install the required dependencies:
   .. code-block:: bash
      pip install -r requirements.txt
3. Configure Redis for session management
4. Set up the web server (Nginx recommended)

For detailed installation instructions, see :doc:`installation`.

Usage
-----

The application provides a web interface and API endpoints for:

* File upload and management
* Test selection and configuration
* Results analysis and visualization
* Export of detailed test results

For detailed usage instructions, see :doc:`usage`.

API Reference
------------

The application exposes the following API endpoints:

* ``/api/setup`` - Initialize a new user session
* ``/api/upload`` - Upload binary files for testing
* ``/api/sample`` - Use the built-in sample file
* ``/api/test`` - Run statistical tests
* ``/api/download_results`` - Download test results
* ``/api/ent`` - Run entropy analysis

For detailed API documentation, see :doc:`api`.

JavaScript Frontend
-----------------

The frontend is built with vanilla JavaScript and provides:

* Interactive file upload interface
* Dynamic test selection and configuration
* Real-time results display
* Export functionality
* Entropy analysis visualization

For detailed frontend documentation, see :doc:`javascript`.

Configuration
------------

The application can be configured through various settings for:

* Session management
* File storage
* Test parameters
* Security settings

For detailed configuration instructions, see :doc:`configuration`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search` 