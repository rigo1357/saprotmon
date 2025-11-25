import pandas as pd
import io

def test_csv_cp1258():
    print("Testing CSV with CP1258 (Vietnamese) encoding read as UTF-8...")
    # 'á' in cp1258 is 0xe1. 
    # We construct bytes directly to avoid script encoding issues.
    # 0xe1 is 'á' in cp1252/latin1/cp1258
    content = b"Code,Name\n123,Test \xe1" 
    try:
        pd.read_csv(io.BytesIO(content))
    except Exception as e:
        print(f"Caught error: {e}")

def test_xlsx_as_csv():
    print("\nTesting XLSX file read as CSV...")
    df = pd.DataFrame({'Code': ['123'], 'Name': ['Test']})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    xlsx_bytes = output.getvalue()
    
    try:
        pd.read_csv(io.BytesIO(xlsx_bytes))
    except Exception as e:
        print(f"Caught error: {e}")

if __name__ == "__main__":
    test_csv_cp1258()
    test_xlsx_as_csv()
