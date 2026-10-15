
import pandas as pd
from pathlib import Path

file_path = Path("data/raw/Financial Sample.xlsx")

if not file_path.exists():
    print("Dataset file not found!")
    print("Please check the file name and folder.")
else:
    df = pd.read_excel(file_path)

    print("\nFINANCIAL DATASET LOADED SUCCESSFULLY")
    print("-" * 45)

    print("\nDataset Shape:")
    print(df.shape)

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nData Types:")
    print(df.dtypes)
