# Power Rig Torque Analysis

Computes torque at gear 4 from power rig test data using the formula:

```
Torque_4 = (Power_watts × Gear4_Teeth × Wheel2_Radius_m) / (Gear3_Teeth × Velocity_mps)
```

![image alt](https://github.com/VT-HPS/2025-Power-Output-/blob/7793e05e1850e8cdb78ebdf6d580788291aa8441/Equations%20for%20RAY!!!!.pdf)

Input data is assumed to have:
- **Speed** in mph (automatically converted to m/s)
- **Power** in watts


## Configuration

Edit `config.json` to set your rig parameters:

```json
{
  "gear3_teeth": 20,
  "gear4_teeth": 34,
  "wheel2_radius_inches": 12.75
}
```

- **gear3_teeth**: Number of teeth on gear 3
- **gear4_teeth**: Number of teeth on gear 4  
- **wheel2_radius_inches**: Radius of wheel 2 in inches (automatically converted to meters)

## Usage

Simply edit `config.json` with your rig parameters, then run:
```bash
python compute_torque.py
```

## Output

- **CSV files with torque column**: `outputs/csv/<Pilot>/<File>.csv`
- **Torque vs time plots**: `outputs/plots/<Pilot>/<File>_torque.png`
- **Comparison plots**: `outputs/comparison_plots/<File>_All_Pilots.png`
- **Summary**: `outputs/summary.csv`

The script adds these columns to each CSV:
- `time_s`: Time in seconds from start
- `speed_mps`: Speed converted to m/s
- `power_w`: Power in watts
- `torque4_nm`: Torque at gear 4 in N·m

## Comparison Plots

To compare multiple pilots on the same graph, use the comparison script:

