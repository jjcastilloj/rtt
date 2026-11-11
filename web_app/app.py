"""
NIST Randomness Testing Tool (RTT) Web Application

This Flask web application provides a user interface for the NIST Statistical Test Suite (STS),
allowing users to perform various statistical tests on binary random number sequences.
The application supports file uploads, test execution, and result analysis with proper
statistical validation.

Key Features:
- Secure session management using Redis
- File upload and processing capabilities
- Statistical test execution and analysis
- Result visualization and download
- Entropy calculation
- Comprehensive statistical validation

Dependencies:
- Flask: Web framework
- Redis: Session management
- NumPy, Pandas, SciPy: Statistical analysis
- Werkzeug: Security utilities
"""

import numpy as np
import pandas as pd
import tarfile
import os
import subprocess
import scipy.special
import uuid
import redis # type: ignore

from flask import Flask, request, jsonify, send_file, abort, session, send_from_directory
from flask_session import Session
from werkzeug.utils import secure_filename
from scipy.stats import ks_1samp, uniform, chisquare
from datetime import timedelta
import time

# Initialize Flask application
app = Flask(__name__)

# Configure Flask application settings
app.config['SESSION_TYPE'] = 'redis'
app.config['SECRET_KEY'] = 'losgatos2025'
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'rtt:'
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379, db=0)
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['PREFERRED_URL_SCHEME'] = 'https'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_PATH'] = '/'

# Define application paths
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
USER_FILES_DIR = '/tmp/rtt'

# Initialize Flask-Session
Session(app)

# Define allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'tar', 'png', 'jpg', 'jpeg', 'gif', 'bin', 'txt'}
def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#############################################################################
##### Create file structure and symbolic links for each user session ########
#############################################################################
@app.route('/api/setup', methods=['POST'])
def setup_session():
    """
    Initialize a new user session and create necessary directory structure.
    
    Returns:
        JSON: Response containing session ID and status message
    """
    session.clear()
    
    if 'session_id' not in session:
        print("Session not found, creating one...")
        session['session_id'] = str(uuid.uuid4())
        session_id = session.get('session_id')
        session_dir = os.path.join(USER_FILES_DIR, session_id)
       
        os.makedirs(session_dir, exist_ok=True)

        required_structure = nist_test 
        for subdir in required_structure:
            os.makedirs(os.path.join(session_dir + "/experiments/AlgorithmTesting", subdir), exist_ok=True)
        
        # Create data directory for binary random numbers files
        os.makedirs(os.path.join(session_dir, 'data'), exist_ok=True)
        # Create symlink to templates dir for some tests
        templates_path = os.path.join(APP_ROOT, 'templates')
        symlink_path = os.path.join(session_dir, 'templates')
        if not os.path.exists(symlink_path):
            os.symlink(templates_path, symlink_path)
        # Create symlink to sample random numbers file
        sample_path = os.path.join(APP_ROOT, 'data', 'SAMPLE.BIN')
        symlink_path = os.path.join(session_dir, 'data', 'SAMPLE.BIN')
        if not os.path.exists(symlink_path):
            os.symlink(sample_path, symlink_path)

        print("Session work directory is ", session_dir)
        session['session_dir'] = session_dir
        print("APP_ROOT is ", APP_ROOT)
   
    else:
        session_id = session.get('session_id')
        print("Session already active", session_id)
        print("Workdir => ", session.get('session_dir'))  
        
    return jsonify({"msg": "Environment ready", "session_id": session_id})

#################################################################
#############   Upload random numbers binary file  ##############
#################################################################
@app.route('/api/upload', methods=['POST', 'GET'])
def upload_file():
    """
    Handle file uploads for random number sequences.
    
    Returns:
        JSON: Response containing upload status and filename
    """
    if 'session_id' not in session:
        print("Session not found")
        return jsonify({'success': False, 'error': 'Session not found'}), 400

    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'None file received'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    session_dir = session.get('session_dir')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  
        uploads_path = os.path.join(session_dir, 'data')
        if not os.path.exists(uploads_path):
            os.makedirs(uploads_path)
        filepath = os.path.join(uploads_path, filename)

        file.save(filepath) 
        session['binary_file'] = filename
        print("Binary data file is:", session.get('binary_file'))

        return jsonify({
            'success': True,
            'filename': filename,
        }), 200
    else:
        return jsonify({'success': False, 'error': 'Forbiden file type'}), 400

#################################################################
####  Use sample binary random numbers file        ##############
#################################################################
@app.route('/api/sample', methods=['POST'])
def use_sample_file():
    """
    Set up the application to use the sample binary random numbers file.
    
    Returns:
        JSON: Response containing the sample file information
    """
    print("My session is => ", session.get('session_id'))
    session['binary_file'] = 'SAMPLE.BIN'
    print("Binary data file is (SAMPLE): ", session.get('binary_file'))
    
    return jsonify({"data": session.get('binary_file')}), 200

#################################################################
#############  Process test data                   ##############
#################################################################
@app.route('/api/test', methods=['POST', 'GET'])
def test_process():
    """
    Process and execute statistical tests on the uploaded random number sequence.
    
    Returns:
        JSON: Response containing test results and statistical measures
    """
    print("Source binary data file is: ", session.get('binary_file'))

    data = request.get_json()
 
    if data is None:
        return jsonify({"error": "No data received"}), 400

    test_params = data

    #print(test_params)
    for key, value in test_params.items():
        if value in [None, "", [], {}]:
            print(key,value)
            print("Error in test parameters")
            return jsonify({"msg": f"Required data missing {key}", "code": -1}), 400
    
    # First execute the assess command with received parameters to generate results file
    start_time = time.time()
    run_assess(test_params)
    # Then process the result files
    test_index = int(test_params['test']) - 1
    results = process_results(nist_test[test_index])

    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000  # in milliseconds

    response = {
        "msg": "OK",
        "test": test_params['test'],
        "chisquare": results[0],
        "ks": results[1],
        "approved": int(results[2]),
        "secuences": int(results[3]),
        "proportion": results[4],
        "passrate": results[5],
        "result": results[6],
        "time": elapsed_time,
        "session_id": session.get('session_id')
    }
    #print(test_params)
    return jsonify(response), 200

def run_assess(params):
    """
    Execute the NIST STS assess command with specified parameters.
    
    Args:
        params (dict): Dictionary containing test parameters
        
    Returns:
        str: Command output or error message
    """
    test_string = ''.join(['1' if i == params['test'] else '0' for i in range(1, 16)])
    session_dir = session.get('session_dir')
    data_file = session.get('binary_file')

    #print(f"Session dir is {session_dir} and data file is {data_file}")
   
    command = ['./assess', 
                '--fast', 
                '--prefix', session_dir,
                '--file', os.path.join(session_dir, 'data', data_file),
                '--tests', test_string,
                '--streams', str(params['secNum']),
                '--blockfreqpar', str(params['blockFreq']),
                '--nonoverpar', str(params['blockNon']),
                '--overpar', str(params['blockOver']),
                '--approxpar', str(params['blockApprox']),
                '--serialpar', str(params['blockSerial']),
                '--linearpar', str(params['blockLinear']),
                '--fileoutput',
                '--binary',
                params['secSize']
            ]
    command = [str(c) for c in command]
    print("Running command:", ' '.join(command))

    try:
    
        result = subprocess.run(command, capture_output=True, text=True)
        #print("Return code:", result.returncode)
        print("Standar output:", result.stdout)
        print(f"Standar error:", result.stderr if result.stderr else "No errors")
        
        if result.returncode in (0, 1):
            return result.stdout
        else:
            return f"Error executing command: {result.stderr}"
    except Exception as e:
        return str(e)

#################################################################
#############  Apply goodness fit test to results  ##############
#################################################################
def fit_test(data_column: pd.Series):
    """
    Apply goodness-of-fit tests to the test results.
    
    Args:
        data_column (pd.Series): Series containing test results
        
    Returns:
        tuple: Statistical measures including chi-square, KS test, pass count,
               data size, proportion, pass rate, and overall result
    """
    #print(test_params)
    alpha = 0.01
    if len(data_column) > 1:
        data_column = data_column[data_column > 0]
        pass_rate = 0.99 - 3.0 * np.sqrt(0.01 * (1.0 - alpha) / (len(data_column)))  # From NIST-STS code
        #pass_rate = round(pass_rate, 6)
        
        F, _ = np.histogram(data_column, bins=np.linspace(0, 1, 11))
        expected = np.full(F.shape, F.sum() / F.size, dtype=np.float64)
    
        _, chi2_p_value = chisquare(F, expected)
        _, ks_p_value = ks_1samp(data_column, uniform.cdf)
        #chi2_p_value = round(chi2_p_value, 6)
        #ks_p_value = round(ks_p_value,6)
        pass_count = (data_column > alpha).sum()
        uniformity = scipy.special.gammaincc(9.0/2.0, chi2_p_value/2.0)
        #print("Uniformity = ", uniformity)   
        proportion = pass_count / len(data_column)
        #proportion = round(proportion, 6)
        data_size = len(data_column)

        result = "SUCCESS" if proportion > pass_rate and uniformity > 0.0001 else "FAILURE"
        return f"{chi2_p_value:.6f}", f"{ks_p_value:.6f}", pass_count, data_size, f"{proportion:.6f}", f"{pass_rate:.6f}", result
    else:
        chi2_p_value = data_column[0]
        ks_p_value = "NA"
        pass_rate = alpha
        pass_count = 1 if chi2_p_value > alpha else 0
        data_size = len(data_column)
        proportion = pass_count / len(data_column)
        result = "SUCCESS" if chi2_p_value > alpha else "FAILURE"
        return chi2_p_value, ks_p_value, pass_count, data_size, proportion, pass_rate, result

##################################################################
####### Process the result files after run assess command #######
##################################################################
def process_results(test_name):
    """
    Process and analyze the results file from the NIST STS assessment.
    
    Args:
        test_name (str): Name of the statistical test
        
    Returns:
        tuple: Processed results including statistical measures and test outcome
    """
    session_dir = session.get('session_dir')
    results_file = os.path.join(session_dir,'experiments/AlgorithmTesting', test_name, 'results.txt')
    
    print(f"Processing results file: {results_file}")

    if os.path.getsize(results_file) == 0:
        print("Empty results file")
        return 0, 0, 0, 0, 0, 0, "EMPTY"

    results = []

    with open(results_file, 'r') as file: 
        for line in file:
            results.append(float(line.strip()))
    
    data = pd.DataFrame(results)
    
    if data.isnull().values.any():
        print("Results file is NaN filled")
        return 0, 0, 0, 0, 0, 0, "NaN"

    if (data == 0).all().all():
        print("Results file is Zero filled")
        return 0, 0, 0, 0, 0, 0, "ZEROS"
   
    results = fit_test(data[0])

    return results

##################################################################
####### Create a TAR compressed file with detailed results #######
##################################################################
def create_tar_file(tar_file, test_list):
    """
    Create a compressed TAR file containing detailed test results.
    
    Args:
        tar_file (str): Path to the output TAR file
        test_list (list): List of test indices to include
        
    Returns:
        bool: True if successful, False otherwise
    """
    directories = [ nist_test[i] for i in test_list]
    #print(directories)
    session_dir = session.get('session_dir')
    try:
        with tarfile.open(tar_file, "w:gz") as tar:
            for directory in directories:
                full_path = os.path.join(session_dir,'experiments/AlgorithmTesting', directory)
                if(os.path.exists(full_path)):
                    tar.add(full_path, arcname=directory)
                    print(f"Added: {full_path} (arcname: {directory})")
                else:
                    print(f"Warning: {full_path} does not exist.")
            
        return True

    except Exception as e:
        print("Error creating compressed file.", e)
        return False

##################################################################
## Endpoint to download compressed file with detailed results ####
##################################################################
@app.route('/api/download_results', methods=['POST'])
def download_results():
    """
    Endpoint for downloading detailed test results as a compressed file.
    
    Returns:
        File: Compressed TAR file containing test results
    """
    TAR_FILE = "detailed_results.tar.gz"
    session_dir = session.get('session_dir')
    data = request.get_json()
 
    if data is None:
        return jsonify({"error": "No data received"}), 400

    test_list = data.get('testList')
    tar_file = os.path.join(session_dir, TAR_FILE)
    success = create_tar_file(tar_file, test_list)

    if not success or not os.path.exists(tar_file):
        abort(500, description="Error creating compressed results file")

    results_file = os.path.join(session_dir, TAR_FILE)
    
    return send_file(results_file, as_attachment=True)
#################################################################
#############       Endpoint to test Entropy       ##############
@app.route("/api/ent", methods=['POST'])
def run_ent():
    """
    Calculate entropy of the uploaded binary file using the 'ent' utility.
    
    Returns:
        JSON: Response containing entropy calculation results
    """
    file = session.get('binary_file')
    if not file:
        return jsonify({"error": "No data file specified"}), 400
    
    session_dir = session.get('session_dir')
    file_path = os.path.join(session_dir, 'data', file)

    start_time = time.time()
    result = subprocess.run(["ent", file_path], capture_output=True, text=True)
    end_time = time.time()
    elapsed_time = (end_time - start_time) * 1000 # in milliseconds
    exec_time = f"Entropy test finished in {elapsed_time:.2f} ms"
    result.stdout += "\n" + exec_time

    if result.returncode != 0:
        return jsonify({"error": f"Error executing command: {result.stderr}"}), 500

    return jsonify({"result": result.stdout, "elapsed_time": elapsed_time, "status": "OK", "file": file})


#################################################################
#############              Main App                ##############
#################################################################
nist_test = ["Frequency", "BlockFrequency", "CumulativeSums", 
            "Runs", "LongestRun", "Rank", "FFT", "NonOverlappingTemplate", 
            "OverlappingTemplate", "Universal", "ApproximateEntropy", 
            "RandomExcursions", "RandomExcursionsVariant", "Serial", "LinearComplexity"]

if __name__ == '__main__':
    
    app.run()
    
