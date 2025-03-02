"""import os
import pandas as pd

# Define the label mapping
label_mapping = {
    "back": "DoS", "land": "DoS", "neptune": "DoS", "mailbomb": "DoS",
    "pod": "DoS", "processtable": "DoS", "smurf": "DoS", "teardrop": "DoS", "udpstorm": "DoS",
    "ipsweep": "Probe", "mscan": "Probe", "nmap": "Probe", "portsweep": "Probe",
    "saint": "Probe", "satan": "Probe",
    "ftp_write": "R2L", "guess_passwd": "R2L", "imap": "R2L", "multihop": "R2L",
    "named": "R2L", "phf": "R2L", "sendmail": "R2L", "snmpgetattack": "R2L",
    "snmpguess": "R2L", "spy": "R2L", "warezclient": "R2L", "warezmaster": "R2L",
    "xlock": "R2L", "xsnoop": "R2L",
    "buffer_overflow": "U2R", "httptunnel": "U2R", "loadmodule": "U2R", "perl": "U2R",
    "ps": "U2R", "rootkit": "U2R", "sqlattack": "U2R", "xterm": "U2R"
}

# Directory containing CSV files
input_directory = os.path.expanduser("~/Desktop/pfa/NSL-KDD-Network-Intrusion-Detection/")
output_file = "merged_updated_dataset.csv"

def process_csv_files(input_directory, output_file):
    all_dataframes = []
    
    # Loop through all CSV files in the directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(input_directory, filename)
            df = pd.read_csv(file_path)
            
            # Check if 'label' column exists
            if 'label' in df.columns:
                df['label'] = df['label'].replace(label_mapping)  # Update labels
            
            all_dataframes.append(df)
    
    # Merge all dataframes
    merged_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Save the updated dataset
    merged_df.to_csv(output_file, index=False)
    print(f"Merged dataset saved as {output_file}")

# Run the function
process_csv_files(input_directory, output_file)
"""

import os
import pandas as pd

# Define the mapping of specific labels to their corresponding categories
label_mapping = {
    # DoS attacks
    'apache2': 'DoS',
    'back': 'DoS',
    'land': 'DoS',
    'neptune': 'DoS',
    'mailbomb': 'DoS',
    'pod': 'DoS',
    'processtable': 'DoS',
    'smurf': 'DoS',
    'teardrop': 'DoS',
    'udpstorm': 'DoS',
    
    # Probe attacks
    'ipsweep': 'Probe',
    'mscan': 'Probe',
    'nmap': 'Probe',
    'portsweep': 'Probe',
    'saint': 'Probe',
    'satan': 'Probe',
    
    # R2L attacks
    'ftp_write': 'R2L',
    'guess_passwd': 'R2L',
    'imap': 'R2L',
    'multihop': 'R2L',
    'named': 'R2L',
    'phf': 'R2L',
    'sendmail': 'R2L',
    'snmpgetattack': 'R2L',
    'snmpguess': 'R2L',
    'spy': 'R2L',
    'warezclient': 'R2L',
    'warezmaster': 'R2L',
    'xlock': 'R2L',
    'xsnoop': 'R2L',
    
    # U2R attacks
    'buffer_overflow': 'U2R',
    'httptunnel': 'U2R',
    'loadmodule': 'U2R',
    'perl': 'U2R',
    'ps': 'U2R',
    'rootkit': 'U2R',
    'sqlattack': 'U2R',
    'xterm': 'U2R'
}

def replace_labels(df, label_mapping):
    """
    Replace specific labels in the DataFrame with their corresponding categories.
    """
    df['labels'] = df['labels'].replace(label_mapping)
    return df

def load_and_process_csv_files(directory):
    """
    Load all CSV files in the given directory, process the labels, and return a combined DataFrame.
    """
    all_data = pd.DataFrame()  # To store combined data
    
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory, filename)
            print(f"Loading file: {file_path}")
            
            # Load the CSV file
            df = pd.read_csv(file_path)
            
            # Replace labels
            df = replace_labels(df, label_mapping)
            
            # Append to the combined DataFrame
            all_data = pd.concat([all_data, df], ignore_index=True)
    
    return all_data

# Directory containing the CSV files
directory = os.path.expanduser("~/Downloads/archive")  # #Replace with the path to your #directory

# Load and process the CSV files
combined_data = load_and_process_csv_files(directory)

# Save the combined and processed data to a new CSV file (optional)
combined_data.to_csv('processed_nsl_kdd.csv', index=False)

print("Processing complete. Combined data saved to 'processed_nsl_kdd.csv'.")