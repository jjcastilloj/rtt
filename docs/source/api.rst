API Reference
============

This section provides detailed documentation for the NIST SP 800-22 Randomness Test Tool API.

.. module:: web_app.app

.. autoclass:: Flask
   :members:
   :undoc-members:
   :show-inheritance:

API Endpoints
------------

Setup Session
~~~~~~~~~~~~

.. autofunction:: setup_session

Upload File
~~~~~~~~~~

.. autofunction:: upload_file

Use Sample File
~~~~~~~~~~~~~~

.. autofunction:: use_sample_file

Process Test
~~~~~~~~~~~

.. autofunction:: test_process

Download Results
~~~~~~~~~~~~~~~

.. autofunction:: download_results

Run Entropy Analysis
~~~~~~~~~~~~~~~~~~

.. autofunction:: run_ent

Helper Functions
--------------

Run Assess
~~~~~~~~~

.. autofunction:: run_assess

Fit Test
~~~~~~~

.. autofunction:: fit_test

Process Results
~~~~~~~~~~~~~

.. autofunction:: process_results

Create Tar File
~~~~~~~~~~~~~

.. autofunction:: create_tar_file

Allowed File
~~~~~~~~~~~

.. autofunction:: allowed_file

Constants
--------

NIST Tests
~~~~~~~~~

.. data:: nist_test

   List of available NIST statistical tests:

   * Frequency
   * BlockFrequency
   * CumulativeSums
   * Runs
   * LongestRun
   * Rank
   * FFT
   * NonOverlappingTemplate
   * OverlappingTemplate
   * Universal
   * ApproximateEntropy
   * RandomExcursions
   * RandomExcursionsVariant
   * Serial
   * LinearComplexity 