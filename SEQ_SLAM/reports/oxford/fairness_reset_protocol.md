# SeqSLAM Fairness Reset Protocol (Post-Fix)

Date: 2026-02-26

## Why this reset is required

Matcher bugs were discovered and fixed during experimentation (`pyseqslam/seqslam.py`).
Therefore, results generated before the final fixes are not directly comparable to post-fix results.

## Rules for fair reporting

1. **Pre-fix outputs are exploratory only**
   - Do not mix pre-fix and post-fix rows in the same final table.

2. **Frozen codebase for evaluation**
   - Use the current fixed matcher/evaluator state for all final runs.

3. **Single protocol across pairs**
   - Same command style, same metric fields, same stride policy (`--auto-query-stride` when length mismatch), same artifact format.

4. **Dual-metric interpretation**
   - Coverage: `valid_ratio`, `core_valid_ratio`
   - Alignment: `corr`, `core_corr`, `norm_mae`, `core_norm_mae`
   - A run is only considered strong if both coverage and alignment are acceptable.

5. **Traceability**
   - Every accepted run must have:
     - `tuning_summary.csv`
     - `oxford_tuning_best_matchings.png`
     - report entry with date and protocol context.

## Current post-fix validated runs

See `postfix_validated_summary.csv` in this folder.

## Pending to reach final unbiased study

- Re-run all Oxford Phase-1 rows under this frozen protocol.
- Mark all previously logged pre-fix run-log entries as exploratory archive.
- Publish one consolidated post-fix-only summary table.
