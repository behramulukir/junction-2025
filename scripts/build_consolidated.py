import json

# Read MainCategories for category descriptions
with open('MainCategories.json', 'r', encoding='utf-8') as f:
    main_cats = json.load(f)

# Map of file names to category info
category_files = [
    ('1CreditRisk.json', 1, 'Credit Risk'),
    ('2MarketRisk.json', 2, 'Market Risk'),
    ('3LiquidityFundingRisk.json', 3, 'Liquidity & Funding Risk'),
    ('4OperationalRisk.json', 4, 'Operational Risk'),
    ('5CapitalAdequacySolvency.json', 5, 'Capital Adequacy & Solvency'),
    ('6ConcentrationRisk.json', 6, 'Concentration Risk'),
    ('7GovernanceRiskManagement.json', 7, 'Governance, Risk Management & Internal Controls'),
    ('8TechnologyCybersecurity.json', 8, 'Technology, Cybersecurity & Information Security'),
    ('9ClimateEnvironmentalRisk.json', 9, 'Climate & Environmental Risk'),
    ('10ConductConsumerProtection.json', 10, 'Conduct, Consumer Protection & Market Integrity')
]

# Build consolidated structure
consolidated = {"categories": []}

for file_name, cat_id, cat_name in category_files:
    # Find matching category description from MainCategories
    cat_desc = next((c['text'] for c in main_cats if c['title'] == cat_name), '')
    
    # Read subcategories
    with open(file_name, 'r', encoding='utf-8') as f:
        subcats = json.load(f)
    
    # Add IDs to subcategories
    for idx, subcat in enumerate(subcats, 1):
        subcat['id'] = f"{cat_id}.{idx}"
    
    # Build category object
    category = {
        "id": cat_id,
        "category": cat_name,
        "categoryDescription": cat_desc,
        "subcategories": subcats
    }
    
    consolidated["categories"].append(category)

# Write consolidated file
with open('AllRiskCategories.json', 'w', encoding='utf-8') as f:
    json.dump(consolidated, f, indent=2, ensure_ascii=False)

print(f"Created AllRiskCategories.json with {len(consolidated['categories'])} categories")
total_subcats = sum(len(c['subcategories']) for c in consolidated['categories'])
print(f"Total subcategories: {total_subcats}")
