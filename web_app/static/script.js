/**
 * NIST Randomness Testing Tool (RTT) Frontend Application
 * 
 * This JavaScript module provides the frontend functionality for the NIST Statistical Test Suite (STS) web interface.
 * It handles file uploads, test configuration, execution, and result visualization.
 * 
 * Key Features:
 * - File upload and management
 * - Test parameter configuration
 * - Real-time test execution
 * - Result visualization and export
 * - Session management
 * - Logging system
 */

// Global state variables
let selectedFileName = "Select file";  // Currently selected file name
let selectedFileSize = 0;             // Size of the selected file in bytes
let fileUploaded = false;             // Flag indicating if a file has been uploaded
let checkbox_checked = true;          // State of test selection checkboxes

// DOM element references
let logDiv = document.getElementById('logDiv');
let logMessages = [];                 // Array to store log messages
let testData = {};                    // Object to store test results

/**
 * Enable all input elements within a specified group
 * @param {string} groupName - The data-group attribute value to identify inputs
 */
function enableGroupInputs(groupName) {
    let inputs = document.querySelectorAll(`input[data-group="${groupName}"]`);
    inputs.forEach(input => input.disabled = false);
}

/**
 * Disable all input elements within a specified group
 * @param {string} groupName - The data-group attribute value to identify inputs
 */
function disableGroupInputs(groupName) {
    let inputs = document.querySelectorAll(`input[data-group="${groupName}"]`);
    inputs.forEach(input => input.disabled = true);
}

/**
 * Toggle between default and manual block size parameter settings
 * Updates UI elements and sets default values when switching to manual mode
 */
function defaultBlockSizes() {
    lblBlock = document.getElementById('lblBlock');
    if (lblBlock.textContent.includes("Enter")) {
        lblBlock.innerHTML = "<i class='ti ti-2fa'></i> Load default block size values";
        enableGroupInputs('block-params');
    }
    else {
        lblBlock.innerHTML = "<i class='ti ti-writing'></i> Enter block size values manually";
        disableGroupInputs('block-params');
        document.getElementById('blockFreq').value = 128;
        document.getElementById('blockNon').value = 9;
        document.getElementById('blockOver').value = 9;
        document.getElementById('blockApprox').value = 10;
        document.getElementById('blockSerial').value = 16;
        document.getElementById('blockLinear').value = 500;
        addLogMessage("Using default block parameters");

    }
}

/**
 * Toggle between sample file and personal file upload modes
 * Handles the UI updates and server communication for file selection
 */
async function defaultSample() {
    lblSample = document.getElementById('lblSample');
    if (lblSample.textContent.includes("Load")) {
        document.getElementById('data_file').removeAttribute("onclick");
        document.getElementById('data_file').innerHTML = "Using internal sample file:<br> SAMPLE.BIN - 2.0 GB";
        lblSample.innerHTML = "<i class='ti ti-user-check'></i> Use custom binary random file";
        document.getElementById('uploadButton').style.display = "none";
        addLogMessage("Using sample random numbers file");

        fetch('/api/sample', {
            method: 'POST',
            credentials: 'include'
        })
            .then(response => response.json())
            .then(data => {
                if (data.data.includes("SAMPLE.BIN")) { 
                    addLogMessage("Sample file loaded");
                    selectedFileName = data.data;
                    fileUploaded = true;
                    enableGroupInputs('test-check');
                    enableGroupInputs('sec-params')
                }
                //console.log("Respuesta del servidor:", data);
            })
            .catch(error => console.error('Error al copiar el archivo:', error));

    }
    else {
        document.getElementById('data_file').setAttribute("onclick", "selectFile()");
        document.getElementById('data_file').textContent = "Select file";
        document.getElementById('uploadButton').style.display = "block";
        lblSample.innerHTML = "<i class='ti ti-archive'></i> Load internal random sample file";
    }

}

/**
 * Validate that all required input fields are filled
 * @returns {boolean} True if all required fields are filled, false otherwise
 */
function validateInputs() {
    let form = document.getElementById('dataForm');
    let inputs = document.querySelectorAll(`input[data-group="block-params"]`);

    for (let input of inputs) {
        if (input.value.trim() === "") {
            console.log(input);
            addLogMessage("Please fill all required data");
            return false;
        }
    }
    return true;
}

/**
 * Restrict input fields to accept only numeric values
 * Adds event listeners to all text inputs
 */
function restrictInputs() {
    const inputs = document.querySelectorAll('input[type="text"]');
    inputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '');
        });
    });
}

/**
 * Format bytes into human-readable string with appropriate units
 * @param {number} bytes - Number of bytes to format
 * @returns {string} Formatted string with size and unit
 */
function formatBytes(bytes) {
    if (bytes === 0) return "0 Bytes";

    const units = ["Bytes", "KB", "MB", "GB", "TB"];
    let i = Math.floor(Math.log(bytes) / Math.log(1024));

    let size = (bytes / Math.pow(1024, i)).toFixed(1);
    return `${size} ${units[i]}`;
}

/**
 * Add a message to the log display with timestamp
 * @param {string} message - Message to add to the log
 */
function addLogMessage(message) {

    const now = new Date();
    const timestamp = now.toLocaleString();  // "12/31/2023, 11:59:59 PM"
    const fullMessage = `[${timestamp}] ${message}`;

    logMessages.push(fullMessage);
    const logDiv = document.getElementById('logDiv');
    logDiv.innerHTML = logMessages.join('<br>');
}

/**
 * Clear all messages from the log display
 */
function clearLog() {
    logDiv = document.getElementById("logDiv");
    logDiv.innerHTML = "";
    logMessages = [];

}

/**
 * Clear all test results from the results table
 */
function clearTable() {
    const rows = document.getElementById("resultsTable").getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');

        for (let j = 2; j < cells.length; j++) {
            cells[j].textContent = '--';
        }
    }
}

/**
 * Trigger file selection dialog
 */
function selectFile() {
    const fileInput = document.getElementById('input_file');
    if (fileInput) {
        fileInput.click();
    } else {
        console.error('File input element not found');
    }
}

/**
 * Handle file selection change event
 * Updates UI elements with selected file information
 */
function handleFileChange() {
    const fileInput = document.getElementById('input_file');
    const dataFile = document.getElementById('data_file');
    const uploadLbl = document.getElementById('uploadLbl');

    if (!fileInput || !dataFile || !uploadLbl) {
        console.error('Required elements not found');
        return;
    }

    const file = fileInput.files[0];
    if (file) {
        selectedFileName = file.name;
        selectedFileSize = file.size;
        dataFile.textContent = selectedFileName;
        uploadLbl.textContent = " Upload - " + formatBytes(file.size);
        clearTable();
        addLogMessage("File selected: " + selectedFileName);
    } else {
        selectedFileName = "Select file";
        selectedFileSize = 0;
        dataFile.textContent = selectedFileName;
        uploadLbl.textContent = "";
        addLogMessage("No file selected");
    }
}

/**
 * Initialize the testing environment by setting up a new session
 * Communicates with the server to create necessary directory structure
 */
async function setupSession() {
    try {
        const response = await fetch('/api/setup', {
            method: 'POST',
            credentials: 'include'
        });
        const result = await response.json();
        addLogMessage(result.msg)
        console.log(result)

    } catch (error) {
        addLogMessage("Error initializing environment");
        console.error('Error:', error);
    }
}

/**
 * Upload the selected file to the server
 * Handles the upload process and updates UI based on server response
 */
function uploadFile() {
    const dataFile = document.getElementById('data_file');
    const fileInput = document.getElementById('input_file');

    if (!dataFile || !fileInput) {
        console.error('Required elements not found');
        return;
    }

    if (selectedFileName === "Select file") {
        dataFile.style.color = "red";
        addLogMessage("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    addLogMessage("Uploading file: " + selectedFileName + "...");

    fetch('/api/upload', {
        method: 'POST',
        body: formData,
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(result => {
        if (result.success) {
            fileUploaded = true;
            addLogMessage("File uploaded successfully");
            clearTable();
            enableGroupInputs('sec-params');
            enableGroupInputs('test-check');
            document.getElementById('lblBlock').style.display = "block";
            dataFile.style.color = "inherit";
        } else {
            addLogMessage("Error uploading file: " + result.error);
            dataFile.style.color = "red";
        }
    })
    .catch(error => {
        addLogMessage("Server error: " + error.message);
        dataFile.style.color = "red";
    });
}

/**
 * Toggle the state of all test selection checkboxes
 * Only works when a file has been uploaded
 */
function toggleAllCheckboxes() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');

    if (fileUploaded) {
        if (checkbox_checked) {
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
                checkbox_checked = false;
            });
        } else {
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
                checkbox_checked = true;
            });
        }
    }
}

/**
 * Start the statistical testing process
 * Collects test parameters and initiates test execution
 */
async function startTest() {

    if (fileUploaded) {

        if (!validateInputs()) {
            return;
        }

        const secSize = document.getElementById('secuenceSize').value;
        const secNum = document.getElementById('secuenceNum').value;
        const blockFreq = document.getElementById('blockFreq').value;
        const blockNon = document.getElementById('blockNon').value;
        const blockOver = document.getElementById('blockOver').value;
        const blockApprox = document.getElementById('blockApprox').value;
        const blockSerial = document.getElementById('blockSerial').value;
        const blockLinear = document.getElementById('blockLinear').value;

        const tests = document.querySelectorAll('input[type="checkbox"]');

        if(!selectedFileName.includes('SAMPLE.BIN')){
            if (secSize * secNum > selectedFileSize * 8) {
                addLogMessage("Insufficient data in file");
                return;
            }
            enableGroupInputs('test-check');
        }

        testData['secSize'] = secSize;
        testData['secNum'] = secNum;
        testData['blockFreq'] = blockFreq;
        testData['blockNon'] = blockNon;
        testData['blockOver'] = blockOver;
        testData['blockApprox'] = blockApprox;
        testData['blockSerial'] = blockSerial;
        testData['blockLinear'] = blockLinear;

        testData['dataFile'] = selectedFileName;

        testId = 1;

        let requests = [];
        let requestError = false;

        //clearTable();

        const nonChecked = Array.from(tests).every(checkbox => !checkbox.checked);

        if (nonChecked) {
            addLogMessage("Please select tests");
            document.getElementById("actionsTable").style.display = "none";
            return;
        }

        addLogMessage("Running NIST  SP800-22 tests...");
        document.getElementById("actionsTable").style.display = "none";

        tests.forEach(checkbox => {
            if (checkbox.checked) {

                updateStatus(testId, 8);

                testData['test'] = testId;

                let request = fetch('/api/test', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(testData)
                })
                    .then(response => response.json())
                    .then(data => {
                        //console.log('Server response:', data);
                        if (data['code'] == -1) {
                            requestError = true;
                            return;
                        }

                        updateTable(data['test'], 2, data['chisquare']);
                        updateTable(data['test'], 3, data['ks']);
                        updateTable(data['test'], 4, data['secuences']);
                        updateTable(data['test'], 5, data['approved']);
                        updateTable(data['test'], 6, data['proportion']);
                        updateTable(data['test'], 7, data['passrate']);

                        if (data['result'] == "SUCCESS") {
                            circleColor = "text-success";
                        }
                        else if (data['result'] == "FAILURE") {
                            circleColor = "text-danger";
                        }
                        else {
                            circleColor = "text-warning";
                        }

                        let test_result = `<span class="d-flex align-items-center gap-2">
                              <i class="fas fa-circle ` + circleColor + ` text-success f-10 m-r-5"></i>` + data['result'] + `</span>`;
                        updateTable(data['test'], 8, test_result);

                    })
                    .catch(error => {
                        console.error('Error sending data:', error);
                        return;
                    });

                requests.push(request);
            }

            testId++;

        });

        let responses = await Promise.all(requests);

        if (requestError) {
            addLogMessage("Required data missing");
            clearTable();
        }
        else {
            addLogMessage("NIST SP800-22 tests completed");
            document.getElementById("actionsTable").style.display = "table";
        }


    } else {
        addLogMessage("Please select and upload a file");
    }
}

/**
 * Update the status of a specific test in the results table
 * @param {number} fil - Row index in the results table
 * @param {number} col - Column index in the results table
 */
function updateStatus(fil, col) {

    let table = document.getElementById('resultsTable');
    let statusCel = table.rows[fil].cells[col];
    let statusBar = document.createElement("div");

    statusBar.classList.add("loading-bar");
    statusCel.textContent = "";
    statusCel.appendChild(statusBar);
    statusBar.style.display = "block";

}

/**
 * Update a specific cell in the results table
 * @param {number} fil - Row index in the results table
 * @param {number} col - Column index in the results table
 * @param {string} value - Value to set in the table cell
 */
function updateTable(fil, col, value) {

    let table = document.getElementById('resultsTable');
    table.rows[fil].cells[col].innerHTML = ""
    table.rows[fil].cells[col].innerHTML = value;

}

/**
 * Download the results table as a CSV file
 */
function downloadTableAsCSV() {

    const tableId = "resultsTable";
    const filename = "results.csv";
    const rows = document.querySelectorAll(`#${tableId} tr`);
    const csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll("td, th");
        const rowData = [];

        cols.forEach(col => {
            let data = col.innerText;
            data = data.replace(/"/g, '""');
            rowData.push(`"${data}"`);
        });

        csv.push(rowData.join(","));
    });

    const csvString = csv.join("\n");
    const blob = new Blob([csvString], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);

    const downloadLink = document.createElement("a");
    downloadLink.href = url;
    downloadLink.download = filename;
    document.body.appendChild(downloadLink);
    downloadLink.click();

    document.body.removeChild(downloadLink);
    window.URL.revokeObjectURL(url);
}

/**
 * Download detailed test results as a compressed file
 */
function downloadResults() {

    addLogMessage("Downloading results");

    const tests = document.querySelectorAll('input[type="checkbox"]');
    const testList = Array.from(tests)
        .map((checkbox, index) => {
            if (!checkbox.checked) return -1;

            const row = checkbox.closest('tr');
            if (!row) return -1;

            const cells = row.querySelectorAll('td');
            const hasInvalidCell = Array.from(cells).some(cell => cell.innerText.trim() === '--');

            return hasInvalidCell ? -1 : index;
        })
        .filter(index => index !== -1);

    if (testList.length === 0) {
        addLogMessage("Please select tests to download");
        return;
    }

    console.log(testList);

    fetch('/api/download_results',
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ testList: testList })
        }

    )
        .then(response => {
            if (!response.ok) {
                throw new Error("Error processing request: " + response.statusText);
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'detailed_results.tar.gz';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            addLogMessage("Download complete");
        })
        .catch(error => {
            console.error("Error downloading file:", error);
        });
}

/**
 * Calculate and display entropy information for the uploaded file
 */
function startEnt(){
    
    entResults = document.getElementById('entResults');
    //entResults.textContent = selectedFileName;
    console.log(selectedFileName);
    if(selectedFileName.includes("Select")){
        entResults.textContent = "Please select file...";
        addLogMessage("Please select file");
        return;
    }
    addLogMessage("Running entropy test...");
    entResults.textContent = "Test in progress. This may take several seconds, please wait...";

    fetch('/api/ent', {
        method: 'POST', 
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            selectedFile: selectedFileName 
        })
    })
    .then(response => response.json())
    .then(data => {
        //console.log("Resultado de la API:", data);
        if(data.status.includes("OK")){
            addLogMessage("Entropy test complete");
            entResults.textContent = "Source file: " + data.file + "\n\n" + data.result;
        }
    })
    .catch(error => console.error('Error:', error));
}

/**
 * Initialize all UI components and set up event listeners
 * Called when the page loads
 */
function initComponents() {
    clearTable();
    disableGroupInputs('block-params');
    disableGroupInputs('sec-params');
    disableGroupInputs('test-check');
    
    // Add event listener for file input
    const fileInput = document.getElementById('input_file');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileChange);
    } else {
        console.error('File input element not found');
    }
}

// Initialize components when the page loads
document.addEventListener('DOMContentLoaded', initComponents);
restrictInputs();
addLogMessage("Preparing environment...");
setupSession();




