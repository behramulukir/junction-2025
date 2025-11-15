export interface Overlap {
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

export const mockRiskCategories: RiskCategory[] = [
  {
    id: 'credit-risk',
    name: 'Credit Risk',
    icon: 'TrendingDown',
    regulationCount: 12458,
    subCategoryCount: 10,
    overlapCount: 147,
    contradictionCount: 3,
    description: 'Credit risk encompasses the potential for financial loss arising from a borrower\'s failure to meet contractual obligations, counterparty default, credit quality deterioration, or downgrade events.',
    subCategories: [
      {
        id: '1.1',
        name: '1.1 Credit Assessment & Underwriting Standards',
        description: 'Credit assessment and underwriting standards govern the evaluation of borrower creditworthiness before granting credit, including know-your-customer (KYC) requirements, financial statement analysis, cash flow assessment, debt service coverage ratios, loan-to-value (LTV) ratio limits, debt-to-income (DTI) ratio thresholds for consumer lending, credit scoring models and rating systems.',
        paragraphsAnalyzed: 8542,
        overlapCount: 23,
        contradictionCount: 1,
        regulations: [
          { id: 'CRR-Art-124', name: 'CRR Article 124 - Risk Weights for Exposures', similarityScore: 0.94, description: 'Requirements for calculating risk weights for credit exposures' },
          { id: 'CRD-Art-79', name: 'CRD IV Article 79 - Credit Risk Assessment', similarityScore: 0.89, description: 'Standards for credit risk assessment procedures' },
          { id: 'EBA-GL-2020-06', name: 'EBA/GL/2020/06 - Loan Origination', similarityScore: 0.87, description: 'Guidelines on loan origination and monitoring' },
          { id: 'IFRS-9', name: 'IFRS 9 - Financial Instruments', similarityScore: 0.82, description: 'Classification and measurement of financial instruments' }
        ],
        overlaps: [
          {
            id: 'overlap-1-1',
            regulationPair: ['CRR Article 124', 'CRD IV Article 79'],
            type: 'Complementary',
            description: 'Both regulations address credit risk assessment but from different perspectives - CRR focuses on capital requirements while CRD IV addresses procedural standards.',
            confidenceScore: 0.89,
            excerpts: {
              regulation1: 'Credit institutions shall apply risk weights to their exposure values in accordance with the approaches set out in this Part...',
              regulation2: 'Competent authorities shall ensure that institutions have in place sound, effective and complete credit risk assessment processes...'
            }
          },
          {
            id: 'overlap-1-2',
            regulationPair: ['EBA/GL/2020/06', 'IFRS 9'],
            type: 'Duplicate',
            description: 'Similar requirements for assessing creditworthiness and expected credit losses at origination.',
            confidenceScore: 0.92,
            excerpts: {
              regulation1: 'Institutions should assess the borrower\'s ability to meet its obligations under the credit agreement...',
              regulation2: 'An entity shall measure expected credit losses of a financial instrument in a way that reflects reasonable and supportable information...'
            }
          }
        ],
        contradictions: [
          {
            id: 'contradiction-1-1',
            regulationPair: ['CRR Article 124', 'Local Banking Act §45'],
            description: 'Conflicting thresholds for residential mortgage risk weights.',
            severity: 'Medium',
            conflictingRequirements: {
              regulation1: 'Risk weight shall not be lower than 35% for residential property exposures',
              regulation2: 'Domestic residential mortgages may apply a minimum risk weight of 25% subject to national supervisor approval'
            }
          }
        ]
      },
      {
        id: '1.2',
        name: '1.2 Credit Risk Mitigation Techniques',
        description: 'Credit risk mitigation (CRM) techniques reduce credit exposure through funded protection such as cash collateral, financial collateral including bonds and equities, real estate mortgages, netting agreements, and unfunded protection including guarantees, credit derivatives, credit default swaps, and credit insurance.',
        paragraphsAnalyzed: 7234,
        overlapCount: 19,
        contradictionCount: 0,
        regulations: [
          { id: 'CRR-Art-194', name: 'CRR Article 194 - Funded Credit Protection', similarityScore: 0.91, description: 'Requirements for funded credit protection including collateral' },
          { id: 'CRR-Art-213', name: 'CRR Article 213 - Guarantees', similarityScore: 0.88, description: 'Eligibility criteria for guarantees as credit risk mitigation' },
          { id: 'Basel-CRM', name: 'Basel III - Credit Risk Mitigation', similarityScore: 0.85, description: 'International standards for credit risk mitigation techniques' }
        ],
        overlaps: [
          {
            id: 'overlap-1-3',
            regulationPair: ['CRR Article 194', 'Basel III - Credit Risk Mitigation'],
            type: 'Complementary',
            description: 'CRR implements Basel III standards on credit risk mitigation with additional EU-specific requirements.',
            confidenceScore: 0.87,
            excerpts: {
              regulation1: 'Funded credit protection shall be recognized where the credit institution has a funded credit protection from an eligible provider...',
              regulation2: 'Banks may use a number of techniques to mitigate the credit risks to which they are exposed including collateral, guarantees and credit derivatives...'
            }
          }
        ],
        contradictions: []
      },
      {
        id: '1.3',
        name: '1.3 Expected Credit Losses, Impairment & Provisioning',
        description: 'Expected credit loss (ECL) framework under IFRS 9 requires institutions to recognize credit losses based on forward-looking information, including 12-month ECL for performing exposures in Stage 1, lifetime ECL for underperforming exposures with significant increase in credit risk in Stage 2.',
        paragraphsAnalyzed: 6891,
        overlapCount: 21,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.4',
        name: '1.4 Non-Performing Exposures & Forbearance',
        description: 'Non-performing exposure (NPE) management includes definition of default under Article 178 CRR with 90 days past due threshold and unlikeliness to pay criteria, classification of non-performing loans (NPL) and non-performing advances, forbearance measures as concessions to borrowers in financial difficulty.',
        paragraphsAnalyzed: 5678,
        overlapCount: 18,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.5',
        name: '1.5 Counterparty Credit Risk (CCR)',
        description: 'Counterparty credit risk (CCR) arises from derivatives, securities financing transactions (SFT) including repurchase agreements and securities lending, long settlement transactions, and other transactions where future exposure varies with market factors.',
        paragraphsAnalyzed: 6234,
        overlapCount: 20,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.6',
        name: '1.6 Securitization Credit Risk',
        description: 'Securitization credit risk involves the transfer of credit risk through structured finance instruments including asset-backed securities (ABS), mortgage-backed securities (MBS), collateralized loan obligations (CLO), and synthetic securitizations.',
        paragraphsAnalyzed: 5432,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.7',
        name: '1.7 Credit Risk Internal Models & IRB Approach',
        description: 'Internal ratings-based (IRB) approach allows banks to use internal models for credit risk capital calculation, covering foundation IRB (F-IRB) where banks estimate probability of default (PD) and supervisors provide loss given default (LGD) and exposure at default (EAD).',
        paragraphsAnalyzed: 7123,
        overlapCount: 22,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.8',
        name: '1.8 Credit Risk Standardized Approaches & RWA',
        description: 'Standardized approach for credit risk assigns risk weights to exposures based on exposure class and external credit ratings, including sovereigns and central banks typically 0% risk weight, institutions with risk weights varying from 20% to 150% based on credit quality.',
        paragraphsAnalyzed: 6789,
        overlapCount: 19,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.9',
        name: '1.9 Credit Derivatives & Credit Protection',
        description: 'Credit derivatives used for credit risk transfer and hedging include credit default swaps (CDS) providing protection against credit events such as default, bankruptcy, or restructuring, total return swaps exchanging total economic performance, credit-linked notes embedding credit risk.',
        paragraphsAnalyzed: 5234,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.10',
        name: '1.10 Credit Risk Stress Testing & Scenario Analysis',
        description: 'Credit risk stress testing assesses portfolio resilience under adverse scenarios including macroeconomic downturns, sector-specific shocks, interest rate stress, unemployment increases, real estate price declines, and commodity price movements.',
        paragraphsAnalyzed: 6456,
        overlapCount: 17,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'market-risk',
    name: 'Market Risk',
    icon: 'BarChart3',
    regulationCount: 9842,
    subCategoryCount: 10,
    overlapCount: 98,
    contradictionCount: 2,
    description: 'Market risk represents the potential for losses due to adverse movements in market prices including interest rate fluctuations, foreign exchange rate volatility, equity price changes, commodity price movements, and credit spread variations.',
    subCategories: [
      {
        id: '2.1',
        name: '2.1 Interest Rate Risk in the Trading Book',
        description: 'Interest rate risk in the trading book arises from changes in interest rates affecting the value of trading positions including bonds, interest rate derivatives, and other rate-sensitive instruments.',
        paragraphsAnalyzed: 7823,
        overlapCount: 18,
        contradictionCount: 1,
        regulations: [
          { id: 'CRR-Art-325', name: 'CRR Article 325 - Trading Book', similarityScore: 0.93, description: 'Definition and requirements for trading book positions' },
          { id: 'FRTB-Standard', name: 'FRTB Standard - Fundamental Review', similarityScore: 0.88, description: 'Fundamental review of the trading book framework' },
          { id: 'IAS-39', name: 'IAS 39 - Financial Instruments Recognition', similarityScore: 0.84, description: 'Accounting standards for financial instruments' }
        ],
        overlaps: [
          {
            id: 'overlap-2-1',
            regulationPair: ['CRR Article 325', 'FRTB Standard'],
            type: 'Complementary',
            description: 'Both regulations define trading book positions but FRTB provides more granular requirements for interest rate risk.',
            confidenceScore: 0.91,
            excerpts: {
              regulation1: 'The trading book shall consist of positions in financial instruments held with trading intent...',
              regulation2: 'A trading desk is defined as a grouping of traders or trading accounts that implements a well-defined business strategy...'
            }
          }
        ],
        contradictions: [
          {
            id: 'contradiction-2-1',
            regulationPair: ['FRTB Standard', 'CRR Article 325'],
            description: 'Different methodologies for calculating interest rate risk capital requirements.',
            severity: 'High',
            conflictingRequirements: {
              regulation1: 'Sensitivities-based approach with prescribed risk weights for delta, vega and curvature',
              regulation2: 'Standardized approach based on maturity ladder and duration-based calculations'
            }
          }
        ]
      },
      {
        id: '2.2',
        name: '2.2 Foreign Exchange Risk',
        description: 'Foreign exchange (FX) risk represents exposure to adverse movements in currency exchange rates affecting the value of positions denominated in foreign currencies, including spot FX, FX forwards, FX swaps, currency options, and cross-currency basis swaps.',
        paragraphsAnalyzed: 6341,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.3',
        name: '2.3 Equity Risk',
        description: 'Equity risk arises from changes in equity prices affecting trading book positions in individual stocks, equity indices, equity derivatives including options and futures, equity swaps, and convertible bonds.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.4',
        name: '2.4 Commodity Risk',
        description: 'Commodity risk involves exposure to price changes in physical commodities and commodity derivatives including energy products (crude oil, natural gas, electricity), precious metals (gold, silver, platinum), base metals (copper, aluminum, zinc), agricultural products.',
        paragraphsAnalyzed: 5234,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.5',
        name: '2.5 Credit Spread Risk in Trading Book',
        description: 'Credit spread risk in the trading book represents exposure to changes in credit spreads affecting the value of corporate bonds, credit derivatives, securitization positions, and other credit-sensitive instruments held for trading.',
        paragraphsAnalyzed: 5876,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.6',
        name: '2.6 Value-at-Risk (VaR) & Risk Metrics',
        description: 'Value-at-Risk (VaR) measures the maximum potential loss over a specified time horizon at a given confidence level, typically 99% confidence over 10 trading days for regulatory capital.',
        paragraphsAnalyzed: 6123,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.7',
        name: '2.7 Trading Book vs Banking Book Boundary',
        description: 'The boundary between trading book and banking book determines which positions are subject to market risk capital requirements versus credit risk capital requirements, with significant implications for capital treatment and risk management.',
        paragraphsAnalyzed: 5542,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.8',
        name: '2.8 Market Liquidity Risk',
        description: 'Market liquidity risk is the risk that institutions cannot easily offset or eliminate positions without significantly affecting market prices due to inadequate market depth or market disruptions.',
        paragraphsAnalyzed: 4987,
        overlapCount: 10,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.9',
        name: '2.9 Hedging Strategies & Hedge Accounting',
        description: 'Hedging strategies aim to reduce market risk exposures through offsetting positions, while hedge accounting allows matching of gains and losses on hedging instruments with hedged items.',
        paragraphsAnalyzed: 5321,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.10',
        name: '2.10 Market Risk Stress Testing & Scenario Analysis',
        description: 'Market risk stress testing evaluates the impact of extreme but plausible market movements on trading portfolios including historical scenarios (2008 financial crisis, COVID-19 market shock), hypothetical scenarios.',
        paragraphsAnalyzed: 6234,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'liquidity-funding',
    name: 'Liquidity & Funding Risk',
    icon: 'Droplet',
    regulationCount: 8234,
    subCategoryCount: 10,
    overlapCount: 76,
    contradictionCount: 1,
    description: 'Liquidity and funding risk involves the inability to meet payment obligations when due without incurring unacceptable losses, or the inability to fund assets at a reasonable cost.',
    subCategories: [
      {
        id: '3.1',
        name: '3.1 Liquidity Coverage Ratio (LCR)',
        description: 'The Liquidity Coverage Ratio (LCR) requires institutions to maintain sufficient high-quality liquid assets (HQLA) to survive a 30-day acute liquidity stress scenario, with minimum requirement of 100%.',
        paragraphsAnalyzed: 7234,
        overlapCount: 18,
        contradictionCount: 0,
        regulations: [
          { id: 'CRR-Art-412', name: 'CRR Article 412 - Liquidity Coverage Requirement', similarityScore: 0.96, description: 'Minimum LCR requirement of 100%' },
          { id: 'Del-Reg-2015-61', name: 'Delegated Regulation 2015/61 - LCR', similarityScore: 0.94, description: 'Detailed LCR calculation methodology' },
          { id: 'Basel-LCR', name: 'Basel III - LCR Standard', similarityScore: 0.92, description: 'International LCR framework' },
          { id: 'EBA-GL-2017-01', name: 'EBA/GL/2017/01 - HQLA', similarityScore: 0.89, description: 'Guidelines on high-quality liquid assets' }
        ],
        overlaps: [
          {
            id: 'overlap-3-1',
            regulationPair: ['CRR Article 412', 'Delegated Regulation 2015/61'],
            type: 'Complementary',
            description: 'CRR sets the principle requirement while Delegated Regulation provides detailed calculation rules.',
            confidenceScore: 0.95,
            excerpts: {
              regulation1: 'Credit institutions shall hold liquid assets, the sum of the values of which covers the liquidity outflows less the liquidity inflows under stressed conditions...',
              regulation2: 'The liquidity coverage requirement shall be calculated as the ratio of the liquidity buffer to the net liquidity outflows over a 30-day stress period...'
            }
          },
          {
            id: 'overlap-3-2',
            regulationPair: ['Basel III - LCR Standard', 'CRR Article 412'],
            type: 'Duplicate',
            description: 'EU implementation of Basel III LCR standard with minor adjustments.',
            confidenceScore: 0.93,
            excerpts: {
              regulation1: 'The LCR is defined as the ratio of the stock of HQLA to total net cash outflows over the next 30 calendar days...',
              regulation2: 'Institutions shall maintain liquidity coverage ratio of at least 100% calculated in accordance with this Regulation...'
            }
          }
        ],
        contradictions: []
      },
      {
        id: '3.2',
        name: '3.2 Net Stable Funding Ratio (NSFR)',
        description: 'The Net Stable Funding Ratio (NSFR) promotes stable funding structures by requiring available stable funding (ASF) to exceed required stable funding (RSF) over a one-year horizon, with minimum 100% requirement.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.3',
        name: '3.3 Intraday Liquidity Management',
        description: 'Intraday liquidity management ensures institutions can meet payment and settlement obligations throughout the business day without disrupting operations or incurring losses.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.4',
        name: '3.4 Contingency Funding Plan & Stress Testing',
        description: 'Contingency funding plans (CFP) establish strategies and procedures for responding to liquidity stress events, ensuring institutions can continue to meet obligations during disruptions.',
        paragraphsAnalyzed: 6123,
        overlapCount: 15,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.5',
        name: '3.5 Maturity Transformation & Funding Gaps',
        description: 'Maturity transformation involves funding long-term assets with shorter-term liabilities, creating maturity mismatches and rollover risk.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.6',
        name: '3.6 Funding Concentration & Diversification',
        description: 'Funding concentration risk arises from over-reliance on specific funding sources, counterparties, instruments, currencies, or markets, creating vulnerability if access is disrupted.',
        paragraphsAnalyzed: 5234,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.7',
        name: '3.7 Asset Encumbrance & Collateral Management',
        description: 'Asset encumbrance occurs when assets are pledged as collateral or otherwise restricted, reducing available unencumbered assets for liquidity management and potentially signaling financial stress.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.8',
        name: '3.8 Deposit Stability & Retail Funding',
        description: 'Deposit stability analysis assesses the reliability of retail and corporate deposits as funding sources, considering customer behavior during normal and stressed conditions.',
        paragraphsAnalyzed: 5456,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.9',
        name: '3.9 Wholesale Funding & Market Access',
        description: 'Wholesale funding includes unsecured and secured borrowing from financial institutions, corporates, and institutional investors through instruments such as interbank deposits, commercial paper, certificates of deposit.',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.10',
        name: '3.10 Central Bank Facilities & Lender of Last Resort',
        description: 'Central bank facilities provide liquidity support through standing facilities, open market operations, and emergency lending, serving as backstop for solvent institutions facing temporary liquidity stress.',
        paragraphsAnalyzed: 6012,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'operational-risk',
    name: 'Operational Risk',
    icon: 'Settings',
    regulationCount: 11567,
    subCategoryCount: 10,
    overlapCount: 112,
    contradictionCount: 4,
    description: 'Operational risk is the risk of loss resulting from inadequate or failed internal processes, human errors, system failures, or external events including natural disasters.',
    subCategories: [
      {
        id: '4.1',
        name: '4.1 Internal Fraud',
        description: 'Internal fraud involves intentional acts by employees or insiders to defraud, misappropriate assets, or circumvent regulations, laws, or company policies, excluding discrimination and diversity events.',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 1,
        regulations: [
          { id: 'CRR-Art-315', name: 'CRR Article 315 - Operational Risk', similarityScore: 0.88, description: 'Operational risk capital requirements including fraud' },
          { id: 'EBA-GL-2017-17', name: 'EBA/GL/2017/17 - Fraud Reporting', similarityScore: 0.86, description: 'Guidelines on fraud reporting obligations' },
          { id: 'MiFID-II-Art-16', name: 'MiFID II Article 16 - Organizational Requirements', similarityScore: 0.82, description: 'Requirements for preventing employee misconduct' }
        ],
        overlaps: [
          {
            id: 'overlap-4-1',
            regulationPair: ['CRR Article 315', 'EBA/GL/2017/17'],
            type: 'Complementary',
            description: 'CRR requires capital for operational risk including fraud, while EBA guidelines specify reporting procedures.',
            confidenceScore: 0.85,
            excerpts: {
              regulation1: 'Institutions shall hold own funds requirements for operational risk including losses from internal fraud...',
              regulation2: 'Institutions shall establish procedures for identifying, recording and reporting fraud incidents to competent authorities...'
            }
          }
        ],
        contradictions: [
          {
            id: 'contradiction-4-1',
            regulationPair: ['EBA/GL/2017/17', 'National Fraud Act §12'],
            description: 'Different timeframes for reporting internal fraud incidents to authorities.',
            severity: 'Medium',
            conflictingRequirements: {
              regulation1: 'Material fraud incidents shall be reported within 72 hours of discovery',
              regulation2: 'Internal fraud must be reported to national authorities within 5 business days'
            }
          }
        ]
      },
      {
        id: '4.2',
        name: '4.2 External Fraud',
        description: 'External fraud results from intentional acts by third parties to defraud, misappropriate assets, or circumvent laws, including theft, robbery, forgery, check kiting, and electronic fraud.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.3',
        name: '4.3 Employment Practices & Workplace Safety',
        description: 'Employment practices and workplace safety risk arises from acts inconsistent with employment, health, or safety laws or agreements, including workers compensation claims, discrimination, harassment, and workplace safety violations.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.4',
        name: '4.4 Clients, Products & Business Practices',
        description: 'Risks from clients, products, and business practices include unintentional or negligent failures to meet professional obligations to clients, or from the nature or design of products.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.5',
        name: '4.5 Damage to Physical Assets',
        description: 'Damage to physical assets results from natural disasters or other events causing loss or damage to physical property including buildings, equipment, and infrastructure.',
        paragraphsAnalyzed: 4987,
        overlapCount: 10,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.6',
        name: '4.6 Business Disruption & System Failures',
        description: 'Business disruption and system failures involve disruption of business operations or system failures including hardware, software, telecommunications, and utility outages.',
        paragraphsAnalyzed: 6456,
        overlapCount: 15,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.7',
        name: '4.7 Execution, Delivery & Process Management',
        description: 'Execution, delivery, and process management failures result from failed transaction processing, process management errors, or disputes with trade counterparties and vendors.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.8',
        name: '4.8 Outsourcing & Third-Party Risk',
        description: 'Outsourcing and third-party risk arises from reliance on external service providers for critical functions, creating dependencies and potential vulnerabilities.',
        paragraphsAnalyzed: 6123,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.9',
        name: '4.9 Legal & Regulatory Risk',
        description: 'Legal and regulatory risk involves exposure to fines, penalties, or punitive damages resulting from supervisory actions or private settlements due to non-compliance with laws, regulations, or legal obligations.',
        paragraphsAnalyzed: 7234,
        overlapCount: 17,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.10',
        name: '4.10 Operational Resilience & Business Continuity',
        description: 'Operational resilience ensures critical operations and services remain within tolerance levels during disruption, enabling institutions to continue serving customers and meeting obligations.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'capital-adequacy',
    name: 'Capital Adequacy & Solvency',
    icon: 'Shield',
    regulationCount: 10234,
    subCategoryCount: 10,
    overlapCount: 89,
    contradictionCount: 2,
    description: 'Capital adequacy and solvency risk relates to maintaining sufficient capital resources to absorb unexpected losses and meet minimum regulatory requirements.',
    subCategories: [
      {
        id: '5.1',
        name: '5.1 Common Equity Tier 1 (CET1) Capital',
        description: 'Common Equity Tier 1 (CET1) capital represents the highest quality capital consisting primarily of common shares, retained earnings, accumulated other comprehensive income (AOCI), and other disclosed reserves.',
        paragraphsAnalyzed: 7456,
        overlapCount: 18,
        contradictionCount: 0,
        regulations: [
          { id: 'CRR-Art-26', name: 'CRR Article 26 - Common Equity Tier 1 Items', similarityScore: 0.97, description: 'Definition of CET1 capital instruments' },
          { id: 'CRR-Art-36', name: 'CRR Article 36 - Deductions from CET1', similarityScore: 0.95, description: 'Items to be deducted from CET1 capital' },
          { id: 'Basel-III-CET1', name: 'Basel III - CET1 Definition', similarityScore: 0.93, description: 'International standard for CET1 capital' },
          { id: 'IAS-1', name: 'IAS 1 - Presentation of Financial Statements', similarityScore: 0.81, description: 'Accounting treatment of equity components' }
        ],
        overlaps: [
          {
            id: 'overlap-5-1',
            regulationPair: ['CRR Article 26', 'CRR Article 36'],
            type: 'Complementary',
            description: 'Article 26 defines what qualifies as CET1 while Article 36 specifies mandatory deductions.',
            confidenceScore: 0.96,
            excerpts: {
              regulation1: 'Common Equity Tier 1 items shall comprise paid-in capital instruments, share premium, retained earnings, accumulated other comprehensive income...',
              regulation2: 'Institutions shall deduct from Common Equity Tier 1 items goodwill, intangible assets, deferred tax assets...'
            }
          },
          {
            id: 'overlap-5-2',
            regulationPair: ['Basel III - CET1 Definition', 'CRR Article 26'],
            type: 'Duplicate',
            description: 'EU CRR implements Basel III CET1 definition with minimal differences.',
            confidenceScore: 0.94,
            excerpts: {
              regulation1: 'Common Equity Tier 1 must comprise common shares issued by the bank that meet the criteria for classification as common shares...',
              regulation2: 'Capital instruments shall qualify as Common Equity Tier 1 instruments only if they meet all criteria specified in this Article...'
            }
          }
        ],
        contradictions: []
      },
      {
        id: '5.2',
        name: '5.2 Additional Tier 1 (AT1) Capital',
        description: 'Additional Tier 1 (AT1) capital consists of instruments subordinated to depositors and general creditors, capable of absorbing losses while the institution remains a going concern.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.3',
        name: '5.3 Tier 2 Capital & Subordinated Debt',
        description: 'Tier 2 capital provides additional loss absorption on a gone-concern basis, consisting primarily of subordinated debt instruments with minimum five-year original maturity.',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.4',
        name: '5.4 Capital Conservation Buffer',
        description: 'The capital conservation buffer requires institutions to hold CET1 capital above minimum requirements to absorb losses during stress while maintaining capacity to lend, set at 2.5% of RWA.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.5',
        name: '5.5 Countercyclical Capital Buffer (CCyB)',
        description: 'The countercyclical capital buffer (CCyB) varies between 0% and 2.5% of RWA based on credit cycle conditions, increasing during periods of excessive credit growth to build resilience.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.6',
        name: '5.6 Systemic Risk Buffers & G-SII/O-SII',
        description: 'Systemic risk buffers apply to systemically important institutions whose failure would have significant negative externalities on the financial system and real economy.',
        paragraphsAnalyzed: 6456,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.7',
        name: '5.7 Leverage Ratio',
        description: 'The leverage ratio serves as non-risk-based backstop to risk-weighted capital requirements, calculated as Tier 1 capital divided by total exposure measure, with minimum requirement of 3%.',
        paragraphsAnalyzed: 6123,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.8',
        name: '5.8 MREL & TLAC Requirements',
        description: 'Minimum requirement for own funds and eligible liabilities (MREL) and total loss-absorbing capacity (TLAC) ensure institutions have sufficient loss-absorbing and recapitalization capacity to support resolution.',
        paragraphsAnalyzed: 7234,
        overlapCount: 17,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.9',
        name: '5.9 Capital Planning & Stress Testing',
        description: 'Capital planning ensures institutions maintain adequate capital under baseline and stress scenarios, supporting business strategy while meeting regulatory requirements and market expectations.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.10',
        name: '5.10 Internal Capital Adequacy Assessment (ICAAP)',
        description: 'Internal Capital Adequacy Assessment Process (ICAAP) requires institutions to assess capital adequacy relative to risk profile, considering all material risks including those not fully captured in Pillar 1 requirements.',
        paragraphsAnalyzed: 7012,
        overlapCount: 17,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'concentration-risk',
    name: 'Concentration Risk',
    icon: 'Target',
    regulationCount: 6543,
    subCategoryCount: 10,
    overlapCount: 54,
    contradictionCount: 1,
    description: 'Concentration risk arises from large exposures to individual counterparties, groups of connected clients, economic sectors, geographic regions, or specific instruments.',
    subCategories: [
      {
        id: '6.1',
        name: '6.1 Large Exposures & Single Name Concentration',
        description: 'Large exposures framework limits concentration to individual counterparties or groups of connected clients to prevent excessive loss from single obligor default. The fundamental limit restricts exposures to 25% of eligible capital.',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.2',
        name: '6.2 Sectoral & Industry Concentration',
        description: 'Sectoral concentration risk arises from excessive exposure to specific industries or economic sectors that may be affected by common risk factors, creating correlated losses during sector-specific downturns.',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.3',
        name: '6.3 Geographic & Country Concentration',
        description: 'Geographic concentration risk involves excessive exposure to specific countries, regions, or geographic areas, creating vulnerability to localized economic shocks, political events, natural disasters, or regulatory changes.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.4',
        name: '6.4 Intra-Financial System Exposures',
        description: 'Intra-financial system exposures represent concentration risk from interconnectedness between financial institutions, creating potential for contagion and systemic risk amplification during stress.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.5',
        name: '6.5 Product & Asset Class Concentration',
        description: 'Product and asset class concentration risk arises from excessive exposure to specific lending products, asset types, or financial instruments that may be affected by common risk factors or market conditions.',
        paragraphsAnalyzed: 5234,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.6',
        name: '6.6 Funding Source Concentration',
        description: 'Funding source concentration creates liquidity and refinancing risk from over-reliance on specific funding providers, instruments, or markets, making the institution vulnerable if access is disrupted.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.7',
        name: '6.7 Currency Concentration',
        description: 'Currency concentration risk involves excessive exposure to specific foreign currencies in assets, liabilities, or off-balance sheet positions, creating vulnerability to exchange rate movements and foreign currency liquidity stress.',
        paragraphsAnalyzed: 4987,
        overlapCount: 10,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.8',
        name: '6.8 Collateral & Security Concentration',
        description: 'Collateral concentration risk arises from over-reliance on specific types of collateral or security for credit risk mitigation, creating vulnerability if collateral values decline or enforceability is challenged.',
        paragraphsAnalyzed: 5321,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.9',
        name: '6.9 Concentration Risk Measurement & Metrics',
        description: 'Concentration risk measurement quantifies the degree of concentration and potential impact on capital adequacy using various metrics and methodologies including Herfindahl-Hirschman Index (HHI).',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.10',
        name: '6.10 Concentration Risk Limits & Governance',
        description: 'Concentration risk governance establishes frameworks for identifying, measuring, monitoring, and controlling concentration risk through limits, policies, and oversight structures.',
        paragraphsAnalyzed: 5456,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'governance-risk',
    name: 'Governance, Risk Management & Internal Controls',
    icon: 'Network',
    regulationCount: 13421,
    subCategoryCount: 10,
    overlapCount: 134,
    contradictionCount: 3,
    description: 'Governance and risk management encompasses the organizational framework, oversight structures, risk culture, and control systems ensuring effective identification, measurement, monitoring and mitigation of risks.',
    subCategories: [
      {
        id: '7.1',
        name: '7.1 Board of Directors & Management Body',
        description: 'The board of directors or management body bears ultimate responsibility for the institution\'s strategy, risk appetite, and oversight of risk management, requiring appropriate composition, expertise, and functioning.',
        paragraphsAnalyzed: 7234,
        overlapCount: 17,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.2',
        name: '7.2 Risk Appetite Framework',
        description: 'Risk appetite framework defines the types and levels of risk an institution is willing to accept in pursuit of its business objectives, establishing boundaries for risk-taking activities.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.3',
        name: '7.3 Three Lines of Defense Model',
        description: 'Three lines of defense model establishes clear separation between business functions taking risks (first line), independent risk management and compliance functions (second line), and internal audit (third line).',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.4',
        name: '7.4 Risk Committee & Risk Governance',
        description: 'Risk committee provides specialized oversight of risk management framework, risk profile, and risk appetite, supporting the board in fulfilling its risk oversight responsibilities.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.5',
        name: '7.5 Chief Risk Officer & Risk Management Function',
        description: 'Chief Risk Officer (CRO) leads the independent risk management function with sufficient authority, stature, and resources to challenge business decisions and escalate concerns to senior management and board.',
        paragraphsAnalyzed: 6456,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.6',
        name: '7.6 Internal Audit Function',
        description: 'Internal audit provides independent assurance on the effectiveness of governance, risk management, and internal controls, reporting directly to the board or audit committee.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.7',
        name: '7.7 Remuneration & Incentive Structures',
        description: 'Remuneration policies align compensation with prudent risk-taking, long-term performance, and regulatory requirements, avoiding incentives for excessive risk-taking.',
        paragraphsAnalyzed: 6123,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.8',
        name: '7.8 Conflicts of Interest Management',
        description: 'Conflicts of interest management identifies, assesses, and manages situations where interests of the institution, employees, or clients may conflict, ensuring fair treatment and appropriate controls.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.9',
        name: '7.9 Risk Data Aggregation & Reporting',
        description: 'Risk data aggregation and reporting capabilities ensure accurate, complete, and timely risk information is available to support decision-making, risk management, and regulatory reporting.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.10',
        name: '7.10 Risk Culture & Conduct',
        description: 'Risk culture encompasses values, beliefs, knowledge, attitudes, and behaviors regarding risk within the organization, influencing how risks are identified, understood, discussed, and acted upon.',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'technology-cyber',
    name: 'Technology, Cybersecurity & Information Security',
    icon: 'Lock',
    regulationCount: 9876,
    subCategoryCount: 10,
    overlapCount: 95,
    contradictionCount: 5,
    description: 'Technology and cybersecurity risk involves threats from information and communication technology (ICT) system failures, cyber attacks including malware and ransomware, data breaches compromising personal or confidential information.',
    subCategories: [
      {
        id: '8.1',
        name: '8.1 ICT Risk Management Framework',
        description: 'ICT risk management framework under Digital Operational Resilience Act (DORA) establishes comprehensive approach to identifying, assessing, monitoring, and mitigating information and communication technology risks.',
        paragraphsAnalyzed: 7234,
        overlapCount: 17,
        contradictionCount: 1,
        regulations: [
          { id: 'DORA-Art-6', name: 'DORA Article 6 - ICT Risk Management Framework', similarityScore: 0.96, description: 'Requirements for ICT risk management framework' },
          { id: 'EBA-GL-2019-04', name: 'EBA/GL/2019/04 - ICT Risk Assessment', similarityScore: 0.89, description: 'Guidelines on ICT and security risk management' },
          { id: 'GDPR-Art-32', name: 'GDPR Article 32 - Security of Processing', similarityScore: 0.84, description: 'Security measures for personal data processing' },
          { id: 'NIS2-Directive', name: 'NIS2 Directive - Cybersecurity', similarityScore: 0.82, description: 'Network and information security requirements' }
        ],
        overlaps: [
          {
            id: 'overlap-8-1',
            regulationPair: ['DORA Article 6', 'EBA/GL/2019/04'],
            type: 'Complementary',
            description: 'DORA establishes binding requirements while EBA guidelines provide implementation details.',
            confidenceScore: 0.91,
            excerpts: {
              regulation1: 'Financial entities shall have in place an internal governance and control framework that ensures effective and prudent management of ICT risk...',
              regulation2: 'Institutions should establish a comprehensive ICT risk management framework as an integral part of their overall risk management system...'
            }
          },
          {
            id: 'overlap-8-2',
            regulationPair: ['DORA Article 6', 'GDPR Article 32'],
            type: 'Duplicate',
            description: 'Overlapping requirements for security measures and risk assessments.',
            confidenceScore: 0.87,
            excerpts: {
              regulation1: 'The ICT risk management framework shall include mechanisms to promptly detect anomalous activities...',
              regulation2: 'The controller and processor shall implement appropriate technical and organizational measures to ensure a level of security appropriate to the risk...'
            }
          }
        ],
        contradictions: [
          {
            id: 'contradiction-8-1',
            regulationPair: ['DORA Article 6', 'NIS2 Directive'],
            description: 'Different incident reporting timeframes and thresholds.',
            severity: 'High',
            conflictingRequirements: {
              regulation1: 'Major ICT-related incidents shall be reported within 4 hours of detection',
              regulation2: 'Significant incidents must be notified within 24 hours of becoming aware'
            }
          }
        ]
      },
      {
        id: '8.2',
        name: '8.2 Cybersecurity Controls & Defense',
        description: 'Cybersecurity controls protect against cyber threats including malware, ransomware, phishing, denial-of-service attacks, and advanced persistent threats through preventive, detective, and responsive measures.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.3',
        name: '8.3 Data Protection & Privacy (GDPR)',
        description: 'Data protection and privacy requirements under General Data Protection Regulation (GDPR) govern collection, processing, storage, and transfer of personal data, ensuring individual rights and organizational accountability.',
        paragraphsAnalyzed: 6456,
        overlapCount: 15,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.4',
        name: '8.4 Incident Detection, Response & Recovery',
        description: 'Incident detection, response, and recovery capabilities enable timely identification of ICT incidents, effective response to contain and mitigate impact, and recovery of operations to normal state.',
        paragraphsAnalyzed: 6123,
        overlapCount: 14,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.5',
        name: '8.5 Third-Party ICT Service Providers',
        description: 'Third-party ICT service provider oversight addresses risks from outsourcing critical ICT functions including cloud computing, data centers, and software services, ensuring appropriate due diligence and ongoing monitoring.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.6',
        name: '8.6 Digital Operational Resilience Testing',
        description: 'Digital operational resilience testing under DORA includes vulnerability assessments, scenario-based testing, and threat-led penetration testing (TLPT) to assess ICT system resilience and identify weaknesses.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.7',
        name: '8.7 Access Control & Identity Management',
        description: 'Access control and identity management ensure only authorized individuals can access systems and data, implementing authentication mechanisms, authorization rules, and privileged access management.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.8',
        name: '8.8 Encryption & Data Security',
        description: 'Encryption and data security protect sensitive information through cryptographic controls for data at rest, in transit, and in use, ensuring confidentiality, integrity, and availability.',
        paragraphsAnalyzed: 5234,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.9',
        name: '8.9 Network Security & Segmentation',
        description: 'Network security and segmentation protect against unauthorized access and lateral movement within networks through firewalls, intrusion detection/prevention systems, network segmentation, and secure network architecture.',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.10',
        name: '8.10 ICT Incident Reporting',
        description: 'ICT incident reporting obligations require timely notification to supervisory authorities of major ICT-related incidents, cyber threats, and significant operational disruptions within specified timeframes.',
        paragraphsAnalyzed: 5321,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'climate-environmental',
    name: 'Climate & Environmental Risk',
    icon: 'Leaf',
    regulationCount: 5432,
    subCategoryCount: 10,
    overlapCount: 47,
    contradictionCount: 1,
    description: 'Climate and environmental risk encompasses both physical risks from climate-related events such as floods, droughts, wildfires and extreme weather, and transition risks from the shift toward a low-carbon economy.',
    subCategories: [
      {
        id: '9.1',
        name: '9.1 Climate-Related Financial Disclosures (TCFD)',
        description: 'Climate-related financial disclosures under Task Force on Climate-related Financial Disclosures (TCFD) framework require reporting on governance, strategy, risk management, and metrics related to climate risks and opportunities.',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.2',
        name: '9.2 EU Taxonomy & Sustainable Activities',
        description: 'EU Taxonomy for sustainable activities provides classification system defining environmentally sustainable economic activities based on technical screening criteria for climate change mitigation and adaptation.',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.3',
        name: '9.3 Sustainable Finance Disclosure (SFDR)',
        description: 'Sustainable Finance Disclosure Regulation (SFDR) requires financial market participants to disclose how they integrate sustainability risks and consider adverse sustainability impacts in investment decisions.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.4',
        name: '9.4 Climate Stress Testing & Scenario Analysis',
        description: 'Climate stress testing and scenario analysis assess portfolio resilience under various climate scenarios including orderly transition, disorderly transition, and physical risk scenarios over short, medium, and long-term horizons.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.5',
        name: '9.5 Physical Climate Risk Assessment',
        description: 'Physical climate risk assessment evaluates exposure to acute physical risks (extreme weather events, floods, wildfires) and chronic physical risks (temperature changes, sea level rise, water stress) affecting assets and operations.',
        paragraphsAnalyzed: 5234,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.6',
        name: '9.6 Transition Risk Assessment',
        description: 'Transition risk assessment examines exposure to policy and regulatory changes, technological disruption, market sentiment shifts, and reputational damage associated with transition to low-carbon economy.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.7',
        name: '9.7 Green Asset Ratio & Taxonomy Alignment',
        description: 'Green asset ratio measures proportion of banking book exposures financing taxonomy-aligned economic activities, providing transparency on alignment with environmental objectives.',
        paragraphsAnalyzed: 4987,
        overlapCount: 10,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.8',
        name: '9.8 Carbon-Intensive Sector Exposure',
        description: 'Carbon-intensive sector exposure monitoring tracks lending and investment in high-emission sectors including fossil fuels, energy-intensive manufacturing, and transportation, assessing transition risk concentration.',
        paragraphsAnalyzed: 5321,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.9',
        name: '9.9 Environmental & Social Due Diligence',
        description: 'Environmental and social due diligence in lending and investment decisions assesses environmental impacts, social considerations, and governance factors, integrating ESG criteria into credit risk assessment.',
        paragraphsAnalyzed: 5456,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.10',
        name: '9.10 Climate Risk Integration in Risk Management',
        description: 'Climate risk integration incorporates climate-related financial risks into existing risk management frameworks including credit risk models, capital planning, risk appetite, and strategic planning.',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'conduct-consumer',
    name: 'Conduct, Consumer Protection & Market Integrity',
    icon: 'Scale',
    regulationCount: 6851,
    subCategoryCount: 10,
    overlapCount: 65,
    contradictionCount: 1,
    description: 'Conduct risk encompasses potential for inappropriate, unethical, or unlawful behavior by institutions or employees that results in poor customer outcomes, market integrity breaches, or reputational damage.',
    subCategories: [
      {
        id: '10.1',
        name: '10.1 Consumer Protection & Fair Treatment',
        description: 'Consumer protection and fair treatment principles ensure customers are treated fairly throughout product lifecycle, from design and marketing through sales, servicing, and complaints handling.',
        paragraphsAnalyzed: 6234,
        overlapCount: 15,
        contradictionCount: 0,
        regulations: [
          { id: 'MiFID-II-Art-24', name: 'MiFID II Article 24 - General Principles', similarityScore: 0.92, description: 'General principles for acting in client\'s best interest' },
          { id: 'IDD-Art-17', name: 'IDD Article 17 - General Principle', similarityScore: 0.90, description: 'Insurance distribution conduct requirements' },
          { id: 'CCD-Art-5', name: 'Consumer Credit Directive Article 5', similarityScore: 0.88, description: 'Pre-contractual information requirements' },
          { id: 'UCPD', name: 'Unfair Commercial Practices Directive', similarityScore: 0.85, description: 'Protection against unfair commercial practices' }
        ],
        overlaps: [
          {
            id: 'overlap-10-1',
            regulationPair: ['MiFID II Article 24', 'IDD Article 17'],
            type: 'Duplicate',
            description: 'Similar fair treatment principles applied to investment services and insurance distribution.',
            confidenceScore: 0.89,
            excerpts: {
              regulation1: 'Investment firms shall act honestly, fairly and professionally in accordance with the best interests of their clients...',
              regulation2: 'Insurance distributors shall always act honestly, fairly and professionally in accordance with the best interests of their customers...'
            }
          },
          {
            id: 'overlap-10-2',
            regulationPair: ['Consumer Credit Directive Article 5', 'MiFID II Article 24'],
            type: 'Complementary',
            description: 'Both require clear information disclosure but for different product types.',
            confidenceScore: 0.86,
            excerpts: {
              regulation1: 'Prior to the conclusion of the credit agreement, the creditor shall provide the consumer with adequate explanations...',
              regulation2: 'Investment firms shall provide clients with information that is fair, clear and not misleading...'
            }
          }
        ],
        contradictions: []
      },
      {
        id: '10.2',
        name: '10.2 Product Governance & Oversight',
        description: 'Product governance and oversight frameworks ensure products are designed to meet identified customer needs, distributed through appropriate channels, and regularly reviewed for continued suitability.',
        paragraphsAnalyzed: 5789,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.3',
        name: '10.3 Suitability & Appropriateness Assessment',
        description: 'Suitability and appropriateness assessments under MiFID II ensure investment products and services match customer knowledge, experience, financial situation, and investment objectives.',
        paragraphsAnalyzed: 5432,
        overlapCount: 12,
        contradictionCount: 1,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.4',
        name: '10.4 Disclosure & Transparency Requirements',
        description: 'Disclosure and transparency requirements ensure customers receive clear, accurate, and timely information about products, services, fees, risks, and terms enabling informed decision-making.',
        paragraphsAnalyzed: 5987,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.5',
        name: '10.5 Sales Practices & Mis-selling Prevention',
        description: 'Sales practices and mis-selling prevention controls ensure products are sold appropriately without misleading information, aggressive tactics, or conflicts of interest compromising customer interests.',
        paragraphsAnalyzed: 5678,
        overlapCount: 13,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.6',
        name: '10.6 Complaints Handling & Redress',
        description: 'Complaints handling and redress mechanisms provide accessible, fair, and timely resolution of customer complaints, with appropriate compensation when harm is identified.',
        paragraphsAnalyzed: 5234,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.7',
        name: '10.7 Market Abuse & Insider Trading',
        description: 'Market abuse and insider trading regulations under Market Abuse Regulation (MAR) prohibit insider dealing, unlawful disclosure of inside information, and market manipulation ensuring market integrity.',
        paragraphsAnalyzed: 6123,
        overlapCount: 14,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.8',
        name: '10.8 Anti-Money Laundering (AML) & KYC',
        description: 'Anti-money laundering (AML) and know-your-customer (KYC) requirements under AML Directives mandate customer due diligence, transaction monitoring, suspicious activity reporting, and sanctions screening.',
        paragraphsAnalyzed: 6789,
        overlapCount: 16,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.9',
        name: '10.9 Conflicts of Interest in Investment Services',
        description: 'Conflicts of interest in investment services must be identified, managed, and disclosed under MiFID II, ensuring customer interests are prioritized and inducements do not compromise advice quality.',
        paragraphsAnalyzed: 5456,
        overlapCount: 12,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.10',
        name: '10.10 Vulnerable Customers & Financial Inclusion',
        description: 'Vulnerable customers and financial inclusion considerations ensure appropriate treatment of customers in vulnerable circumstances and promote access to essential financial services for all segments of society.',
        paragraphsAnalyzed: 5321,
        overlapCount: 11,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  }
];
