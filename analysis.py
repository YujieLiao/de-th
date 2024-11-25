import pandas as pd

if __name__ == "__main__":
    data = pd.read_csv("processed_data.csv")
    
    print(data.groupby("locale")["device_type"].count().sort_values())