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
# Main loop (parallel tests, stop after 2 failures total)
# ===========================
sessions = []
df_columns = ['IoT Device Number', 'Source', 'Test',
              'Result', 'Chi square', 'Kolmogorov-Smirnov',
              'Proportion', 'Pass rate', 'Time (ms)']

# Create client sessions
for _ in range(NUM_CLIENTS):
    client_session = create_client(SERVER_URL)
    sessions.append(client_session)

def run_test_async(client, server_url, params, client_idx):
    """Execute test and return (client_idx, response)."""
    response = send_test_request(client, server_url, params)
    return client_idx, response

try:
    iteration = 0
    stop_experiment = False
    failure_count = 0   # global accumulated failures across iterations
    failure_records = []  # list of dicts with failure details (to be placed in final df)

    # main loop: run iterations until >=2 failures observed
    while not stop_experiment:
        iteration += 1
        print(f"\n=== Iteration {iteration} ===")

        # DataFrame for this iteration (consolidated)
        df = pd.DataFrame(columns=df_columns)

        # store exact uploaded bytes and source per client for this iteration
        last_data_per_client = {}

        # 1) For each client: generate unique data and upload it
        for client_idx, client in enumerate(sessions):
            source = random.choice(["PRNG", "TRNG"])
            print(f"IoT device {client_idx}: generating data from {source}")

            data_buffer = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE, source=source)
            data_buffer.seek(0)
            data_bytes = data_buffer.read()
            last_data_per_client[client_idx] = (data_bytes, source)

            # upload (create fresh BytesIO for upload)
            upload_buf = io.BytesIO(data_bytes)
            if upload_data(client, SERVER_URL, upload_buf):
                print(f"Client {client_idx}: data uploaded")
            else:
                raise RuntimeError(f"Could not upload file for client {client_idx}")

        # 2) Submit all tests for all clients to executor
        futures = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            for client_idx, client in enumerate(sessions):
                for test in run_tests:
                    test_params_copy = dict(test_params)
                    test_params_copy['test'] = test
                    futures.append(executor.submit(run_test_async, client, SERVER_URL, test_params_copy, client_idx))

            # 3) Process results as futures complete (ensures we collect all test results this iteration)
            for fut in concurrent.futures.as_completed(futures):
                client_idx, response = fut.result()
                if response is None:
                    # Unexpected failure to get response
                    print(f"Warning: no response for client {client_idx}")
                    continue

                # Map source
                data_bytes, src = last_data_per_client[client_idx]

                # Build row dict (use .get to be robust)
                row = {
                    'IoT Device Number': client_idx,
                    'Source': src,
                    'Test': nist_test[int(response['test']) - 1],
                    'Result': response['result'],
                    'Chi square': response.get('chisquare', ''),
                    'Kolmogorov-Smirnov': response.get('ks', ''),
                    'Proportion': response.get('proportion', ''),
                    'Pass rate': response.get('passrate', ''),
                    'Time (ms)': f"{response.get('time', 0):.2f}"
                }

                # Append row to DataFrame
                df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

                # If this test failed, record it and save binary immediately
                if response['result'] != "SUCCESS":
                    failure_count += 1
                    failed_test_name = row['Test']
                    failure_number = failure_count
                    print(f"\nFailure #{failure_number}: client {client_idx}, test {failed_test_name}, source {src}")

                    # Save binary that caused this failure (unique filename per failure)
                    fail_filename = f"failed_sequence_iter{iteration}_client{client_idx}_{src}_fail{failure_number}.bin"
                    with open(fail_filename, "wb") as f:
                        f.write(data_bytes)
                    print(f"Saved failed binary: {fail_filename}")

                    # store full failure record (row + filenames + iteration)
                    failure_records.append({
                        'failure_number': failure_number,
                        'iteration': iteration,
                        'client_idx': client_idx,
                        'test': failed_test_name,
                        'source': src,
                        'binary_filename': fail_filename
                    })

                    # If we have reached the threshold, still keep collecting remaining futures
                    # so df will include all tests of this iteration; set stop_experiment so loop exits after iteration
                    if failure_count >= 2:
                        stop_experiment = True
                        # do NOT break here — continue processing remaining futures to complete df

            # end processing futures

        # 4) After processing all futures for the iteration, save consolidated CSV
        results_csv = f"last_results_iter{iteration}.csv"
        df.to_csv(results_csv, index=False)
        print(f"\nIteration {iteration} consolidated results saved to {results_csv}")

        # 5) For each recorded failure, create a CSV copy that links the consolidated results to that failure
        #    (this guarantees the consolidated CSV contains the failure rows)
        for rec in failure_records:
            if rec['iteration'] == iteration:
                # create copy name by matching binary filename base
                base = os.path.splitext(rec['binary_filename'])[0]
                csv_copy_name = base + ".csv"
                shutil.copy(results_csv, csv_copy_name)
                rec['results_csv'] = csv_copy_name
                print(f"Copied consolidated CSV to {csv_copy_name} for failure #{rec['failure_number']}")

        # 6) Decide whether to stop the experiment
        if failure_count >= 2:
            print(f"\nStopping experiment: total failures reached {failure_count}")
            break

        # Otherwise continue to next iteration

except KeyboardInterrupt:
    print("\nUser interrupt")
