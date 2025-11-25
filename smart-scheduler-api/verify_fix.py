import pandas as pd
import io

def test_robust_read(filename, content_bytes):
    print(f"\nTesting file: {filename}")
    filename = filename.lower()
    df = None
    
    if filename.endswith('.csv'):
        try:
            print("Attempting UTF-8...")
            df = pd.read_csv(io.BytesIO(content_bytes), encoding='utf-8')
            print("Success with UTF-8")
        except UnicodeDecodeError:
            try:
                print("UTF-8 failed. Attempting CP1258...")
                df = pd.read_csv(io.BytesIO(content_bytes), encoding='cp1258')
                print("Success with CP1258")
            except UnicodeDecodeError:
                try:
                    print("CP1258 failed. Attempting Latin1...")
                    df = pd.read_csv(io.BytesIO(content_bytes), encoding='latin1')
                    print("Success with Latin1")
                except Exception:
                    try:
                        print("Text parsing failed. Attempting Excel fallback...")
                        df = pd.read_excel(io.BytesIO(content_bytes))
                        print("Success with Excel fallback")
                    except Exception as e:
                        print(f"All attempts failed: {e}")
        except pd.errors.ParserError:
            try:
                print("ParserError. Attempting Excel fallback...")
                df = pd.read_excel(io.BytesIO(content_bytes))
                print("Success with Excel fallback")
            except Exception as e:
                print(f"Excel fallback failed: {e}")
                
    elif filename.endswith(('.xls', '.xlsx')):
        try:
            df = pd.read_excel(io.BytesIO(content_bytes))
            print("Success with Excel read")
        except Exception as e:
            print(f"Excel read failed: {e}")

    if df is not None:
        print(f"Read {len(df)} rows.")
        print(df.head())
    else:
        print("Failed to produce DataFrame.")

def run_tests():
    # 1. Test CP1258 CSV
    print("--- Test Case 1: Vietnamese CSV (CP1258) ---")
    content_cp1258 = b"Code,Name\n123,Test \xe1" # \xe1 is 'á' in cp1258
    test_robust_read("test.csv", content_cp1258)

    # 2. Test XLSX disguised as CSV
    print("\n--- Test Case 2: XLSX file named .csv ---")
    df_orig = pd.DataFrame({'Code': ['456'], 'Name': ['ExcelData']})
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_orig.to_excel(writer, index=False)
    xlsx_bytes = output.getvalue()
    test_robust_read("fake.csv", xlsx_bytes)

if __name__ == "__main__":
    run_tests()
