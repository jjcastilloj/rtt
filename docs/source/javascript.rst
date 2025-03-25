JavaScript Frontend Documentation
==============================

This section provides detailed documentation for the JavaScript frontend of the NIST SP 800-22 Randomness Test Tool.

Global Variables
--------------

.. js:attribute:: selectedFileName
   :type: string
   :value: "Select file"
   Stores the name of the currently selected file.

.. js:attribute:: selectedFileSize
   :type: number
   :value: 0
   Stores the size of the currently selected file in bytes.

.. js:attribute:: fileUploaded
   :type: boolean
   :value: false
   Indicates whether a file has been successfully uploaded.

.. js:attribute:: checkbox_checked
   :type: boolean
   :value: true
   Tracks the state of test selection checkboxes.

.. js:attribute:: logDiv
   :type: HTMLElement
   Reference to the log display element.

.. js:attribute:: logMessages
   :type: Array
   Array storing log messages.

.. js:attribute:: testData
   :type: Object
   Object storing test results data.

UI Management Functions
---------------------

.. js:function:: enableGroupInputs(groupName)
   Enables all input elements within a specified group.
   
   :param string groupName: The data-group attribute value to match
   :return: void

.. js:function:: disableGroupInputs(groupName)
   Disables all input elements within a specified group.
   
   :param string groupName: The data-group attribute value to match
   :return: void

.. js:function:: defaultBlockSizes()
   Toggles between default and manual block size input modes.
   
   :return: void

.. js:function:: defaultSample()
   Toggles between using the sample file and personal file upload.
   
   :return: void

Input Validation Functions
------------------------

.. js:function:: validateInputs()
   Validates that all required input fields are filled.
   
   :return: boolean - True if all inputs are valid, false otherwise

.. js:function:: restrictInputs()
   Restricts input fields to numeric values only.
   
   :return: void

Utility Functions
---------------

.. js:function:: formatBytes(bytes)
   Formats a number of bytes into a human-readable string.
   
   :param number bytes: The number of bytes to format
   :return: string - Formatted size string (e.g., "1.5 MB")

.. js:function:: addLogMessage(message)
   Adds a timestamped message to the log display.
   
   :param string message: The message to log
   :return: void

.. js:function:: clearLog()
   Clears all messages from the log display.
   
   :return: void

.. js:function:: clearTable()
   Clears all test results from the results table.
   
   :return: void

File Management Functions
-----------------------

.. js:function:: selectFile()
   Triggers the file input element's click event.
   
   :return: void

.. js:function:: handleFileChange()
   Handles the file selection change event.
   
   :return: void

.. js:function:: setupSession()
   Initializes a new user session via API call.
   
   :return: Promise<void>

.. js:function:: uploadFile()
   Uploads the selected file to the server.
   
   :return: void

Test Management Functions
-----------------------

.. js:function:: toggleAllCheckboxes()
   Toggles the selection state of all test checkboxes.
   
   :return: void

.. js:function:: startTest()
   Initiates the selected statistical tests.
   
   :return: Promise<void>

.. js:function:: updateStatus(fil, col)
   Updates the status cell in the results table.
   
   :param number fil: Row index
   :param number col: Column index
   :return: void

.. js:function:: updateTable(fil, col, value)
   Updates a cell in the results table.
   
   :param number fil: Row index
   :param number col: Column index
   :param any value: Value to set
   :return: void

Export Functions
--------------

.. js:function:: downloadTableAsCSV()
   Downloads the results table as a CSV file.
   
   :return: void

.. js:function:: downloadResults()
   Downloads detailed test results as a compressed file.
   
   :return: void

Entropy Analysis Functions
------------------------

.. js:function:: startEnt()
   Initiates entropy analysis of the uploaded file.
   
   :return: void

Initialization Functions
----------------------

.. js:function:: initComponents()
   Initializes UI components and event listeners.
   
   :return: void

Event Listeners
-------------

The following event listeners are set up in the ``initComponents`` function:

* File input change event
* Form submission event
* Block size toggle event
* Sample file toggle event
* Test checkbox toggle events
* Download buttons click events
* Entropy analysis button click event

API Integration
-------------

The frontend interacts with the following API endpoints:

* ``/api/setup`` - Session initialization
* ``/api/upload`` - File upload
* ``/api/sample`` - Sample file loading
* ``/api/test`` - Test execution
* ``/api/download_results`` - Results download
* ``/api/ent`` - Entropy analysis

All API calls include credentials and handle responses appropriately. 