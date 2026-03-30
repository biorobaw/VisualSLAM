# Phase 2 Converter Task Board

Date: 2026-03-29

## Objective

Track converter implementation per SLAM model into canonical TUM format.

## Global converter requirements

- Input parser documented
- Output format: `timestamp tx ty tz qx qy qz qw`
- Monotonic timestamp check
- NaN/Inf rejection
- Quaternion normalization check
- Non-zero exit on invalid output

## ORB_SLAM

- Owner: TBD
- Native output identified: [ ]
- Parser implemented: [ ]
- Validation checks pass: [ ]
- Sample output produced: [ ]
- Ready for evo pilot: [ ]

## RAT_SLAM

- Owner: TBD
- Native output identified: [ ]
- Parser implemented: [ ]
- Validation checks pass: [ ]
- Sample output produced: [ ]
- Ready for evo pilot: [ ]

## SEQ_SLAM

- Owner: TBD
- Native output identified: [ ]
- Parser implemented: [ ]
- Validation checks pass: [ ]
- Sample output produced: [ ]
- Ready for evo pilot: [ ]

## Integration gate

Move to full evo pilot only after all models produce at least one validated canonical trajectory file.
