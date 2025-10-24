import requests
import numpy as np
import pandas as pd
import json
import time
import random

NUM_CLIENTS = 5
TMP_FILE = "tmp_random_sequence.bin"
NUM_SECUENCES = 100
BITS_PER_SECUENCE = 1_000_000
SERVER_URL = "http://127.0.0.1:8000"

run_tests = [1,2,3] # NIST tests to execute (1-15)

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
# Generate random binary secuence file
# ====================================
def generate_random_file(filename: str, num_sequences: int = 10, bits_per_sequence: int = 1_000_000):
    print(f"Generating random file: {filename} with {num_sequences} sequences of {bits_per_sequence} bits each", end='...')
    with open(filename, "wb") as f:
        for _ in range(num_sequences):
            # Generate random bits {0,1} and convert to bytes
            bits = np.random.randint(0, 2, size=bits_per_sequence, dtype=np.uint8)
            # Pack 8 bits into 1 byte
            bytes_array = np.packbits(bits)
            f.write(bytes_array)
    print(f"OK")

# Upload binary file with random secuence
def upload_file(session, server_url, filename):
    print(f"Uploading file {filename} to server...", end=' ')
    with open(filename, 'rb') as f:
        resp = session.post(f'{server_url}/api/upload', files={'file': f})
    if resp.status_code == 200:
        print("File uploaded successfully")
        return True
    else:   
        print("File upload failed with status code:", resp.status_code)
        return False

def create_client(server_url):   
    print("Creating client environment...", end='')
    session = requests.Session()
    # Initialize the session on the backend
    resp = session.post(f"{server_url}/api/setup")
    if resp.status_code == 200:
        generate_random_file(TMP_FILE, NUM_SECUENCES, BITS_PER_SECUENCE)
        # Upload the random file to the server
        if upload_file(session, server_url, TMP_FILE):
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
df = pd.DataFrame(columns=['Client', 'Test', 'Result', 'Passrate', 'Chi square', 'Kolmogorov', 'Time (ms)'])

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
                response['test'], 
                response['result'], 
                response['passrate'], 
                response['chisquare'], 
                response['ks'], 
                f"{response['time']:.2f}"]
            
            idx += 1
#stdsrc.addstr(df.to_string(index=False))

def run_emulation():
    try:
        while True:
            idx = random.randrange(NUM_CLIENTS)
            client = sessions[idx]
            print(f"\nRunning tests for client {idx}...")
            df_idx = idx * len(run_tests)
            for test in run_tests:
                test_params['test'] = test
                generate_random_file(TMP_FILE, NUM_SECUENCES, BITS_PER_SECUENCE)
                upload_file(client, SERVER_URL, TMP_FILE)
                response = send_test_request(client, SERVER_URL, test_params)
                
                if response:
                    #print(f"{i} Test {response['test']} Result: {response['result']}, Passrate: {response['passrate']}, Time: {response['time']:.2f} ms")
                    #print(f"Client {i} RESPONSE: {response}")
                    print(df_idx)
                    df.loc[df_idx] = [
                        idx, 
                        response['test'], 
                        "PASS" if response['result'] else "FAIL", 
                        response['passrate'], 
                        response['chisquare'], 
                        response['ks'], 
                        f"{response['time']:.2f}"]
                    
                    df_idx += 1
                else:
                    print("Test failed for client")
            
            print(df.to_string(index=False))
            df.to_csv("iot_clients_results.csv", index=False)

            #time.sleep(0.2)

    except KeyboardInterrupt:
     
        print("Exiting...")

run_emulation()




