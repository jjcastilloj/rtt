def text_to_binary(input_file, output_file):
    with open(input_file, 'r') as txt_file:
        binary_sequence = txt_file.read().strip().replace(" ", "")  # Leer y limpiar espacios

    with open(output_file, 'wb') as bin_file:
        byte_array = bytearray(int(binary_sequence[i:i+8], 2) for i in range(0, len(binary_sequence), 8))
        bin_file.write(byte_array)

if __name__ == "__main__":
    input_filename = "sequence.txt"  # Nombre del archivo de texto
    output_filename = "sequence.bin"  # Nombre del archivo binario
    text_to_binary(input_filename, output_filename)
    print(f"Archivo binario '{output_filename}' generado correctamente.")
