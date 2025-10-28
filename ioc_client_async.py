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
SERVER_URL = "https://mindub.ddns.net"

run_tests = [1, 2, 4, 5, 11]
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

# ===================================================
# Generate random binary sequence in memory
# ===================================================
def generate_random_data(num_sequences: int = 10, bits_per_sequence: int = 1_000_000) -> io.BytesIO:
    print(f"Generating random data with {num_sequences} sequences of {bits_per_sequence} bits each...", end=' ')
    buffer = io.BytesIO()
    for _ in range(num_sequences):
        bits = np.random.randint(0, 2, size=bits_per_sequence, dtype=np.uint8)
        buffer.write(np.packbits(bits))
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
        data = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE)
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
# Main 
# ===========================
sessions = []
df = pd.DataFrame(columns=['Client ID', 'Test', 'Result', 'Passrate', 'Chi square', 'Kolmogorov-Smirnov', 'Time (ms)'])
lock = threading.Lock()  # global lock for safe writes
results_queue = queue.Queue()

# Initialize client sessions
for _ in range(NUM_CLIENTS):
    client_session = create_client(SERVER_URL)
    sessions.append(client_session)

def run_test_async(client, server_url, params, idx, df_idx):
    response = send_test_request(client, server_url, params)
    results_queue.put((idx, df_idx, response))

def process_results_queue():
    while not results_queue.empty():
        idx, df_idx, response = results_queue.get()
        if response:
            with lock:  # protect shared df
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

def run_emulation():
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            while True:
                idx = random.randrange(NUM_CLIENTS)
                client = sessions[idx]
                print(f"\nRunning tests for client {idx}...")
                df_idx = idx * len(run_tests)

                for test in run_tests:
                    test_params['test'] = test
                    data = generate_random_data(NUM_SECUENCES, BITS_PER_SECUENCE)
                    upload_data(client, SERVER_URL, data)
                    executor.submit(run_test_async, client, SERVER_URL, dict(test_params), idx, df_idx)
                    df_idx += 1

                process_results_queue()

                with lock:
                    print(df.to_string(index=False))
                    df.to_csv("iot_clients_results.csv", index=False)

    except KeyboardInterrupt:
        print("\nExiting...")

run_emulation()
