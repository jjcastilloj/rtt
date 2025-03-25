import os
import subprocess
import time
import multiprocessing
import sys

# Directorios de entrada y salida
DATA_DIR = "input_data/250204"
OUTPUT_DIR = "results/250204"

# Crear el directorio de resultados si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Lista de archivos a procesar
files = [f for f in os.listdir(DATA_DIR) if f.startswith("RNDF") and f.endswith(".BIN")]

def run_test(command, test_name, filename, result_file):
    """Ejecuta un comando y guarda su salida en el archivo de resultados y en pantalla en tiempo real."""
    start_time = time.time()
    try:
        with open(result_file, "a") as f:
            f.write(f"\n--- {test_name} ---\n")
            f.write(f"Ejecutando: {command}\n")
        
        # Mostrar en pantalla que se está ejecutando la prueba
        print(f"Ejecutando prueba: {test_name} sobre {filename}...")

        # Ejecutar el comando y leer la salida en tiempo real
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        # Leer y mostrar la salida línea por línea mientras se ejecuta el comando
        with process.stdout:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')  # Imprimir la línea en pantalla
                sys.stdout.flush()  # Forzar el vaciado del buffer en pantalla (especialmente para Windows)
                with open(result_file, "a") as f:
                    f.write(line)  # Guardar la línea en el archivo de resultados

        process.wait()  # Esperar a que termine el proceso

        elapsed_time = time.time() - start_time
        print(f"Tiempo de ejecución de {test_name} para {filename}: {elapsed_time:.2f} segundos.")
        with open(result_file, "a") as f:
            f.write(f"\nTiempo de ejecución: {elapsed_time:.2f} segundos\n")
    except Exception as e:
        with open(result_file, "a") as f:
            f.write(f"\nError en {test_name}: {e}\n")
        print(f"Error en {test_name} para {filename}: {e}")

def process_file(filename):
    """Ejecuta las pruebas sobre un archivo de números aleatorios."""
    filepath = os.path.join(DATA_DIR, filename)
    result_file = os.path.join(OUTPUT_DIR, f"{filename[:-4]}_results.txt")

    print(f"\nProcesando {filename}...")

    #commands = [(f"python sp800_22_tests/sp800_22_tests.py {filepath}", "SP800-22", result_file)]

    commands = [
        (f"python sp800_22_tests/sp800_22_tests.py {filepath}", "SP800-22", os.path.join(OUTPUT_DIR, f"{filename[:-4]}_sp80022.txt")),
        (f"dieharder -a -g 201 -f {filepath}", "Dieharder", os.path.join(OUTPUT_DIR, f"{filename[:-4]}_dieharder.txt")),
        (f"ent {filepath}", "Ent", os.path.join(OUTPUT_DIR, f"{filename[:-4]}_ent.txt"))
    ]

    # Ejecutar pruebas en paralelo utilizando multiprocessing
    for cmd, name, res_file in commands:
        
        run_test(cmd, name, filename, res_file)

if __name__ == "__main__":
    # Crear un pool de procesos para ejecutar las pruebas en paralelo
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        pool.map(process_file, files)

    print("\nTodas las pruebas han sido completadas.")
  


