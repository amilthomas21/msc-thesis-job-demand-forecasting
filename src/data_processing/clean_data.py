import pandas as pd
import os

def clean_master_dataset():
    input_path = 'data/processed/master_jobs.csv'
    output_path = 'data/processed/master_jobs_clean.csv'
    
    df = pd.read_csv(input_path)
    print(f'Before cleaning: {df.shape}')
    
    # Drop missing descriptions
    df = df.dropna(subset=['description'])
    
    # Drop duplicates based on title + description
    df = df.drop_duplicates(subset=['title', 'description'])
    
    # Reset index
    df = df.reset_index(drop=True)
    
    # Save
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f'After cleaning: {df.shape}')
    print(f'Saved to {output_path}')

if __name__ == '__main__':
    clean_master_dataset()