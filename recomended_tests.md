## Most Relevant NIST Tests for a First Approach

| **Test** | **What it Measures** | **Comment** |
|-------------|--------------|----------------|
| **Frequency** | Distribution of 0s and 1s | Measures if there is approximately the same amount of 0s and 1s. Fundamental and fast. |
| **Block Frequency** | Distribution in blocks | Detects local bit imbalances within blocks. |
| **Runs** | Length of consecutive sequences | Evaluates whether there are too many or too few consecutive sequences of the same bit. |
| **Longest Run** | Length of the longest sequence | Detects anomalous patterns in long sequences of 0s or 1s. |
| **Cumulative Sums (Cusum)** | Cumulative deviations | Measures trends in the sequence, useful for detecting hidden "biases". |
| **Approximate Entropy** | Complexity and pattern repetition | Detects repetitive patterns that do not appear in simple tests. |

---

### Parameter Recommendation for a First Evaluation

- **Number of sequences (`secNum`)**: 10–20  
  (More sequences increase statistical reliability but also execution time.)

- **Size of each sequence (`secSize`)**: between 1 million and 10 million bits.  

#### Suggested Example
```python
secNum = 10           # 10 sequences per test
secSize = 1_000_000   # 1 million bits per sequence
