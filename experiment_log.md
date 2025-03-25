# Archivo de registro de los experimentos

## Instrucciones
1. Ejecutar las pruebas con Fast NIST en el servidor.
2. Empaquetar el directorio experiments en formato tar (experiments<*nn*>.tar)
3. Actualiza el archivo experiments_log.md
4. Copiar el archivo empaquetado al PC en el directorio nist_test y desempaquetar.
5. Ejecutar el script de python.
```bash
python report.py
```
El script genera archivos de gráficos de boxplots en formato PNG para las pruebas (*Others.png*) tiene los gráficos de las que no se encuentren
generadas separadamente.
El script genera el archivo *global_results.csv* con el consolidado de los resultados.
Estos archivos se generan en el directorio *results/experimentsNN* para su posterior análisis. NN es el número asignado al experimento.


## Resultados
### Estructura de archivos:

La carpeta "experiments/AlgorithmTesting" contiene una estructura archivos donde se almacenan los resultados para cada
experimento. Éstos se sobre escriben cada vez que se ejecuta el comando "assesss"

- *finalAnalysisReport.txt:* contiene el reporte general de resultados
- *freq:* contiene los conteos de 1s y 0s para cada una de las secuencias
- *results.txt:* contiene consolidado de los valores del estadístico calculado para cada prueba

Además, una directorio con el nombre de cada prueba, en cada uno de las cuales se identifican los archivos:

- *results.txt:* contiene los valores del estadístico que aplica la prueba en cuestión (generalmente chi2).
                    Si la prueba se ejecuta varias veces, el archivo agrupa los resultados uno por cada linea.
- *stats.txt:* contiene los detalles del cálculo del estadístico que aplica la prueba y el resultado 
                    del p-value. Se evalua el resultado y se registra SUCCESS o FAILURE. Aquí están agrupados
                    los resultados de todas las pruebas en el caso en que la prueba incluya varias etapas, 
                    por ejemplo plantillas o variantes de la prueba.
- *data<nn>.txt:* aparecen solo cuando la prueba se ejecuta múltiples veces. Contiene los resultados del 
                    estadístico calculado en cada prueba.

## Experimentos realizados

|Fecha| Hora| Archivo BIN | Archivo de resultados | Descripción |
|----------|----------|----------|----------|----------|
|12/02/25|10:40|RNDF00.BIN|experiments00.tar|Pruebas NIST sobre un archivo de 2GB, 100 streams, 1000000 bits por stream (solo para probar el programa)|
|12/02/25|11:20|RNDF01.BIN|experiments01.tar|Pruebas NIST sobre un archivo de 1GB, 8000 streams, 1000000 bits por stream. ESP32C3 apagado módulos RF|
|24/02/25|12:15|WRNDF01.BIN|experiments02.tar|Pruebas NIST sobre un archivo de 1GB, 8000 streams, 1000000 bits. ESP32C3 encendido módulos RF|
|25/02/25|15:28|AWRNDF02.BIN|experiments02.tar|Pruebas NIST sobre un archivo de 1GB, 8000 streams, 1000000 bits. ESP32C3 encendido módulos RF en cámara anecoica
----

## Modificaciones realizadas al codigo C de Fast Nist
Se modificó el código fuente original de Fast Nist para poder definir por la línea de comandos, un directorio de salida para los resultados ya que
originalmente, los resultados se guardan en la estructura de directorios a partir del directorio "experiments" que debe estar en el directorio
donde se ejecuta el comando, de lo contrario produce error. El cambio realizado permite especificar un directorio particular para la salida de los 
resultados independientemente desde donde se ejecute el comando assess.
Ahora se dispone del argumento *--prefix <ruta/de/salida>*. En *</ruta/de/salida>* debe estar creada la estructura de directorios tal como se especifica
em el software original NIST-STS y Fast-NIST.

Se incluyeron los cambios en los archivos:
*assess.c*  Se cambio la definición estática "experiments" por *<ruta/de/salida/experiments>* y la llamada a la función *openOutputStreams* con un nuevo argumento *outputDir*
*utils.c* Se cambio la definición estática "experiments" por *<ruta/de/salida/experiments>*
*utils.h* Se actualizó la definicón del prototipo