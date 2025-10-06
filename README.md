# pyH2A - Forked to Add Feature

- **PyPI:** [https://pypi.org/project/pyH2A](https://pypi.org/project/pyH2A)  
- **Docs:** [https://pyh2a.readthedocs.io](https://pyh2a.readthedocs.io)  
- **Source:** [https://github.com/jschneidewind/pyH2A](https://github.com/jschneidewind/pyH2A)  

---

## General Optimization

This fork adds a **general-purpose optimization module** to minimize **Levelized Cost of Hydrogen (LCOH)** by adjusting parameters within bounds.

- Uses **`scipy.optimize.differential_evolution`**  
- Logs each iteration’s parameter values and hydrogen cost  
- Saves results to a tab-delimited file

---

## Test

Input file: `data/PV_E/Base/PV_E_Base.md`  

Run example:

```bash
python Example_Run/pyH2A_take_home_run.py
```

## Main Feature

```bash
result = differential_evolution(
    self.objective_function,
    bounds=[(p['Values'][0], p['Values'][1]) for p in self.parameters.values()],
    strategy='best1bin',
    maxiter=self.n_iter,
    popsize=self.pop_size,
    workers=1,
    seed=42,
    disp=True,
    polish=True
)
```

This module performs global optimization to minimize the Levelized Cost of Hydrogen (LCOH). It varies specified input parameters within their bounds, evaluates the hydrogen cost using the Discounted_Cash_Flow model, and uses differential evolution to find the optimal set of parameters. Results are logged and saved for analysis.

## Input Parameter:

# General_Optimization_Analysis

Name | Value | Comment
--- | --- | ---
Max Iterations | 50 | Maximum iterations for optimization
Population Size | 15 | Differential evolution population size
Output File | data/PV_E/Base/general_optimizer_output.csv

# Parameters - General_Optimization_Analysis

Parameter | Name | Type | Values | File Index | Comment
--- | --- | --- | --- | --- | --- 
Photovoltaic > Nominal Power (kW) > Value | kW(PV) | value | 0.5; 4.0 | 0 | Common value range.



