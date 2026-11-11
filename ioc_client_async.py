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
import os
import shutil

NUM_CLIENTS = 4
NUM_SECUENCES = 55
BITS_PER_SECUENCE = 1_000_000
SERVER_URL = "https://mindub.ddns.net"

run_tests = [1, 2, 4, 5, 11]
nist_test = ["Frequency", "BlockFrequency", "CumulativeSums", 
            "Runs", "LongestRun", "Rank", "FFT", "NonOverlappingTemplate", 
            "OverlappingTemplate", "Universal", "ApproximateEntropy", 
            "RandomExcursions", "RandomExcursionsVariant", "Serial", "LinearComplexity"]

test_params = {
    "test": 0,
    "secNum": NUM_SECUENCES,
    "secSize": 1000000,
    "blockFreq": 128,
    "blockNon": 9,
    "blockOver": 9,
    "blockApprox": 10,
    "blockSerial": 16,
    "blockLinear": 500,
}

# ===================================================
# Generate random binary sequence (TRNG or PRNG)
# ===================================================
def generate_random_data(num_sequences: int = 10,
                         bits_per_sequence: int = 1_000_000,
                         source: str = "TRNG") -> io.BytesIO:
    """
    Generate a random binary sequence in memory.
    """
    print(f"Generating {source} data with {num_sequences} sequences of {bits_per_sequence} bits each...", end=' ')
    buffer = io.BytesIO()
    
    for _ in range(num_sequences):
        if source.upper() == "TRNG":
            total_bytes = (bits_per_sequence + 7) // 8
            buffer.write(os.urandom(total_bytes))
        elif source.upper() == "PRNG":
            bits = np.random.randint(0, 2, size=bits_per_sequence, dtype=np.uint8)
            buffer.write(np.packbits(bits))
        else:
            raise ValueError("Invalid source. Choose 'TRNG' or 'PRNG'.")
    
    buffer.seek(0)
    print("OK")
    return buffer

def upload_data(session, server_url, data_buffer, filename="rnd_data.bin"):
    files = {'file': (filename, data_buffer)}
    resp = session.post(f'{server_url}/api/upload', files=files)
    if resp.status_code == 200:
        print("File uploaded successfully")
        return True
    else:
        print("File upload failed:", resp.status_code)
        return False

def create_client(server_url):   
    print("Creating client environment...", end='')
    session = requests.Session()
    resp = session.post(f"{server_url}/api/setup")
    if resp.status_code == 200:
        data = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE, source="PRNG")
        if upload_data(session, SERVER_URL, data):
            print("Client environment created successfully")
        else:
            raise RuntimeError("Could not upload file to server")
    else:
        raise RuntimeError("Could not create environment on server")
    return session

def send_test_request(session, server_url, params):
    url = f"{server_url}/api/test"
    headers = {"Content-Type": "application/json"}
    try:
        response = session.post(url, data=json.dumps(params), headers=headers)
        if response.status_code == 200:
            print("Request successful.")
            return response.json()
        else:
            print(f"Server returned {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None

# ===========================
# Main loop
# ===========================
sessions = []
df_columns = ['IoT Device Number', 'Source', 'Test', 
              'Result', 'Chi square', 'Kolmogorov-Smirnov', 
              'Proportion', 'Pass rate', 'Time (ms)']

lock = threading.Lock()
results_queue = queue.Queue()

# Init client sessions
for _ in range(NUM_CLIENTS):
    client_session = create_client(SERVER_URL)
    sessions.append(client_session)

def run_test_async(client, server_url, params, client_idx):
    """Exect test and store results in queue"""
    response = send_test_request(client, server_url, params)
    results_queue.put((client_idx, response))

try:
    iteration = 0
    stop_experiment = False

    while not stop_experiment:
        iteration += 1
        print(f"\n=== Iteration {iteration} ===")

        df = pd.DataFrame(columns=df_columns)
        any_failure = False

        last_data_per_client = {}

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = []

            for client_idx, client in enumerate(sessions):
                # Select source randomly
                source = random.choice(["PRNG", "TRNG"])
                print(f"\nIoT device {client_idx}: generating data from {source}")

                data_buffer = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE, source=source)
                data_buffer.seek(0)
                data_bytes = data_buffer.read()
                last_data_per_client[client_idx] = (data_bytes, source)

                # Upload data
                upload_buf = io.BytesIO(data_bytes)
                if upload_data(client, SERVER_URL, upload_buf):
                    print("Random data uploaded")
                else:
                    raise RuntimeError(f"Could not upload file for client {client_idx}")

                # Exect selected tests for each client
                for test in run_tests:
                    test_params_copy = dict(test_params)
                    test_params_copy['test'] = test
                    futures.append(executor.submit(run_test_async, client, SERVER_URL, test_params_copy, client_idx))

            concurrent.futures.wait(futures)

        # Process results queue
        while not results_queue.empty():
            client_idx, response = results_queue.get()
            if response:
                print(response)
                _, src = last_data_per_client[client_idx]
                df = pd.concat([df, pd.DataFrame([{
                    'IoT Device Number': client_idx,
                    'Source': src,
                    'Test': nist_test[int(response['test']) - 1],
                    'Result': response['result'],
                    'Chi square': response['chisquare'],
                    'Kolmogorov-Smirnov': response['ks'],
                    'Proportion': response['proportion'],
                    'Pass rate': response['passrate'],
                    'Time (ms)': f"{response['time']:.2f}"
                }])], ignore_index=True)

                if response['result'] != "SUCCESS":
                    any_failure = True
                    failed_client = client_idx
                    failed_test = nist_test[int(response['test']) - 1]
            else:
                print(f"Error: client {client_idx} fail some test")
                any_failure = True
                failed_client = client_idx
                failed_test = "unknown"

        # Store results
        with lock:
            print(df.to_string(index=False))
            df.to_csv(f"last_results.csv", index=False)

        # Store associated binary secuence 
        if any_failure:
            data_bytes, src = last_data_per_client[failed_client]
            fail_filename = f"failed_sequence_iter{iteration}_client{failed_client}_{src}.bin"
            print(f"\nTest failed on client {failed_client}, test {failed_test}")
            print(f"Saving binary secuence in '{fail_filename}'")
            with open(fail_filename, "wb") as f:
                f.write(data_bytes)
          
            print("Saving associated results in cvs file")
            results_filename = f"failed_sequence_iter{iteration}_client{failed_client}_{src}.csv"
            shutil.copy("last_results.csv", results_filename)
            stop_experiment = True

except KeyboardInterrupt:
    print("\nUser interrupt")
