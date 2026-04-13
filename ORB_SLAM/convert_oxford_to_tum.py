import argparse
import pandas as pd
from scipy.spatial.transform import Rotation
import numpy as np

def convert_oxford_to_tum(input_csv, output_tum):
    """
    Convert Oxford RobotCar ground truth (ins.csv) to TUM format.
    Input format: timestamp, northing, easting, down, roll, pitch, yaw
    Output format: timestamp tx ty tz qx qy qz qw
    """
    try:
        # The Oxford ins.csv has no header by default in some versions, but standard Oxford SDK format is:
        # timestamp, ins_status, latitude, longitude, altitude, northing, easting, down, utm_zone, roll, pitch, yaw
        df = pd.read_csv(input_csv)
        
        # Strip whitespace from column names if present
        df.columns = df.columns.str.strip()
        
        # Check required columns
        required_cols = ['timestamp', 'northing', 'easting', 'down', 'roll', 'pitch', 'yaw']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            # If no header is present, assume columns based on standard SDK format
            print(f"Warning: Missing headers {missing}. Attempting to process assuming standard layout...")
            df = pd.read_csv(input_csv, header=None)
            # Assuming standard 12 column format:
            # 0:timestamp, 1:ins_status, 2:lat, 3:lon, 4:alt, 5:northing, 6:easting, 7:down, 8:utm_zone, 9:roll, 10:pitch, 11:yaw
            df = df.rename(columns={
                0: 'timestamp',
                5: 'northing',
                6: 'easting',
                7: 'down',
                9: 'roll',
                10: 'pitch',
                11: 'yaw'
            })
            
        with open(output_tum, 'w') as f:
            for _, row in df.iterrows():
                # Timestamp in microseconds -> seconds
                timestamp = row['timestamp'] / 1e6
                
                # Translation: Easting (x), Northing (y), -Down (z, altitude upwards) or just use exactly what is mapped.
                # Standard TUM is tx, ty, tz. 
                # Let's map Easting -> tx, Northing -> ty, -Down -> tz (Up)
                tx = row['easting']
                ty = row['northing']
                tz = -row['down']
                
                # Rotation: Euler (roll, pitch, yaw) -> Quaternion
                # Oxford uses standard roll, pitch, yaw (XYZ) but check convention.
                # Typically ZYX or XYZ. We use 'xyz' or 'ZYX' intrinsic.
                r = Rotation.from_euler('xyz', [row['roll'], row['pitch'], row['yaw']], degrees=False)
                qx, qy, qz, qw = r.as_quat()
                
                f.write(f"{timestamp:.6f} {tx:.6f} {ty:.6f} {tz:.6f} {qx:.6f} {qy:.6f} {qz:.6f} {qw:.6f}\n")
                
        print(f"Successfully converted {input_csv} to {output_tum}")
        
    except Exception as e:
        print(f"Error converting {input_csv}: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Oxford ins.csv to TUM trajectory format.')
    parser.add_argument('input_csv', help='Path to input ins.csv')
    parser.add_argument('output_tum', help='Path to output .tum file')
    args = parser.parse_args()
    
    convert_oxford_to_tum(args.input_csv, args.output_tum)
