#!/usr/bin/env python3
import json

# Read the JSON file
with open('AllRiskCategories.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Generate TypeScript mockData
output = '''export interface Overlap {
  id: string;
  regulationPair: [string, string];
  type: 'Duplicate' | 'Complementary' | 'Conflicting';
  description: string;
  confidenceScore: number;
  excerpts: {
    regulation1: string;
    regulation2: string;
  };
}

export interface Contradiction {
  id: string;
  regulationPair: [string, string];
  description: string;
  severity: 'High' | 'Medium' | 'Low';
  conflictingRequirements: {
    regulation1: string;
    regulation2: string;
  };
}

export interface Regulation {
  id: string;
  name: string;
  similarityScore: number;
  description: string;
  metadata?: any;
}

export interface SubCategory {
  id: string;
  name: string;
  description: string;
  paragraphsAnalyzed: number;
  overlapCount: number;
  contradictionCount: number;
  regulations: Regulation[];
  overlaps: Overlap[];
  contradictions: Contradiction[];
}

export interface RiskCategory {
  id: string;
  name: string;
  icon: string;
  regulationCount: number;
  subCategoryCount: number;
  overlapCount: number;
  contradictionCount: number;
  description: string;
  subCategories: SubCategory[];
}

// Clean category structure - all data will come from API
export const mockRiskCategories: RiskCategory[] = [
'''

icons = {
    'Credit Risk': 'TrendingDown',
    'Market Risk': 'BarChart3',
    'Liquidity & Funding Risk': 'Droplet',
    'Operational Risk': 'Settings'
}

for category in data['categories']:
    cat_name = category['category']
    icon = icons.get(cat_name, 'Circle')
    
    output += f'''  {{
    id: '{cat_name.lower().replace(' ', '-').replace('&', '')}',
    name: '{cat_name}',
    icon: '{icon}',
    regulationCount: 0,
    subCategoryCount: {len(category['subcategories'])},
    overlapCount: 0,
    contradictionCount: 0,
    description: {json.dumps(category['categoryDescription'])},
    subCategories: [
'''
    
    for subcat in category['subcategories']:
        output += f'''      {{
        id: '{subcat['id']}',
        name: '{subcat['title']}',
        description: {json.dumps(subcat['text'])},
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }},
'''
    
    output = output.rstrip(',\n') + '\n'
    output += '''    ]
  },
'''

output = output.rstrip(',\n') + '\n'
output += '''];
'''

# Write to file
with open('frontend/src/data/mockData.ts', 'w', encoding='utf-8') as f:
    f.write(output)

print("✅ Generated clean mockData.ts with all risk categories")
print(f"   Categories: {len(data['categories'])}")
print(f"   Total subcategories: {sum(len(c['subcategories']) for c in data['categories'])}")
