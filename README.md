# Banking Risk Categories - RAG Dataset

Comprehensive dataset of banking and financial risk categories structured for RAG (Retrieval-Augmented Generation) applications.

## Structure

```
data/
  risk-categories/
    AllRiskCategories.json          # Main consolidated file (100 subcategories)
    MainCategories.json             # 10 main risk categories
    individual/                     # Individual category files (1-10)
    source/                         # Original markdown source files
scripts/
  build_consolidated.py             # Script to rebuild consolidated JSON
```

## Dataset Overview

- **10 Main Risk Categories**
- **100 Risk Subcategories** (10 per category)
- Each subcategory contains detailed regulatory and compliance information

### Main Categories

1. Credit Risk
2. Market Risk
3. Liquidity & Funding Risk
4. Operational Risk
5. Capital Adequacy & Solvency
6. Concentration Risk
7. Governance, Risk Management & Internal Controls
8. Technology, Cybersecurity & Information Security
9. Climate & Environmental Risk
10. Conduct, Consumer Protection & Market Integrity

## Usage for RAG

The `AllRiskCategories.json` file is optimized for RAG systems:

```json
{
  "categories": [
    {
      "id": 1,
      "category": "Credit Risk",
      "categoryDescription": "...",
      "subcategories": [
        {
          "id": "1.1",
          "title": "Credit Assessment & Underwriting Standards",
          "text": "Detailed description..."
        }
      ]
    }
  ]
}
```

### Recommended Approach

1. Create embeddings for each subcategory's `text` field
2. Store embeddings with metadata (id, title, category)
3. Use for semantic search and context retrieval
4. Feed retrieved subcategories as context to your LLM

## Building

To rebuild the consolidated file:

```bash
python scripts/build_consolidated.py
```

## License

[Add your license here]
