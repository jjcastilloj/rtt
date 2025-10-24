import requests
import numpy as np
import pandas as pd
import json
import time
import random
import concurrent.futures
import threading
import queue
import io


NUM_CLIENTS = 5
NUM_SECUENCES = 10
BITS_PER_SECUENCE = 1_000_000
SERVER_URL = "http://127.0.0.1:8000"

run_tests = [1, 2, 4, 5, 11] # NIST tests to execute (1-15) recomended subset [1, 2, 3, 4, 5, 11]

nist_test = ["Frequency", "BlockFrequency", "CumulativeSums", 
            "Runs", "LongestRun", "Rank", "FFT", "NonOverlappingTemplate", 
            "OverlappingTemplate", "Universal", "ApproximateEntropy", 
            "RandomExcursions", "RandomExcursionsVariant", "Serial", "LinearComplexity"]

test_params = {
        "test": 1,
        "secNum": NUM_SECUENCES,
        "secSize": 1000000,
        "blockFreq": 28,
        "blockNon": 9,
        "blockOver": 9,
        "blockApprox": 10,
        "blockSerial": 16,
        "blockLinear": 500,
    }

# ====================================
# Generate random binary secuence 
# ====================================

def generate_random_data(num_sequences: int = 10, bits_per_sequence: int = 1_000_000) -> io.BytesIO:
    """
    Generate a random binary sequence and return it as an in-memory binary stream.
    """
    print(f"Generating random data with {num_sequences} sequences of {bits_per_sequence} bits each...", end=' ')
    buffer = io.BytesIO()

    for _ in range(num_sequences):
        bits = np.random.randint(0, 2, size=bits_per_sequence, dtype=np.uint8)
        bytes_array = np.packbits(bits)
        buffer.write(bytes_array)

    buffer.seek(0)  # return to the beginning of the stream
    print("OK")
    return buffer


# Upload binary file with random secuence
def upload_data(session, server_url, data_buffer, filename="rnd_data.bin"):
    """
    Send binary data to the server from an in-memory stream.
    """
    files = {'file': (filename, data_buffer)}
    resp = session.post(f'{server_url}/api/upload', files=files)
    if resp.status_code == 200:
        print("File uploaded successfully")
        return True
    else:   
        print("File upload failed with status code:", resp.status_code)
        return False

# create client environment
def create_client(server_url):   
    print("Creating client environment...", end='')
    session = requests.Session()
    # Initialize the session on the backend
    resp = session.post(f"{server_url}/api/setup")
    if resp.status_code == 200:
        data = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE)
        # Upload the random data to the server
        if upload_data(session, SERVER_URL, data):
            print("Client environment created successfully")
        else:
            raise RuntimeError("Could not upload file to server")
    else:
        raise RuntimeError("Could not create environment on server")
    return session

# send test request to the server
def send_test_request(session, server_url, params):
    """
    Sends test parameters to the /api/test endpoint and returns the JSON response.
    Args:
        server_url (str): Base URL of the server, e.g. "http://127.0.0.1:5000"
        params (dict): Dictionary containing test parameters

    Returns:
        dict: Parsed JSON response from the server
    """
    url = f"{server_url}/api/test"
    headers = {"Content-Type": "application/json"}

    #print(f"Sending test request with params: {params}")

    try:
        response = session.post(url, data=json.dumps(params), headers=headers)

        if response.status_code == 200:
            print("Request successful.")
            return response.json()
        else:
            print(f"Server returned status code {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# ===========================
# Main 
# ===========================

# Create multiple clients and store their sessions
sessions = []
df = pd.DataFrame(columns=['Client ID', 'Test', 'Result', 'Passrate', 'Chi square', 'Kolmogorov-Smirnov', 'Time (ms)'])

for _ in range(NUM_CLIENTS):
    client_session = create_client(SERVER_URL)
    if client_session:
        sessions.append(client_session)
    else:
        print("Failed to create client session")


# init dataframe
idx = 0

for client_idx in range(NUM_CLIENTS):
    
    for test in run_tests:
        test_params['test'] = test
        
        response = send_test_request(sessions[client_idx], SERVER_URL, test_params)
        if response:
            df.loc[idx] = [
                client_idx, 
                nist_test[int(response['test']) - 1], 
                response['result'], 
                response['passrate'], 
                response['chisquare'], 
                response['ks'], 
                f"{response['time']:.2f}"]
            
            idx += 1

# Asynchronous test execution with ThreadPoolExecutor
print(df.to_string(index=False))
df.to_csv("iot_clients_results.csv", index=False)

results_queue = queue.Queue()
lock = threading.Lock()  # Optional, por si se usa stdout en paralelo

def run_emulation():
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            while True:
                idx = random.randrange(NUM_CLIENTS)
                client = sessions[idx]
                print(f"\nRunning tests for client {idx}...")
                df_idx = idx * len(run_tests)

                # launch async tasks without blocking the loop
                for test in run_tests:
                    test_params['test'] = test
                    data = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE)
                    upload_data(client, SERVER_URL, data)

                    # submit the test to be run in a separate thread
                    executor.submit(run_test_async, client, SERVER_URL, dict(test_params), idx, df_idx)
                    df_idx += 1

                # update DataFrame with any completed results
                process_results_queue()

                with lock:
                    print(df.to_string(index=False))

                df.to_csv("iot_clients_results.csv", index=False)
                #time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nExiting...")

# --- Función que se ejecuta en hilos ---
def run_test_async(client, server_url, params, idx, df_idx):
    response = send_test_request(client, server_url, params)
    if response:
        results_queue.put((idx, df_idx, response))
    else:
        results_queue.put((idx, df_idx, None))

# --- Procesa los resultados acumulados ---
def process_results_queue():
    while not results_queue.empty():
        idx, df_idx, response = results_queue.get()
        if response:
            df.loc[df_idx] = [
                idx,
                nist_test[int(response['test']) - 1],
                response['result'],
                response['passrate'],
                response['chisquare'],
                response['ks'],
                f"{response['time']:.2f}"
            ]
        else:
            print(f"Test failed for client {idx}")

run_emulation()