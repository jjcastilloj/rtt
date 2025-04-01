```mermaid
graph TD;
    A[Inicio]-->
    B[Generar archivo binario de 2GB con TRNG del ESP32C2]-->
    C[Generar estructura de directorios y archivos de resultados]-->
    D[Ejecutar herramienta assess de Fast NIST-STS]-->
    E[Ejecutar script process_results.py]-->
    F[Generar archivo CSV con resultados]-->
    G[Generar imágenes con boxplots]-->
    H[Fin]
