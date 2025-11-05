from pathlib import Path
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def compute_torque_frame(df: pd.DataFrame,
                         gear3_teeth: int,
                         gear4_teeth: int,
                         wheel2_radius_m: float) -> pd.DataFrame:
    df = df.copy()

    # Ensure required columns exist
    for col in ("timestamp", "power", "speed"):
        if col not in df.columns:
            df[col] = np.nan if col == "timestamp" else 0.0

    # Time base in seconds
    try:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
        t0 = ts.dropna().min()
        df["time_s"] = (ts - t0).dt.total_seconds()
    except Exception:
        df["time_s"] = np.arange(len(df), dtype=float)

    # Convert speed from mph to m/s (mph * 0.44704 = m/s)
    df["speed_mps"] = pd.to_numeric(df["speed"], errors="coerce").fillna(0.0) * 0.44704
    
    # Power is already in watts
    df["power_w"] = pd.to_numeric(df["power"], errors="coerce").fillna(0.0)

    # Torque at gear 4: (Power_W * Gear4_Teeth * Wheel2_Radius_m) / (Gear3_Teeth * Velocity_mps)
    ratio = (gear4_teeth / float(gear3_teeth)) if gear3_teeth else np.nan
    with np.errstate(divide="ignore", invalid="ignore"):
        df["torque4_nm"] = (df["power_w"] * ratio * wheel2_radius_m) / df["speed_mps"].replace({0.0: np.nan})

    return df


def find_input_csvs(input_root: Path) -> list[Path]:
    csvs: list[Path] = []
    for pilot_dir in sorted([p for p in input_root.iterdir() if p.is_dir()]):
        csvs.extend(sorted(pilot_dir.glob("*.csv")))
    return csvs


def load_config(config_path: Path) -> dict:
    """Load configuration from JSON file."""
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: failed to load config from {config_path}: {e}")
        return {}


def extract_test_type(filename: str) -> str:
    """Extract test type from filename (e.g., '150W', '200W', 'Passive')."""
    filename_lower = filename.lower()
    
    # Check for power levels - handle both "150W" and "150" formats
    if '250' in filename_lower and 'passive' not in filename_lower:
        return '250W'
    elif '200' in filename_lower and 'passive' not in filename_lower:
        return '200W'
    elif '150' in filename_lower and 'passive' not in filename_lower:
        return '150W'
    elif 'passive' in filename_lower:
        return 'Passive'
    else:
        return 'Unknown'


def extract_pilot_short_name(pilot_dir_name: str) -> str:
    """Extract pilot's short name from directory name (e.g., 'AndrewR Tests' -> 'Andrew R')."""
    # Remove 'Tests' and clean up
    name = pilot_dir_name.replace(' Tests', '').strip()
    # If there's a capital letter at the end, add a space before it
    if len(name) > 1 and name[-1].isupper() and name[-2].islower():
        return name[:-1] + ' ' + name[-1]
    return name


def create_comparison_plots(csv_out_dir: Path, output_root_path: Path) -> None:
    """Create comparison plots for each test type showing all pilots."""
    print("\nCreating comparison plots...")
    
    comparison_dir = output_root_path / "comparison_plots"
    comparison_dir.mkdir(parents=True, exist_ok=True)
    
    # Collect all processed CSV files with their metadata
    test_data: dict[str, list[tuple[str, Path]]] = {}  # test_type -> [(pilot_name, csv_path)]
    
    for pilot_dir in sorted([p for p in csv_out_dir.iterdir() if p.is_dir()]):
        pilot_short_name = extract_pilot_short_name(pilot_dir.name)
        for csv_file in sorted(pilot_dir.glob("*.csv")):
            test_type = extract_test_type(csv_file.stem)
            if test_type not in test_data:
                test_data[test_type] = []
            test_data[test_type].append((pilot_short_name, csv_file))
    
    # Create a plot for each test type
    for test_type, pilot_files in sorted(test_data.items()):
        if test_type == 'Unknown':
            continue
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Use a colormap for distinguishing pilots
        colors = plt.cm.tab10(np.linspace(0, 1, len(pilot_files)))
        
        for idx, (pilot_name, csv_path) in enumerate(sorted(pilot_files)):
            try:
                df = pd.read_csv(csv_path)
                # Plot torque vs time for this pilot
                ax.plot(df["time_s"], df["torque4_nm"], 
                       label=pilot_name, color=colors[idx], linewidth=1.5, alpha=0.8)
            except Exception as e:
                print(f"Warning: Failed to plot {csv_path}: {e}")
                continue
        
        ax.set_title(f"{test_type} Test - All Pilots", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time (s)", fontsize=12)
        ax.set_ylabel("Torque at Gear 4 (N·m)", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=10)
        fig.tight_layout()
        
        plot_filename = comparison_dir / f"{test_type}_Test_-_All_Pilots.png"
        fig.savefig(plot_filename, dpi=150)
        plt.close(fig)
        
        print(f"  Created: {plot_filename.name} ({len(pilot_files)} pilots)")


def main() -> int:
    # Load configuration from config.json
    config = load_config(Path("config.json"))
    
    input_root = config.get("input_root", "Power Output Data")
    output_root = config.get("output_root", "outputs")
    gear3_teeth = config.get("gear3_teeth", 24)
    gear4_teeth = config.get("gear4_teeth", 48)
    wheel2_radius_inches = config.get("wheel2_radius_inches", 5.906)
    wheel2_radius_m = wheel2_radius_inches * 0.0254 

    print(f"Configuration: gear3={gear3_teeth} teeth, gear4={gear4_teeth} teeth, wheel2_radius={wheel2_radius_inches} in ({wheel2_radius_m:.4f} m)")

    input_root_path = Path(input_root)
    output_root_path = Path(output_root)
    plots_dir = output_root_path / "plots"
    csv_out_dir = output_root_path / "csv"
    plots_dir.mkdir(parents=True, exist_ok=True)
    csv_out_dir.mkdir(parents=True, exist_ok=True)

    csv_files = find_input_csvs(input_root_path)
    if not csv_files:
        print(f"No CSV files found under {input_root_path}")
        return 1

    summary_records: list[dict] = []

    for csv_path in csv_files:
        pilot_name = csv_path.parent.name
        pilot_plot_dir = plots_dir / pilot_name
        pilot_csv_dir = csv_out_dir / pilot_name
        pilot_plot_dir.mkdir(parents=True, exist_ok=True)
        pilot_csv_dir.mkdir(parents=True, exist_ok=True)

        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"Failed to read {csv_path}: {e}")
            continue

        df_torque = compute_torque_frame(
            df,
            gear3_teeth=gear3_teeth,
            gear4_teeth=gear4_teeth,
            wheel2_radius_m=wheel2_radius_m,
        )

        out_csv = pilot_csv_dir / csv_path.name
        df_torque.to_csv(out_csv, index=False)

        # Generate plot
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_torque["time_s"], df_torque["torque4_nm"], label="Torque 4 (N·m)")
        ax.set_title(f"{pilot_name} — {csv_path.stem}")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Torque at gear 4 (N·m)")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(pilot_plot_dir / f"{csv_path.stem}_torque.png", dpi=150)
        plt.close(fig)

        summary_records.append({
            "pilot": pilot_name,
            "file": str(csv_path.relative_to(input_root_path)),
            "out_csv": str(out_csv.relative_to(output_root_path)),
            "torque_median_nm": float(np.nanmedian(df_torque["torque4_nm"].values)),
            "torque_max_nm": float(np.nanmax(df_torque["torque4_nm"].values)),
        })

    summary_df = pd.DataFrame(summary_records)
    summary_csv = output_root_path / "summary.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"Wrote {len(summary_records)} results. Summary: {summary_csv}")
    
    # Create comparison plots
    create_comparison_plots(csv_out_dir, output_root_path)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


