import pickle

data = pickle.load(open('metadata_store_production.pkl', 'rb'))

financial_terms = ['bank', 'capital requirement', 'mifid', 'basel', 'crr', 'credit risk', 'market risk', 'financial instrument', 'trading']

financial = [k for k, v in data.items() if any(term in str(v).lower() for term in financial_terms)]

print(f'Found {len(financial)} financial regulation chunks out of {len(data)} total')
print(f'Percentage: {len(financial)/len(data)*100:.2f}%')
print('\nSample regulations:')
for k in list(financial)[:10]:
    print(f'  - {data[k].get("regulation_name", "Unknown")} ({data[k].get("year", "N/A")})')
