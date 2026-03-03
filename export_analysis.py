import json
import glob
import re
import pandas as pd
import matplotlib.pyplot as plt
import os

def clean_value(val):
    """
    Cleans value string to float.
    Handles '1,234.56', empty strings, etc.
    """
    if not isinstance(val, str):
        return val
    if val.strip() == "":
        return 0.0
    try:
        return float(val.replace(',', ''))
    except ValueError:
        return 0.0

def load_data(pattern="export-data-commodity-wise/data-year-*.json"):
    """
    Loads all JSON files matching the pattern.
    Consolidates data into a dictionary keyed by HSCode.
    
    Structure:
    all_data = {
        'HSCode1': {
            'Commodity': 'Name',
            'years': {
                '2017-2018': 123.45,
                '2018-2019': 678.90,
                ...
            }
        },
        ...
    }
    """
    files = glob.glob(pattern)
    files.sort() # Ensure we process in order, so newer files (potentially) overwrite or add to older ones
    
    print(f"Found {len(files)} files: {files}")
    
    all_data = {}
    
    # Regex to identify year keys like "2017 - 2018", "2018-2019", etc.
    # Allowing for spaces around hyphens
    year_key_pattern = re.compile(r"^\d{4}\s*-\s*\d{4}$")

    for fpath in files:
        print(f"Processing {fpath}...")
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = json.load(f)
        except Exception as e:
            print(f"Error reading {fpath}: {e}")
            continue
            
        # Some files might identify 'tbody' directly, others might just be a list if structure varies
        # Based on view_file, structure is { "thead": [], "tbody": [] }
        rows = content.get('tbody', [])
        
        for row in rows:
            hscode = row.get('HSCode')
            if not hscode:
                continue
            
            # Normalize hscode potentially (strip spaces)
            hscode = hscode.strip()
            
            commodity = row.get('Commodity', '').strip()
            
            if hscode not in all_data:
                all_data[hscode] = {
                    'Commodity': commodity,
                    'years': {}
                }
            else:
                # Update commodity name if the new one is longer/better? 
                # Usually later files have better descriptions, or just overwrite.
                # Let's just overwrite to keep it simple, or keep the longest one.
                if len(commodity) > len(all_data[hscode]['Commodity']):
                    all_data[hscode]['Commodity'] = commodity
            
            # Extract year columns
            for key, val in row.items():
                if year_key_pattern.match(key):
                    # Normalized year key: remove spaces
                    year_norm = key.replace(" ", "")
                    numeric_val = clean_value(val)
                    
                    # Update the value
                    all_data[hscode]['years'][year_norm] = numeric_val

    return all_data

def analyze_hscode(all_data):
    """
    Interactive loop to search and graph HSCodes.
    """
    print("\nData loaded. Ready for query.")
    print("Enter 'q' to quit.")
    
    all_codes = sorted(all_data.keys())
    
    while True:
        query = input("\nEnter HSCode (or part of it): ").strip()
        if query.lower() == 'q':
            break
        
        if not query:
            continue
            
        # Find matches
        matches = [c for c in all_codes if query in c]
        
        if not matches:
            print("No matching HSCode found.")
            continue
        
        if len(matches) > 1:
            print(f"Found {len(matches)} matches. Showing first 10:")
            for m in matches[:10]:
                print(f"  {m} - {all_data[m]['Commodity']}")
            if len(matches) > 10:
                print("  ...")
            
            # If exact match exists in the list, ask if they meant that one, or just let them refine
            if query in matches:
                print(f"\nExact match found for '{query}'. Selecting it.")
                selected_code = query
            else:
                print("Please refine your search to select a specific code.")
                continue
        else:
            selected_code = matches[0]
            
        # Display data for the selected code
        data = all_data[selected_code]
        print(f"\nAnalysis for HSCode: {selected_code}")
        print(f"Commodity: {data['Commodity']}")
        
        # Sort years
        years = sorted(data['years'].keys())
        values = [data['years'][y] for y in years]
        
        df = pd.DataFrame({'Year': years, 'Value (Crore Rs)': values})
        print(df.to_string(index=False))
        
        # Plot
        if years:
            plt.figure(figsize=(10, 6))
            plt.plot(years, values, marker='o', linestyle='-', color='b')
            plt.title(f"Export Trends for {selected_code}\n{data['Commodity']}")
            plt.xlabel("Year")
            plt.ylabel("Value in Crore Rupee")
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            print("Displaying graph...")
            plt.show()
        else:
            print("No yearly data available for this code.")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming files are in current directory based on glob pattern in user request
    # but run_command often sets Cwd.
    # The load_data default pattern assumes files are in CWD.
    
    data = load_data()
    analyze_hscode(data)
