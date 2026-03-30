# Cross-Model Results Files Guide

To avoid confusion between validation runs and real benchmark runs, results are split into separate files:

- Sanity checks only:
  - SEQ_SLAM/reports/cross_model/cross_model_sanity_results.csv
- Benchmark/non-trivial runs only:
  - SEQ_SLAM/reports/cross_model/cross_model_benchmark_results.csv
- Empty row template for future new entries:
  - SEQ_SLAM/reports/cross_model/cross_model_results_template.csv

Rule:

- If GT and EST are intentionally identical to test pipeline integrity, write to `cross_model_sanity_results.csv`.
- If GT and EST are a true comparison pair, write to `cross_model_benchmark_results.csv`.
