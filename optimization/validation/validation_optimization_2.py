import os
import numpy as np
import pandas as pd
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from optimization.optimization_2_connector_allocation import (
    load_regional_data,
    solve_connector_allocation,
    proportional_baseline,
    validate_solution,
    validate_budget_sensitivity,
    DATA_PATH
)

REPORT_PATH = Path(__file__).parent / "optimization_2_validation_results.md"

df, regional_df = load_regional_data(DATA_PATH)

report_lines = []
report_lines.append("# Optimization 2 Validation Results\n")
report_lines.append("## A. Configuration\n")

total_records = len(df)
valid_records = df['state'].notna().sum()
missing_records = df['state'].isna().sum()

report_lines.append(f"- **Dataset**: ev_stations_2025.csv")
report_lines.append(f"- **Total Dataset Records**: {total_records:,}")
report_lines.append(f"- **Records with Valid State (Included)**: {valid_records:,}")
report_lines.append(f"- **Records with Missing State (Excluded)**: {missing_records:,}")
report_lines.append(f"- **Decision Variable**: Integer additional connectors allocated to each state")
report_lines.append("- **Solver**: `scipy.optimize.milp`\n")

all_passed = True
def record(val):
    global all_passed
    if not val:
        all_passed = False
    return "PASS" if val else "FAIL"

report_lines.append("## B. Budget Sensitivity & Monotonicity (Min-CPS)\n")
budgets = [100, 250, 500, 750, 1000]
sensitivity_table, monotonic = validate_budget_sensitivity(regional_df, budgets)

report_lines.append("| Budget | Minimum CPS | Total Allocated | Constraints Passed |")
report_lines.append("|---:|---:|---:|---|")
for _, row in sensitivity_table.iterrows():
    budget = int(row['budget'])
    min_cps = row['minimum_cps']
    total_alloc = int(row['total_allocated'])
    c_pass = row['all_checks_pass']
    if not c_pass: all_passed = False
    report_lines.append(f"| {budget} | {min_cps:.6f} | {total_alloc} | {record(c_pass)} |")

report_lines.append(f"\nMonotonicity Check (Min-CPS increases with Budget): **{record(monotonic)}**\n")

report_lines.append("## C. Baseline Comparison (Proportional vs. Optimized)\n")
report_lines.append("Testing across all budgets:\n")
report_lines.append("| Budget | Proportional Baseline Min CPS | Optimized Min CPS | Improved? |")
report_lines.append("|---:|---:|---:|---|")

baseline_pass = True
for budget in budgets:
    opt_res = solve_connector_allocation(regional_df, budget)
    base_res = proportional_baseline(regional_df, budget)
    
    opt_cps = opt_res['minimum_cps']
    base_cps = base_res['final_cps'].min()
    improved = opt_cps >= base_cps - 1e-9  # Handle floating point
    if not improved: baseline_pass = False
    
    report_lines.append(f"| {budget} | {base_cps:.6f} | {opt_cps:.6f} | {record(improved)} |")

report_lines.append(f"\nOptimization performs >= Baseline across all budgets: **{record(baseline_pass)}**\n")

report_lines.append("## D. Detailed Constraint Validation (Budget = 500)\n")
budget_500_res = solve_connector_allocation(regional_df, 500)
checks, indep_cps = validate_solution(budget_500_res)

for k, v in checks.items():
    report_lines.append(f"- **{k}**: {record(v)}")

report_lines.append("\n## E. Overall Verdict\n")
if all_passed:
    report_lines.append("```text\nOptimization 2 Validation Status: PASS\n```\n")
else:
    report_lines.append("```text\nOptimization 2 Validation Status: FAIL\n```\n")

with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write("\n".join(report_lines))

print(f"Optimization 2 Validation Status: {'PASS' if all_passed else 'FAIL'}")
