# Frontend JavaScript Documentation (script.js)

## Overview
The `script.js` file implements the frontend functionality for the NIST Randomness Testing Tool (RTT) web interface. It manages file operations, test configurations, real-time test execution, and result visualization.

## Global State
```javascript
let selectedFileName = "Select file"    // Currently selected file name
let selectedFileSize = 0                // Size of the selected file in bytes
let fileUploaded = false               // Flag indicating if a file has been uploaded
let checkbox_checked = true            // State of test selection checkboxes
let logDiv                             // DOM reference to log display
let logMessages = []                   // Array of log messages
let testData = {}                      // Object storing test results
```

## Core Functions

### Session Management
```javascript
async function setupSession()
```
- Initializes testing environment
- Creates necessary server-side directory structure
- Sets up session cookies and configuration

### File Operations

#### File Selection
```javascript
function selectFile()
function handleFileChange()
```
- Manages file selection dialog
- Updates UI with file information
- Validates file selection

#### File Upload
```javascript
function uploadFile()
```
- Handles file upload to server
- Validates file before upload
- Updates UI based on upload status
- Enables test configuration after successful upload

### Test Configuration

#### Parameter Management
```javascript
function defaultBlockSizes()
function validateInputs()
function restrictInputs()
```
- Manages test parameter configuration
- Validates input fields
- Handles default vs. manual parameter settings

#### Sample Data Management
```javascript
async function defaultSample()
```
- Toggles between sample and custom file modes
- Manages sample file loading
- Updates UI accordingly

### Test Execution

#### Test Control
```javascript
function startTest()
function toggleAllCheckboxes()
```
- Initiates test execution
- Manages test selection
- Validates test parameters
- Handles test execution flow

#### Results Management
```javascript
function updateStatus(fil, col)
function updateTable(fil, col, value)
```
- Updates test progress indicators
- Manages result display in table
- Handles result formatting

### Results Export

#### Download Functions
```javascript
function downloadTableAsCSV()
function downloadResults()
```
- Exports results in CSV format
- Downloads detailed test results
- Creates compressed archive of results

### Entropy Analysis
```javascript
function startEnt()
```
- Calculates entropy of uploaded file
- Displays entropy information
- Manages entropy test execution

### Logging System
```javascript
function addLogMessage(message)
function clearLog()
```
- Manages system log messages
- Timestamps log entries
- Provides user feedback

### UI Management
```javascript
function initComponents()
function clearTable()
function enableGroupInputs(groupName)
function disableGroupInputs(groupName)
```
- Initializes UI components
- Manages component states
- Handles group input enabling/disabling

## Event Handling
```javascript
document.addEventListener('DOMContentLoaded', initComponents)
```
- Sets up event listeners
- Initializes components on page load
- Configures input restrictions

## Utility Functions
```javascript
function formatBytes(bytes)
```
- Formats file sizes
- Converts bytes to human-readable format

## Security Considerations

1. Input Validation
   - Numeric input restriction
   - File type validation
   - Parameter validation before test execution

2. File Handling
   - Secure file upload process
   - Validated file extensions
   - Size limit checks

3. API Communication
   - Credentials included in requests
   - Error handling for all API calls
   - Secure session management

## Dependencies
- Modern web browser with JavaScript enabled
- Server-side API endpoints (/api/*)
- DOM manipulation capabilities
- Fetch API support
