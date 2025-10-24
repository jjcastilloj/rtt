# Archivo de registro de los experimentos

## Instrucciones
1. Ejecutar las pruebas con Fast NIST en el servidor tomando como archivo de origen el producido por el generador.
2. El archivo *test.sh* permite definir los parámetros de la ejecución del comando *assess* que ejecuta las pruebas.
3. Una vez finalizada la prueba, empaquetar el directorio experiments en formato tar (experiments<*nn*>.tar)
4. Actualizar el archivo experiments_log.md para llevar el registro de detalles del experimento.
5. Copiar el archivo empaquetado al PC en el directorio fast-nist y desempaquetar (se sobreescribirá todo el contenido del directorio *experiments*).
6. Modificar las variables del script process_results.py:
nbits = "1.000.000" # Número de bits por secuencia (solo informativo para los reportes, el número real se especifica en *tests.sh* y deben coincidir)
results_dir = "results/experiments00/" # Se debe modificar el directorio donde se almacenarán los resultados del experimento, en este caso *results/experiments00*
Ejecutar el script de python.
```bash
python process_results.py
```
El script genera el archivo *Others.png* con los boxplots para las pruebas que tienen un solo resultado. Para las pruebas
que tienen mas de un resultado, se genera un archivo de boxplot con el nombre de la prueba.
El script genera el archivo *global_results.csv* con el consolidado de los resultados.
Estos archivos se generan en el directorio *results/experimentsNN* para su posterior análisis. NN es el número asignado al experimento.


## Resultados
### Estructura de archivos:

La carpeta "experiments/AlgorithmTesting" contiene una estructura archivos donde se almacenan los resultados para cada
experimento. Éstos se sobre escriben cada vez que se ejecuta el comando "assesss" mediante "test.sh"

- *finalAnalysisReport.txt:* contiene el reporte general de resultados
- *freq:* contiene los conteos de 1s y 0s para cada una de las secuencias
- *results.txt:* contiene consolidado de los valores del estadístico calculado para cada prueba

Además un directorio con el nombre de cada prueba, en cada uno de los cuales se identifican los archivos:

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
|12/02/25|11:20|RNDF01.BIN|experiments01.tar|Pruebas NIST sobre un archivo de 1GB, 8000 streams, 1000000 bits por stream. ESP32C3 encendido módulos RF con saturación|
|24/02/25|12:15|WRNDF01.BIN|experiments02.tar|Pruebas NIST sobre un archivo de 1GB, 8000 streams, 1000000 bits. ESP32C3 encendido módulos RF en condiciones normales
|25/02/25|15:28|AWRNDF02.BIN|experiments02.tar|Pruebas NIST sobre un archivo de 1GB, 8000 streams, 1000000 bits. ESP32C3 encendido módulos RF en cámara anecoica
----

## Modificaciones realizadas al codigo C de Fast Nist
Se modificó el código fuente original de Fast Nist para poder definir por la línea de comandos un directorio de salida para los resultados ya que
originalmente, los resultados se guardan en la estructura de directorios a partir del directorio "experiments" que debe estar en el directorio
donde se ejecuta el comando, de lo contrario produce error. El cambio realizado permite especificar un directorio particular para la salida de los 
resultados independientemente desde donde se ejecute el comando assess.
Ahora se dispone del argumento *--prefix <ruta/de/salida>*. En *</ruta/de/salida>* debe estar creada la estructura de directorios tal como se especifica
em el software original NIST-STS y Fast-NIST.

Se incluyeron los cambios en los archivos:
*assess.c*  Se cambio la definición estática "experiments" por *<ruta/de/salida/experiments>* y la llamada a la función *openOutputStreams* con un nuevo argumento *outputDir*
*utils.c* Se cambio la definición estática "experiments" por *<ruta/de/salida/experiments>*
*utils.h* Se actualizó la definicón del prototipo

## Para tener en cuenta

La aplicación **Python Flask** se ejecuta mediante **Gunicorn**, el cual se hace disponible para la aplicación cuando se activa el entorno virtual `env-nist-test` con el siguiente comando:

```bash
source env-nist-test/bin/activate
```

Gunicorn se ejecuta bajo **systemd** con el módulo ubicado en:

```
/etc/systemd/system/rtt.service
```

Puedes iniciar o detener el servicio con los comandos:

```bash
sudo systemctl start rtt
sudo systemctl stop rtt
```

---

### Código del archivo `rtt.service`

```ini
[Unit]
Description=Gunicorn instance to serve NIST Tests
After=network.target

[Service]
User=jcastillo
Group=jcastillo
WorkingDirectory=/opt/web_app
ExecStart=/home/jcastillo/nist/env-nist-tests/bin/gunicorn -k gthread --workers=8 --threads=8 --timeout=360 --bind 0.0.0.0:8000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```
