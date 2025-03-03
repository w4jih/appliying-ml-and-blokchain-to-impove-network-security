import os
import pandas as pd

# Define the mapping of specific labels to "normal" or "malicious"
label_mapping = {
    # Normal traffic
    'normal': 'normal',
    
    # All attack types are mapped to "malicious"
    'apache2': 'malicious',
    'back': 'malicious',
    'land': 'malicious',
    'neptune': 'malicious',
    'mailbomb': 'malicious',
    'pod': 'malicious',
    'processtable': 'malicious',
    'smurf': 'malicious',
    'teardrop': 'malicious',
    'udpstorm': 'malicious',
    'ipsweep': 'malicious',
    'mscan': 'malicious',
    'nmap': 'malicious',
    'portsweep': 'malicious',
    'saint': 'malicious',
    'satan': 'malicious',
    'ftp_write': 'malicious',
    'guess_passwd': 'malicious',
    'imap': 'malicious',
    'multihop': 'malicious',
    'named': 'malicious',
    'phf': 'malicious',
    'sendmail': 'malicious',
    'snmpgetattack': 'malicious',
    'snmpguess': 'malicious',
    'spy': 'malicious',
    'warezclient': 'malicious',
    'warezmaster': 'malicious',
    'xlock': 'malicious',
    'xsnoop': 'malicious',
    'buffer_overflow': 'malicious',
    'httptunnel': 'malicious',
    'loadmodule': 'malicious',
    'perl': 'malicious',
    'ps': 'malicious',
    'rootkit': 'malicious',
    'sqlattack': 'malicious',
    'xterm': 'malicious'
}

def replace_labels(df, label_mapping):
    """
    Replace specific labels in the DataFrame with "normal" or "malicious".
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
directory = os.path.expanduser("~/Downloads/archive")  # Replace with the path to your directory

# Load and process the CSV files
combined_data = load_and_process_csv_files(directory)

# Save the combined and processed data to a new CSV file (optional)
combined_data.to_csv('processed_nsl_kdd_normal_malicious.csv', index=False)

print("Processing complete. Combined data saved to 'processed_nsl_kdd_normal_malicious.csv'.")