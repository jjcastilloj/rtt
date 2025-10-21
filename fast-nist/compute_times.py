import os
import subprocess
import time
import pandas as pd



def run_assess(fast=True, results_dir=None, data_file=None):

    # Use explicit parameters first, fallback to session if available
    
    if not results_dir or not data_file:
        return "Error: 'results_dir' and 'data_file' must be provided."
    # Añadir '--fast' si fast=True, eliminar si fast=False
    if fast:
        if '--fast' not in command:
            command.append('--fast')
    else:
        if '--fast' in command:
            command.remove('--fast')


    #print(f"Executing NIST STS {nist_test[params['test_id']]} {'FAST' if fast else 'NORMAL'} Test...")
    #print("COMMAND:", ' '.join(command))

    try:
        start_time = time.time()
        result = subprocess.run(command, capture_output=True, text=True)
        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000
        
        if result.returncode in (0, 1):
            return result.stdout, elapsed_ms
        else:
            return f"Error executing command:\n{result.stderr}", elapsed_ms
    except Exception as e:
        return f"Exception: {e}", None
    

##########################################################
# -- Main execution --
##########################################################
data_dir = "data"
data_file = "SAMPLE.BIN"
results_dir = "tmp_results"

nist_test = {
    1: "Frequency",
    2: "Block Frequency",
    3: "Cumulative Sums",
    4: "Runs",
    5: "Longest Run",
    6: "Rank",
    7: "FFT",
    8: "Non-overlapping Template",
    9: "Overlapping Template",
    10: "Maurer's Universal",
    11: "Approximate Entropy",
    12: "Random Excursions",
    13: "Random Excursions Variant",
    14: "Serial",
    15: "Linear Complexity"
}

params = {
    "test_id": 1,
    "secNum": "10",
    "secSize": "1000000",
    "blockFreq": "128",
    "blockNon": "9",
    "blockOver": "9",
    "blockApprox": "10",
    "blockSerial": "16",
    "blockLinear": "500"
}

params['test_id'] = 7


command = [
    './assess',
    '--prefix', results_dir,
    '--file', os.path.join(data_dir, data_file),
    '--tests', "",
    '--streams', str(params['secNum']),
    '--blockfreqpar', str(params['blockFreq']),
    '--nonoverpar', str(params['blockNon']),
    '--overpar', str(params['blockOver']),
    '--approxpar', str(params['blockApprox']),
    '--serialpar', str(params['blockSerial']),
    '--linearpar', str(params['blockLinear']),
    '--fileoutput',
    '--binary',
    str(params['secSize'])
]


df = pd.DataFrame(columns=['Test', 'FAST (ms)', 'NORMAL (ms)', 'Speedup (%)'])

start_time = time.time()
for test in nist_test:
    print(f"Executing {nist_test[test]} Test...")
    command[6] = ''.join(['1' if i == test else '0' for i in range(1, 16)])
    output, exec_time_fast = run_assess(fast=True, results_dir=results_dir, data_file=data_file)
    output, exec_time = run_assess(fast=False, results_dir=results_dir, data_file=data_file)
    
    df.loc[len(df)] = [nist_test[test], exec_time_fast, exec_time, ((exec_time - exec_time_fast) / exec_time) * 100 if exec_time else None]

    print(f"{nist_test[test]} FAST execution time (ms): {exec_time_fast:.2f}")
    print(f"{nist_test[test]} NORMAL execution time (ms): {exec_time:.2f}")

fast_total = df["FAST (ms)"].sum()
normal_total = df["NORMAL (ms)"].sum()
speedup_total = df["Speedup (%)"].mean()
df.loc[len(df)] = [
    "Overall time",
    fast_total,
    normal_total,
    speedup_total
]
end_time = time.time()
total_elapsed = end_time - start_time

print(df)
print(f"Total elapsed time for all tests (including overhead): {total_elapsed:.2f} seconds")
df.to_csv("nist_times.csv", index=False)