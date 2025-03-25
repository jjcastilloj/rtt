Usage Guide
==========

This guide explains how to use the NIST SP 800-22 Randomness Test Tool effectively.

Getting Started
--------------

1. Access the Web Interface
~~~~~~~~~~~~~~~~~~~~~~~~~

Open your web browser and navigate to the application URL:
``https://your_domain.com``

2. Initial Setup
~~~~~~~~~~~~~~

The first time you access the application:

* A new session will be automatically created
* The necessary directory structure will be set up
* You'll be ready to upload files or use the sample file

File Management
--------------

Uploading Files
~~~~~~~~~~~~~

1. Click the "Upload File" button
2. Select your binary file
3. Wait for the upload to complete
4. Verify the file appears in the list

Using Sample File
~~~~~~~~~~~~~~~

1. Click "Use Sample File"
2. The built-in pi.bin file will be loaded
3. You can proceed with testing

Running Tests
------------

Selecting Tests
~~~~~~~~~~~~

1. Choose the test(s) you want to run from the list
2. Configure test parameters as needed
3. Click "Run Tests"

Test Parameters
~~~~~~~~~~~~

Common parameters for different tests:

* Block Frequency Test
  * Block Size
  * Number of Streams

* Non-overlapping Template Test
  * Template Length
  * Number of Streams

* Overlapping Template Test
  * Template Length
  * Number of Streams

* Approximate Entropy Test
  * Block Length
  * Number of Streams

* Serial Test
  * Block Length
  * Number of Streams

* Linear Complexity Test
  * Block Length
  * Number of Streams

Viewing Results
-------------

Test Results Display
~~~~~~~~~~~~~~~~~

Results are displayed in a table format showing:

* Test Name
* Chi-square Value
* Kolmogorov-Smirnov Value
* Number of Approved Sequences
* Total Number of Sequences
* Proportion
* Pass Rate
* Overall Result (PASS/FAIL)

Detailed Results
~~~~~~~~~~~~~~

For detailed results:

1. Select the tests you want to analyze
2. Click "Download Results"
3. A compressed file containing detailed results will be downloaded

Entropy Analysis
--------------

To analyze the entropy of your binary file:

1. Upload your file or use the sample file
2. Click "Run Entropy Analysis"
3. View the entropy statistics including:

   * Entropy
   * Chi-square Distribution
   * Arithmetic Mean
   * Monte Carlo Value for Pi
   * Serial Correlation Coefficient

Best Practices
-------------

File Preparation
~~~~~~~~~~~~~

1. Ensure your binary file is properly formatted
2. Use appropriate file sizes (recommended: 1MB or larger)
3. Verify file integrity before uploading

Test Selection
~~~~~~~~~~~~

1. Start with basic tests (Frequency, Runs)
2. Progress to more complex tests
3. Consider your specific use case when selecting tests

Result Interpretation
~~~~~~~~~~~~~~~~~~

1. Consider multiple test results together
2. Pay attention to proportions and pass rates
3. Look for patterns in failed tests
4. Use entropy analysis as a complementary tool

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~

1. File Upload Failures
   * Check file size limits
   * Verify file format
   * Ensure proper permissions

2. Test Execution Errors
   * Verify test parameters
   * Check file integrity
   * Review error messages

3. Result Interpretation
   * Consider test dependencies
   * Review test documentation
   * Consult NIST guidelines

Getting Help
~~~~~~~~~~

If you encounter issues:

1. Check the application logs
2. Review the test documentation
3. Consult the NIST SP 800-22 specification
4. Contact system administrator 