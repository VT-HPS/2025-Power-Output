# Power Rig Torque Analysis

Computes torque at gear 4 from power rig test data using the formula:

```
Torque_4 = (Power_watts × Gear4_Teeth × Wheel2_Radius_m) / (Gear3_Teeth × Velocity_mps)
```

Input data is assumed to have:
- **Speed** in mph (automatically converted to m/s)
- **Power** in watts

## Setup

```bash
pip install -r requirements.txt
```

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
- **Summary**: `outputs/summary.csv`

The script adds these columns to each CSV:
- `time_s`: Time in seconds from start
- `speed_mps`: Speed converted to m/s
- `power_w`: Power in watts
- `torque4_nm`: Torque at gear 4 in N·m

## Comparison Plots

To compare multiple pilots on the same graph, use the comparison script:

```bash
python plot_comparison.py
```

Edit `comparison_config.json` to define which pilots to compare:

```json
{
  "comparisons": [
    {
      "title": "150W Test - All Pilots",
      "test_type": "150",
      "pilots": [
        "AndrewR Tests",
        "AshleyW Tests",
        "ChaimG Tests"
      ]
    },
    {
      "title": "Andrew - All Tests",
      "test_type": "",
      "pilots": [
        {"name": "AndrewR Tests", "label": "Andrew 150W"},
        {"name": "AndrewR Tests", "label": "Andrew 200W"}
      ]
    }
  ]
}
```

- **title**: Name for the comparison plot
- **test_type**: Filter tests by name (e.g., "150", "200", "passive"). Leave empty `""` to manually specify tests.
- **pilots**: List of pilot names, or objects with `name` and custom `label`

Comparison plots are saved to: `outputs/comparison_plots/`

