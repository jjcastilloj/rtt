## Pruebas NIST más relevantes para una primera aproximación

| **Prueba** | **Qué mide** | **Comentario** |
|-------------|--------------|----------------|
| **Frequency** | Distribución de 0 y 1 | Mide si hay aproximadamente la misma cantidad de 0s y 1s. Fundamental y rápida. |
| **Block Frequency** | Distribución en bloques | Detecta desequilibrios locales de bits dentro de bloques. |
| **Runs** | Longitud de secuencias consecutivas | Evalúa si hay demasiadas o muy pocas secuencias consecutivas de un mismo bit. |
| **Longest Run** | Longitud de la secuencia más larga | Detecta patrones anómalos en secuencias largas de 0 o 1. |
| **Cumulative Sums (Cusum)** | Desviaciones acumuladas | Mide tendencias en la secuencia, útil para detectar “sesgos” ocultos. |
| **Approximate Entropy** | Complejidad y repetición de patrones | Detecta patrones repetitivos que no aparecen en pruebas simples. |

---

### Recomendación de parámetros para una primera evaluación

- **Número de secuencias (`secNum`)**: 10–20  
  (Más secuencias aumentan la confiabilidad estadística pero también el tiempo de ejecución.)

- **Tamaño de cada secuencia (`secSize`)**: entre 1 millón y 10 millones de bits.  

#### Ejemplo sugerido
```python
secNum = 10           # 10 secuencias por prueba
secSize = 1_000_000   # 1 millón de bits por secuencia
