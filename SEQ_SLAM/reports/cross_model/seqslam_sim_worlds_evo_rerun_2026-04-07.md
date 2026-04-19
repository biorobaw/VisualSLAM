# SeqSLAM Sim Worlds Evo Rerun

Date: 2026-04-07

## Summary

- Re-ran the SeqSLAM evo lane on the current simulator datasets using canonical TUM trajectories.
- City day/night pose CSVs are byte-identical, so the cross-condition city geometry metrics collapse to zero.
- Village day/winter pose CSVs are byte-identical, so the cross-condition village geometry metrics collapse to zero.
- This confirms the TUM conversion + evo tooling still works, but the current simulator pose tracks do not create a non-trivial geometry benchmark.

## Results

| World | Sequence | Kind | GT poses | EST poses | CSV identical | ATE RMSE | RPE trans RMSE | RPE rot RMSE | Artifacts |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- |
| city_sim | city_sim_night_centerline_vs_city_sim_night_centerline | sanity | 364 | 364 | yes | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_sim_night_centerline_vs_city_sim_night_centerline` |
| city_sim | city_sim_day_centerline_vs_city_sim_night_centerline | benchmark | 364 | 364 | yes | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/city_sim_day_centerline_vs_city_sim_night_centerline` |
| village_sim | village_sim_winter_centerline_smooth_vs_village_sim_winter_centerline_smooth | sanity | 1116 | 1116 | yes | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_sim_winter_centerline_smooth_vs_village_sim_winter_centerline_smooth` |
| village_sim | village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth | benchmark | 1116 | 1116 | yes | 0.000000 | 0.000000 | 0.000000 | `SEQ_SLAM/reports/cross_model/pilot/seq_slam/village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth` |

## Pose Hashes

| Sequence | GT SHA1 | EST SHA1 |
| --- | --- | --- |
| city_sim_night_centerline_vs_city_sim_night_centerline | `da92310258450446960f66ba6367b6b3d9542422` | `da92310258450446960f66ba6367b6b3d9542422` |
| city_sim_day_centerline_vs_city_sim_night_centerline | `da92310258450446960f66ba6367b6b3d9542422` | `da92310258450446960f66ba6367b6b3d9542422` |
| village_sim_winter_centerline_smooth_vs_village_sim_winter_centerline_smooth | `2ce31709d9f8ae4c614d0d3a49439631dfa9bddf` | `2ce31709d9f8ae4c614d0d3a49439631dfa9bddf` |
| village_sim_day_centerline_smooth_vs_village_sim_winter_centerline_smooth | `2ce31709d9f8ae4c614d0d3a49439631dfa9bddf` | `2ce31709d9f8ae4c614d0d3a49439631dfa9bddf` |

## Commands

- `evo_ape tum <gt> <est> -a -r full --save_results ... --save_plot ... --plot_mode xyz`
- `evo_rpe tum <gt> <est> -a -r trans_part --save_results ... --save_plot ... --plot_mode xyz`
- `evo_rpe tum <gt> <est> -a -r angle_deg --save_results ... --save_plot ... --plot_mode xyz`
