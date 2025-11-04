import os
import numpy as np
import subprocess
import pandas as pd
import io

# ==============================
# CONFIGURACIÓN
# ==============================
NUM_SECUENCES = 10          # Número de secuencias
BITS_PER_SECUENCE = 1_000_000  # Bits por secuencia
PRNG_FILE = "prng_sequence.bin"
TRNG_FILE = "trng_sequence.bin"
NIST_ASSESS_PATH = "./assess"  # Ruta al ejecutable NIST SP800-22

# ==============================
# FUNCIONES DE GENERACIÓN
# ==============================
def generate_prng_file(filename, num_sequences, bits_per_sequence):
    print(f"Generando PRNG en {filename}...")
    with open(filename, "wb") as f:
        for _ in range(num_sequences):
            bits = np.random.randint(0, 2, size=bits_per_sequence, dtype=np.uint8)
            f.write(np.packbits(bits))
    print("PRNG generado.")

def generate_trng_file(filename, num_sequences, bits_per_sequence):
    print(f"Generando TRNG en {filename}...")
    with open(filename, "wb") as f:
        total_bytes = (num_sequences * bits_per_sequence + 7) // 8
        f.write(os.urandom(total_bytes))
    print("TRNG generado.")

# ==============================
# FUNCION PARA EJECUTAR NIST
# ==============================
def run_nist_assess(file_path, prefix="nist_output"):
    output_dir = f"{prefix}_{os.path.splitext(os.path.basename(file_path))[0]}"
    os.makedirs(output_dir, exist_ok=True)
    
    cmd = [
        NIST_ASSESS_PATH,
        "--file", file_path,
        "--prefix", output_dir,
        "--fast",
        "--fileoutput",
        "--binary"
    ]
    
    print(f"Ejecutando NIST SP800-22 en {file_path}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode not in (0, 1):
        print("Error ejecutando NIST:", result.stderr)
        return None
    return output_dir

# ==============================
# FUNCION PARA PROCESAR RESULTADOS
# ==============================
def parse_nist_results(results_dir, nist_tests):
    """
    Extrae resultados de pass/fail para cada prueba desde results.txt
    """
    summary = []
    for test_name in nist_tests:
        print(f"Juan={results_dir}")
        test_file = os.path.join(results_dir, "experiments", "AlgorithmTesting", test_name, "results.txt")
        

        if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            with open(test_file, "r") as f:
                results = [float(line.strip()) for line in f if line.strip()]
            proportion = np.mean([r > 0.01 for r in results])
            summary.append({
                "Test": test_name,
                "PassRate": proportion,
                "Passed": "Yes" if proportion >= 0.99 else "No"
            })
        else:
            summary.append({"Test": test_name, "PassRate": 0.0, "Passed": "No"})
    return pd.DataFrame(summary)

# ==============================
# LISTA DE PRUEBAS
# ==============================
nist_test = [
    "Frequency", "BlockFrequency", "CumulativeSums", 
    "Runs", "LongestRun", "Rank", "FFT", "NonOverlappingTemplate", 
    "OverlappingTemplate", "Universal", "ApproximateEntropy", 
    "RandomExcursions", "RandomExcursionsVariant", "Serial", "LinearComplexity"
]

# ==============================
# SCRIPT PRINCIPAL
# ==============================
if __name__ == "__main__":
    # Generar archivos
    generate_prng_file(PRNG_FILE, NUM_SECUENCES, BITS_PER_SECUENCE)
    generate_trng_file(TRNG_FILE, NUM_SECUENCES, BITS_PER_SECUENCE)

    # Ejecutar NIST
    prng_dir = run_nist_assess(PRNG_FILE, prefix="prng")
    trng_dir = run_nist_assess(TRNG_FILE, prefix="trng")

    # Procesar resultados
    prng_df = parse_nist_results(prng_dir, nist_test)
    trng_df = parse_nist_results(trng_dir, nist_test)

    # Guardar CSV
    prng_df.to_csv("prng_results.csv", index=False)
    trng_df.to_csv("trng_results.csv", index=False)

    # Mostrar resumen comparativo
    print("\n--- RESUMEN PRNG ---")
    print(prng_df)
    print("\n--- RESUMEN TRNG ---")
    print(trng_df)
