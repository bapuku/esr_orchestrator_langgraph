import pandas as pd
from pathlib import Path

DATA = Path("data/sample_waste_data.csv")

def get_waste_info(selector: str) -> dict:
    """
    selector can be batch_id like 'WB-789' or container_id like 'C-456'
    """
    if not DATA.exists():
        return {"results": []}
    df = pd.read_csv(DATA)
    if selector.startswith("C-"):
        rows = df[df["container_id"] == selector]
    elif selector.startswith("WB-"):
        rows = df[df["batch_id"] == selector]
    else:
        rows = df[df["material"].str.contains(selector, case=False, na=False)]
    return {"results": rows.to_dict(orient="records")}
