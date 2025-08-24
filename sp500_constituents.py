import pandas as pd
import requests
from pathlib import Path
from datetime import datetime

def download_sp500_constituents():
    """Download current S&P 500 constituents from GitHub dataset"""
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Save to local file
        filepath = Path("sp500_constituents.csv")
        filepath.write_text(response.text)
        
        # Load and return as DataFrame
        df = pd.read_csv(filepath)
        print(f"Downloaded {len(df)} S&P 500 constituents")
        print(f"Saved to {filepath}")
        
        return df
    except Exception as e:
        print(f"Error downloading S&P 500 list: {e}")
        return None

def load_sp500_constituents():
    """Load S&P 500 constituents from local file or download if not exists"""
    filepath = Path("sp500_constituents.csv")
    
    if filepath.exists():
        # Check if file is older than 7 days
        file_age = datetime.now() - datetime.fromtimestamp(filepath.stat().st_mtime)
        if file_age.days > 7:
            print("S&P 500 list is older than 7 days, downloading fresh copy...")
            return download_sp500_constituents()
        else:
            df = pd.read_csv(filepath)
            print(f"Loaded {len(df)} S&P 500 constituents from cache")
            return df
    else:
        print("S&P 500 list not found, downloading...")
        return download_sp500_constituents()

def get_sp500_symbols():
    """Get just the symbol list"""
    df = load_sp500_constituents()
    if df is not None:
        return df['Symbol'].tolist()
    return []

if __name__ == "__main__":
    # Test the functions
    df = download_sp500_constituents()
    if df is not None:
        print("\nFirst 10 S&P 500 stocks:")
        print(df[['Symbol', 'Name', 'Sector']].head(10))
        
        print("\nSector distribution:")
        print(df['Sector'].value_counts())