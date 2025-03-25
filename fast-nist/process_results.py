import numpy as np
import pandas as pd
import os
import glob
from scipy.stats import ks_1samp, uniform, chisquare
import matplotlib.pyplot as plt
import seaborn as sns

alfa = 0.01
nbits = "1.000.000"
results_dir = "results/urandom/"

base_dir = "experiments/AlgorithmTesting/"
tests_results = pd.DataFrame() # Dataframe to store the result of test with only 1 result
nist_data = pd.DataFrame() # Dataframe to store all results for all tests (process with other tools such as Matlab)

# define the NIST tests and their corresponding number of variants. The tests with numbers > 1 should be process as special test
nist_tests = {
                "Frequency": 1, "BlockFrequency": 1, "CumulativeSums": 2, 
                "Runs": 1, "LongestRun": 1, "Rank": 1, "FFT": 1, "NonOverlappingTemplate": 148, 
                "OverlappingTemplate" : 1, "Universal" : 1, "ApproximateEntropy" : 1, 
                "RandomExcursions" : 8, "RandomExcursionsVariant" : 18, "Serial" : 2, "LinearComplexity": 1
            }

# Goodness of fit test
def fit_test(data_column: pd.Series):
   
    data_column = data_column[data_column > 0]
    pass_rate = 0.99 - 3.0 * np.sqrt(0.01 * (1.0 - alfa) / (len(data_column)))  # From NIST-STS code
    pass_rate = round(pass_rate, 6)
    F, _ = np.histogram(data_column, bins=np.linspace(0, 1, 11))
    expected = np.full(F.shape, F.sum() / F.size, dtype=np.float64)
   
    _, chi2_p_value = chisquare(F, expected)
    _, ks_p_value = ks_1samp(data_column, uniform.cdf)
    chi2_p_value = round(chi2_p_value, 6)
    ks_p_value = round(ks_p_value,6)
    pass_count = (data_column > alfa).sum()
    proportion = pass_count / len(data_column)
    proportion = round(proportion, 4)
    data_size = len(data_column)
    result = "PASS" if proportion > pass_rate else "FAIL"
    
    return chi2_p_value, ks_p_value, pass_count, data_size, proportion, pass_rate, result

def draw_boxplot2(data, msg):
    
    data.boxplot()
    plt.ylabel('P-Value')
    plt.title('Distribución de resultados prueba NIST SP-800 para ' + msg)
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()


def draw_boxplot(data, msg, filename):

    fig, ax = plt.subplots(figsize=(8, 6))
    data.boxplot(ax=ax, patch_artist=True, 
                 boxprops=dict(facecolor='lightblue', color='blue'),
                 whiskerprops=dict(color='green', linewidth=1.5),
                 capprops=dict(color='red', linewidth=2),
                 flierprops=dict(marker='o', color='purple', markersize=5))

    ax.set_ylabel('P-Value', fontsize=12)
    ax.set_title('Distribución de resultados prueba NIST SP-800 para' + msg, fontsize=12)

    plt.xticks(rotation=45, fontsize=10)
    
    ax.grid(True, which='both', axis='y', color='gray', linestyle='--', linewidth=0.5)
    ax.minorticks_on()  
    ax.grid(True, which='minor', axis='y', color='gray', linestyle=':', linewidth=0.5)
    ax.tick_params(axis='y', which='minor', length=4, width=1, direction='in', grid_color='gray', grid_alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    #plt.show()
    
#####################################################
####                 Main Program                ####
#####################################################

os.makedirs(results_dir, exist_ok=True) # Create results directory

for test_name, num_tests in nist_tests.items():
    
    # Process fot test with single results
    if num_tests == 1:

        results_file = "/results.txt"
        file_name = base_dir + test_name + results_file
        results = []

        with open(file_name, 'r') as file: 
            for line in file:
                results.append(float(line.strip()))

        test_data = pd.DataFrame(results)
        test_data.columns = ['p-value']  
        nist_data[test_name] = test_data

        tests_results[test_name] = fit_test(test_data['p-value'])
        
    # Process for test with multiple results
    else: 
        dir_name = base_dir + test_name
        data_files = glob.glob(os.path.join(dir_name, "data*"))
        data_set = pd.DataFrame() # To store individual results of each special test (Data source for the boxplots and fit of goodness test)
       
        for file_name in data_files:
            df = pd.read_csv(file_name, header=None)
            data_set = pd.concat([data_set, df], axis=1)

        data_set = data_set[data_set != 0]
        data_set.columns = range(1, len(data_set.columns) + 1)

        stacked_dataset = data_set.stack().reset_index(drop=True) # To store consolidate results of each test (Data source for calculate global p-value of p-values)

        tests_results[test_name] = fit_test(stacked_dataset)
            
        if len(data_set.columns) > 20: # Avoid boxplot graphic saturation, extract only the firs 20 groups as representative data
            representative_groups = [i for i in range(1, 21)]
            data_set = data_set[representative_groups]
        
        png_file = test_name + ".png"
       
        draw_boxplot(data_set, f"\n{test_name}, {len(data_set)} muestras de {nbits} bits c/u", results_dir + test_name + ".png")

global_results = tests_results.T
global_results.index.name = "Test"
global_results.columns = ['Chi2 P-Value', 'KS P-Value', 'Aproved', 'Total', 'Proportion', 'Pass rate', 'Global result']
global_results.to_csv(results_dir + "global_results.csv")

draw_boxplot(nist_data, f"\npruebas de un solo resultado, {len(data_set)} muestras de {nbits} bits c/u", results_dir + "Others.png")
print(global_results)


