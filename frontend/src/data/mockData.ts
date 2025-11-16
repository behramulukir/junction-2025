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
  {
    id: 'credit-risk',
    name: 'Credit Risk',
    icon: 'TrendingDown',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Credit risk encompasses the potential for financial loss arising from a borrower's failure to meet contractual obligations, counterparty default, credit quality deterioration, or downgrade events. This includes assessment of creditworthiness, probability of default (PD), loss given default (LGD), exposure at default (EAD), expected credit losses under IFRS 9, credit risk mitigation techniques including collateral and guarantees, credit concentration to individual borrowers or groups of connected clients, impairment and provisioning requirements, non-performing loans (NPL) management, forbearance measures, restructuring of exposures, securitization credit risk, and counterparty credit risk arising from derivatives, securities financing transactions, and off-balance sheet exposures.",
    subCategories: [
      {
        id: '1.1',
        name: 'Credit Assessment & Underwriting Standards',
        description: "Credit assessment and underwriting standards govern the evaluation of borrower creditworthiness before granting credit, including know-your-customer (KYC) requirements, financial statement analysis, cash flow assessment, debt service coverage ratios, loan-to-value (LTV) ratio limits, debt-to-income (DTI) ratio thresholds for consumer lending, credit scoring models and rating systems, assessment of repayment capacity and ability to pay, collateral valuation methodologies, documentation requirements for loan origination, underwriting criteria and approval authorities, credit application processing, assessment of borrower's business model and industry risks, guarantor assessment, and responsible lending obligations ensuring borrowers are not granted unaffordable credit. This includes mortgage underwriting standards, consumer credit assessment under Consumer Credit Directive, and commercial lending due diligence.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.2',
        name: 'Credit Risk Mitigation Techniques',
        description: "Credit risk mitigation (CRM) techniques reduce credit exposure through funded protection such as cash collateral, financial collateral including bonds and equities, real estate mortgages, netting agreements, and unfunded protection including guarantees, credit derivatives, credit default swaps, and credit insurance. Regulatory requirements cover eligibility criteria for recognized CRM, legal certainty and enforceability of security interests, collateral valuation and revaluation frequency, haircuts applied to collateral values, margin requirements and variation margin, credit quality of protection providers, operational requirements for on-balance sheet netting, master netting agreements under ISDA frameworks, substitution and concentration limits for collateral, wrong-way risk where collateral value correlates with obligor default, documentation standards, and regulatory capital relief calculations for recognized CRM techniques under the Capital Requirements Regulation (CRR).",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.3',
        name: 'Expected Credit Losses, Impairment & Provisioning',
        description: "Expected credit loss (ECL) framework under IFRS 9 requires institutions to recognize credit losses based on forward-looking information, including 12-month ECL for performing exposures in Stage 1, lifetime ECL for underperforming exposures with significant increase in credit risk in Stage 2, and lifetime ECL for credit-impaired assets in Stage 3. This encompasses staging criteria and transfers between stages, indicators of significant increase in credit risk (SICR) including quantitative thresholds and qualitative factors, incorporation of forward-looking macroeconomic scenarios and probability weighting, calculation of probability of default (PD), loss given default (LGD), and exposure at default (EAD) parameters, discounting of expected cash flows, treatment of modifications and restructuring, collective versus individual assessment, write-off policies, provisioning adequacy assessment by supervisors, Pillar 2 guidance on provisions, prudential filters and regulatory adjustments, and disclosure requirements on credit quality and allowance movements.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.4',
        name: 'Non-Performing Exposures & Forbearance',
        description: "Non-performing exposure (NPE) management includes definition of default under Article 178 CRR with 90 days past due threshold and unlikeliness to pay criteria, classification of non-performing loans (NPL) and non-performing advances, forbearance measures as concessions to borrowers in financial difficulty including payment holidays, term extensions, interest rate reductions, and principal forgiveness, performing and non-performing forborne exposures, probation period before forborne exposures exit non-performing status, cure criteria and return to performing status, NPE coverage ratios and provisioning expectations, NPE reduction strategies and workout processes, distressed debt restructuring, recovery and resolution procedures, collateral enforcement and repossession, loan sales and portfolio transactions, servicing of NPEs, regulatory reporting of asset quality metrics, NPE calendar provisioning backstops requiring time-based provisions, and supervisory expectations on NPE management frameworks under ECB guidance.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.5',
        name: 'Counterparty Credit Risk (CCR)',
        description: "Counterparty credit risk (CCR) arises from derivatives, securities financing transactions (SFT) including repurchase agreements and securities lending, long settlement transactions, and other transactions where future exposure varies with market factors. CCR-specific requirements include calculation of exposure at default using current exposure method (CEM), standardized approach for CCR (SA-CCR), internal model method (IMM), effective expected positive exposure (EEPE), default risk charge for derivatives under Fundamental Review of the Trading Book (FRTB), central counterparty (CCP) exposure treatment and default fund contributions, bilateral margining requirements under EMIR for non-cleared derivatives including initial margin and variation margin, credit valuation adjustment (CVA) risk capital charge, wrong-way risk where exposure increases when counterparty credit quality deteriorates, collateral management for derivatives, netting sets and margin agreements, exposure aggregation across product types, and stress testing of CCR exposures.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.6',
        name: 'Securitization Credit Risk',
        description: "Securitization credit risk involves the transfer of credit risk through structured finance instruments including asset-backed securities (ABS), mortgage-backed securities (MBS), collateralized loan obligations (CLO), and synthetic securitizations. Regulatory framework covers originator, sponsor, and investor requirements, due diligence obligations on underlying exposures, risk retention rules requiring 5% retention of economic interest, prohibition on re-securitization except for asset-backed commercial paper (ABCP), disclosure requirements on underlying pools, homogeneity criteria for securitized portfolios, capital treatment using securitization internal ratings-based approach (SEC-IRBA), securitization external ratings-based approach (SEC-ERBA), and securitization standardized approach (SEC-SA), significant risk transfer (SRT) assessment for regulatory capital relief, senior positions in securitizations, treatment of securitization positions in trading book and banking book, Simple, Transparent and Standardized (STS) securitization framework with preferential capital treatment, and assessment of credit quality steps.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.7',
        name: 'Credit Risk Internal Models & IRB Approach',
        description: "Internal ratings-based (IRB) approach allows banks to use internal models for credit risk capital calculation, covering foundation IRB (F-IRB) where banks estimate probability of default (PD) and supervisors provide loss given default (LGD) and exposure at default (EAD), and advanced IRB (A-IRB) where banks estimate all parameters. Requirements include rating system design with sufficient rating grades and default definition consistency, data requirements with minimum historical observation periods typically five years for PD and seven years for LGD, model validation and backtesting, stress testing and economic downturn LGD estimation, treatment of guarantees and credit derivatives in LGD estimation, default and loss identification, margin of conservatism in parameter estimates, supervisory approval processes, ongoing monitoring and model performance, use test ensuring models are embedded in credit decision-making and management, model governance including independent validation, material model changes and extensions, permanent partial use and rollout plans, and output floor limiting capital benefits.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.8',
        name: 'Credit Risk Standardized Approaches & RWA',
        description: "Standardized approach for credit risk assigns risk weights to exposures based on exposure class and external credit ratings, including sovereigns and central banks typically 0% risk weight, institutions with risk weights varying from 20% to 150% based on credit quality, corporate exposures typically 100% risk weight or rated-based weights, retail exposures at 75% risk weight with granularity criteria, exposures secured by residential mortgages typically 35% risk weight, commercial real estate at higher weights, equity exposures at 100% or higher, off-balance sheet items with credit conversion factors (CCF), unfunded credit protection treatment, and risk weight floors. This includes revised standardized approach under CRR II with increased risk sensitivity, external credit assessment institution (ECAI) mapping, preferential treatment for small and medium enterprises (SME) with SME supporting factor, infrastructure supporting factor, regulatory retail exposures criteria, specialized lending including project finance, object finance, commodities finance, and income-producing real estate, and calculation of total risk-weighted assets (RWA).",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.9',
        name: 'Credit Derivatives & Credit Protection',
        description: "Credit derivatives used for credit risk transfer and hedging include credit default swaps (CDS) providing protection against credit events such as default, bankruptcy, or restructuring, total return swaps exchanging total economic performance, credit-linked notes embedding credit risk, first-to-default baskets, and nth-to-default structures. Requirements cover eligible credit protection under CRM framework, recognition criteria including legal certainty and direct claim on protection provider, credit quality of protection seller with minimum ratings typically A- or equivalent, maturity mismatches and haircuts reducing protection value, currency mismatches between exposure and protection, restructuring credit events and modified restructuring clauses, materiality of restructuring triggers, tranched credit protection with attachment and detachment points, regulatory capital treatment of purchased and sold protection, CVA for credit derivatives, treatment of credit protection in securitizations, central clearing mandates under EMIR, and margining requirements.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '1.10',
        name: 'Credit Risk Stress Testing & Scenario Analysis',
        description: "Credit risk stress testing assesses portfolio resilience under adverse scenarios including macroeconomic downturns, sector-specific shocks, interest rate stress, unemployment increases, real estate price declines, and commodity price movements. Regulatory requirements include supervisory stress tests such as ECB/EBA stress testing exercises, internal stress testing under ICAAP and ILAAP, reverse stress testing identifying scenarios leading to business model failure, scenario design with baseline, adverse, and severely adverse scenarios, incorporation of second-round effects and feedback loops, assessment of credit migration across rating grades and stages, impact on expected credit losses and provisions, stressed PD, LGD and EAD parameters, concentration risk stress testing, sectoral and geographic stress scenarios, climate-related credit risk stress testing, stress testing of credit risk mitigation effectiveness, management actions and mitigants in stress scenarios, capital and liquidity impact assessment, and documentation and governance of stress testing frameworks.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
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
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Market risk represents the potential for losses due to adverse movements in market prices including interest rate fluctuations, foreign exchange rate volatility, equity price changes, commodity price movements, and credit spread variations. This encompasses trading book positions, fair value measurement requirements, value-at-risk (VaR) methodologies, stressed VaR calculations, internal models approach versus standardized approach for market risk capital, incremental risk charge (IRC), correlation trading activities, distinction between banking book and trading book, hedging strategies and hedge accounting, derivatives valuation, market liquidity risk during stressed conditions, and wrong-way risk where exposure and counterparty credit quality are adversely correlated.",
    subCategories: [
      {
        id: '2.1',
        name: 'Interest Rate Risk in the Trading Book',
        description: "Interest rate risk in the trading book arises from changes in interest rates affecting the value of trading positions including bonds, interest rate derivatives, and other rate-sensitive instruments. This encompasses delta risk from parallel shifts in yield curves, vega risk from changes in interest rate volatility, curvature risk from non-linear price changes, basis risk between different rate indices such as LIBOR versus OIS, spread risk between government and corporate bonds, and risks across different currencies and tenors. Regulatory requirements include the Fundamental Review of the Trading Book (FRTB) framework with sensitivities-based approach calculating risk charges for delta, vega and curvature across prescribed risk factors and buckets, internal models approach (IMA) subject to profit and loss attribution tests and backtesting, trading desk structure and approval processes, risk factor modellability assessment requiring real prices from multiple independent sources, non-modellable risk factors (NMRF) treatment with stressed calibration, and capital requirements for general interest rate risk and specific risk.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.2',
        name: 'Foreign Exchange Risk',
        description: "Foreign exchange (FX) risk represents exposure to adverse movements in currency exchange rates affecting the value of positions denominated in foreign currencies, including spot FX, FX forwards, FX swaps, currency options, and cross-currency basis swaps. This covers translation risk from converting foreign currency assets and liabilities, transaction risk from future foreign currency cash flows, economic risk from competitive position changes due to exchange rate movements, and risks in both major currency pairs and emerging market currencies. Requirements include calculation of net open foreign exchange positions aggregating long and short positions across currencies, capital charges under standardized approach typically 8% of net open position, treatment of structural FX positions in banking book, gold treatment as foreign currency, FX delta risk, FX vega risk and FX curvature risk under FRTB sensitivities-based approach, correlation assumptions between currency pairs, FX volatility risk from options positions, and stress testing of FX exposures including currency crisis scenarios.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.3',
        name: 'Equity Risk',
        description: "Equity risk arises from changes in equity prices affecting trading book positions in individual stocks, equity indices, equity derivatives including options and futures, equity swaps, and convertible bonds. This encompasses specific risk from individual issuer price movements, general market risk from broad equity market changes, sector concentration risk, geographic market exposures, and volatility risk from equity options. Regulatory framework covers equity delta risk with risk weights varying by market capitalization and liquidity, equity vega risk from implied volatility changes, equity curvature risk from non-linear exposures, correlation between equities within and across buckets based on sectors and regions, treatment of equity indices and index arbitrage positions, equity repo and securities lending exposures, dividend risk, and capital requirements under both standardized and internal models approaches. This includes assessment of large and concentrated equity positions, equity underwriting risk, and equity derivatives including exotic options.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.4',
        name: 'Commodity Risk',
        description: "Commodity risk involves exposure to price changes in physical commodities and commodity derivatives including energy products (crude oil, natural gas, electricity), precious metals (gold, silver, platinum), base metals (copper, aluminum, zinc), agricultural products (wheat, corn, soybeans), and other commodities. This covers directional risk from outright long or short positions, basis risk between different delivery locations or contract specifications, calendar spread risk between different delivery dates, volatility risk from commodity options, and liquidity risk in less liquid commodity markets. Requirements include commodity delta risk with separate treatment across commodity categories, commodity vega risk and curvature risk, correlation assumptions within and between commodity classes, treatment of commodity forwards and futures, energy-specific risks including spark spreads and crack spreads, storage costs and convenience yields, physical delivery obligations, and capital charges under FRTB framework with prescribed risk weights and correlation parameters for different commodity types.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.5',
        name: 'Credit Spread Risk in Trading Book',
        description: "Credit spread risk in the trading book represents exposure to changes in credit spreads affecting the value of corporate bonds, credit derivatives, securitization positions, and other credit-sensitive instruments held for trading. This encompasses spread widening risk from credit quality deterioration, jump-to-default risk from sudden default events, credit migration risk from rating changes, and basis risk between cash bonds and credit default swaps. Regulatory requirements under FRTB include credit spread delta risk with risk weights based on credit quality (investment grade versus high yield), sector, and tenor, credit spread vega risk from credit volatility changes, credit spread curvature risk, correlation between issuers within sectors and across sectors, treatment of securitization positions with separate risk weights, distinction from credit risk in banking book, default risk charge (DRC) capturing jump-to-default risk with prescribed loss-given-default assumptions, and integration with counterparty credit risk for derivatives positions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.6',
        name: 'Value-at-Risk (VaR) & Risk Metrics',
        description: "Value-at-Risk (VaR) measures the maximum potential loss over a specified time horizon at a given confidence level, typically 99% confidence over 10 trading days for regulatory capital. This encompasses historical simulation VaR using past market movements, parametric VaR assuming normal distributions, Monte Carlo VaR using simulated scenarios, stressed VaR (SVaR) calibrated to a 12-month stressed period, incremental risk charge (IRC) capturing default and migration risk over one-year horizon, and comprehensive risk measure (CRM) for correlation trading. Requirements include daily VaR calculation and reporting, backtesting comparing VaR predictions to actual profit and loss with traffic light approach triggering multiplier increases for excessive breaches, profit and loss attribution tests comparing risk-theoretical P&L to actual P&L, model validation and independent review, treatment of diversification benefits, risk factor selection and proxies, data quality and historical observation periods, and regulatory multiplier (typically 3 or higher) applied to VaR for capital calculation.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.7',
        name: 'Trading Book vs Banking Book Boundary',
        description: "The boundary between trading book and banking book determines which positions are subject to market risk capital requirements versus credit risk capital requirements, with significant implications for capital treatment and risk management. Trading book includes positions held with trading intent, for short-term profit-taking, hedging other trading book positions, or market-making activities, while banking book contains positions held to maturity, relationship banking loans, and structural positions. Regulatory requirements under FRTB include presumptive lists of trading book instruments (derivatives, trading securities) and banking book instruments (loans, deposits), internal risk transfer (IRT) framework allowing hedging between books with strict documentation and approval, prohibition on regulatory arbitrage through artificial assignment, restrictions on switching positions between books, valuation requirements with daily mark-to-market for trading book, prudent valuation adjustments (PVA) for trading book positions, and supervisory approval for trading desk structure and boundary policies.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.8',
        name: 'Market Liquidity Risk',
        description: "Market liquidity risk is the risk that institutions cannot easily offset or eliminate positions without significantly affecting market prices due to inadequate market depth or market disruptions. This encompasses bid-ask spread widening during stress, inability to exit large positions without material price impact, market gaps and discontinuities, reduced trading volumes, and potential for fire sales. Requirements include liquidity horizons in capital calculations with longer horizons for less liquid positions ranging from 10 days for liquid instruments to 120 days for illiquid positions under FRTB, assessment of market depth and concentration, stress testing of market liquidity including scenarios where normal liquidity disappears, contingency planning for illiquid positions, limits on illiquid and concentrated positions, valuation adjustments for illiquid positions, exit strategies and wind-down plans, and distinction between market liquidity risk and funding liquidity risk though recognizing their interaction during stress events.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.9',
        name: 'Hedging Strategies & Hedge Accounting',
        description: "Hedging strategies aim to reduce market risk exposures through offsetting positions, while hedge accounting allows matching of gains and losses on hedging instruments with hedged items. This covers fair value hedges protecting against changes in fair value of assets, liabilities or firm commitments, cash flow hedges protecting against variability in future cash flows, hedges of net investments in foreign operations, micro-hedges of individual exposures, and macro-hedges of portfolios. Requirements under IAS 39 and IFRS 9 include hedge designation and documentation at inception, formal assessment of hedge effectiveness both prospectively and retrospectively, hedge effectiveness testing with 80-125% effectiveness range under IAS 39 or economic relationship under IFRS 9, treatment of hedge ineffectiveness in profit and loss, rebalancing of hedge relationships, discontinuation criteria, dynamic risk management and portfolio hedging approaches, and regulatory treatment of hedging instruments in capital calculations including recognition of hedging benefits and treatment of basis risk.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '2.10',
        name: 'Market Risk Stress Testing & Scenario Analysis',
        description: "Market risk stress testing evaluates the impact of extreme but plausible market movements on trading portfolios including historical scenarios (2008 financial crisis, COVID-19 market shock), hypothetical scenarios (interest rate shocks, equity crashes, currency crises), and reverse stress tests identifying scenarios causing critical losses. This encompasses multi-factor stress scenarios with simultaneous moves across risk types, correlation breakdown scenarios where diversification benefits disappear, volatility spikes, liquidity stress with widened bid-ask spreads, emerging market crises, sovereign debt crises, and climate-related market shocks. Requirements include regular stress testing at trading desk and firm-wide levels, integration with ICAAP and recovery planning, stress testing of complex and illiquid positions, assessment of concentration risks, second-round effects including margin calls and collateral requirements, management actions in stress scenarios, stress testing governance and independent review, documentation of scenarios and assumptions, and use of stress test results in risk appetite setting, limit frameworks, and strategic decision-making.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'liquidity--funding-risk',
    name: 'Liquidity & Funding Risk',
    icon: 'Droplet',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Liquidity and funding risk involves the inability to meet payment obligations when due without incurring unacceptable losses, or the inability to fund assets at a reasonable cost. This includes liquidity coverage ratio (LCR) requirements ensuring sufficient high-quality liquid assets to survive acute stress, net stable funding ratio (NSFR) promoting stable funding structures, intraday liquidity management, contingency funding plans and stress testing, maturity transformation risks, funding concentration from single sources or markets, encumbrance of assets affecting liquidity position, collateral management and margin requirements, access to central bank facilities, deposit stability analysis, wholesale funding dependencies, and contractual versus behavioral maturity mismatches between assets and liabilities.",
    subCategories: [
      {
        id: '3.1',
        name: 'Liquidity Coverage Ratio (LCR)',
        description: "The Liquidity Coverage Ratio (LCR) requires institutions to maintain sufficient high-quality liquid assets (HQLA) to survive a 30-day acute liquidity stress scenario, with minimum requirement of 100%. HQLA includes Level 1 assets such as central bank reserves, government bonds with 0% haircut, Level 2A assets including covered bonds and corporate bonds rated AA- or higher with 15% haircut capped at 40% of total HQLA, and Level 2B assets including lower-rated corporate bonds, residential mortgage-backed securities, and equities with higher haircuts capped at 15% of total HQLA. Net cash outflows encompass retail deposit runoff rates varying by stability and coverage (3-10% for stable deposits, 10-40% for less stable), wholesale funding runoff rates (typically 100% for unsecured wholesale funding from financial institutions, 25-100% for operational deposits), committed credit and liquidity facilities drawdown assumptions, derivative collateral calls, and contractual obligations. Requirements include daily monitoring and reporting, currency-specific LCR for material currencies, treatment of intragroup transactions, and supervisory expectations for maintaining buffers above minimum.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.2',
        name: 'Net Stable Funding Ratio (NSFR)',
        description: "The Net Stable Funding Ratio (NSFR) promotes stable funding structures by requiring available stable funding (ASF) to exceed required stable funding (RSF) over a one-year horizon, with minimum 100% requirement. ASF includes capital and liabilities with remaining maturity over one year receiving 100% ASF factor, stable retail deposits and certain wholesale deposits receiving 90-95% factors, less stable deposits receiving 90% factor, and wholesale funding with maturity under one year receiving lower factors (50% for operational deposits, 0% for other short-term wholesale funding). RSF depends on asset liquidity and remaining maturity, with cash and central bank reserves requiring 0% RSF, government bonds requiring 5% RSF, covered bonds and corporate bonds requiring 15-50% RSF depending on rating and maturity, performing loans requiring 65-85% RSF, and unencumbered assets available for immediate sale or pledging receiving lower RSF factors. This includes treatment of derivatives, off-balance sheet exposures, interdependencies with LCR, and restrictions on double-counting of liquid assets.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.3',
        name: 'Intraday Liquidity Management',
        description: "Intraday liquidity management ensures institutions can meet payment and settlement obligations throughout the business day without disrupting operations or incurring losses. This encompasses real-time monitoring of intraday liquidity positions across accounts, payment systems (TARGET2, CHAPS, Fedwire), and currencies, management of payment flows and timing, optimization of collateral usage for intraday credit facilities, coordination between treasury and operations, and contingency arrangements for intraday stress. Requirements include identification of peak intraday liquidity needs, monitoring of time-specific obligations including large-value payments and securities settlements, assessment of available intraday liquidity sources such as central bank facilities and correspondent banking arrangements, collateral mobilization capabilities, stress testing of intraday liquidity including operational disruptions and participant defaults in payment systems, governance and escalation procedures for intraday liquidity issues, and reporting obligations to supervisors on intraday liquidity risk management frameworks and key metrics.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.4',
        name: 'Contingency Funding Plan & Stress Testing',
        description: "Contingency funding plans (CFP) establish strategies and procedures for responding to liquidity stress events, ensuring institutions can continue to meet obligations during disruptions. This includes identification of early warning indicators such as credit rating downgrades, widening CDS spreads, increased funding costs, deposit outflows, and negative media coverage, escalation procedures and crisis management governance with clear roles and responsibilities, quantification of liquidity needs under stress scenarios ranging from institution-specific stress to market-wide crises, inventory of available liquidity sources including unencumbered assets, committed facilities, and central bank access, prioritization of actions including asset sales, liability management, and curtailment of activities, communication strategies with stakeholders including regulators, rating agencies, and counterparties, and regular testing and updating of plans. Stress testing encompasses idiosyncratic scenarios (reputation events, credit downgrades), market-wide scenarios (market disruptions, funding market freezes), combined scenarios, reverse stress tests, and assessment of funding concentrations, rollover risks, and contingent liquidity obligations.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.5',
        name: 'Maturity Transformation & Funding Gaps',
        description: "Maturity transformation involves funding long-term assets with shorter-term liabilities, creating maturity mismatches and rollover risk. This encompasses contractual maturity analysis showing legal maturity dates of assets and liabilities, behavioral maturity analysis incorporating expected customer behavior such as deposit stability and loan prepayments, cumulative funding gap analysis across time buckets identifying periods of net cash outflows, and assessment of refinancing risk when significant liabilities mature. Requirements include maturity ladder reporting across standardized time buckets from overnight to over 5 years, limits on maturity mismatches and cumulative gaps, distinction between liquid and illiquid assets in gap analysis, treatment of off-balance sheet items and contingent obligations, scenario analysis of behavioral assumptions under stress, assessment of term funding needs, diversification of maturity profile avoiding excessive concentration in specific maturity buckets, and integration with interest rate risk in banking book (IRRBB) management given the interaction between maturity transformation and interest rate exposure.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.6',
        name: 'Funding Concentration & Diversification',
        description: "Funding concentration risk arises from over-reliance on specific funding sources, counterparties, instruments, currencies, or markets, creating vulnerability if access is disrupted. This includes concentration to individual depositors or creditors with limits typically set relative to total funding or capital, concentration to funding instruments such as excessive reliance on short-term wholesale funding, commercial paper, or repos, concentration to specific markets or currencies creating rollover risk if market access is impaired, concentration to related counterparties or groups, and time concentration with large amounts maturing simultaneously. Requirements include identification and monitoring of funding concentrations across multiple dimensions, limits on concentrations with escalation when approaching thresholds, diversification strategies across funding sources, instruments, tenors, currencies, and investor types, assessment of funding market capacity and institution's share, contingency plans for loss of concentrated funding sources, stress testing of concentration risks, and regular reporting to senior management and board on funding composition and concentration metrics.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.7',
        name: 'Asset Encumbrance & Collateral Management',
        description: "Asset encumbrance occurs when assets are pledged as collateral or otherwise restricted, reducing available unencumbered assets for liquidity management and potentially signaling financial stress. This encompasses encumbrance from secured funding transactions including covered bonds, securitizations, and repos, collateral posted for derivatives under CSA agreements, margin requirements for centrally cleared derivatives, assets pledged to central banks for access to facilities, and assets backing deposit guarantee schemes. Requirements include monitoring and reporting of encumbrance levels with metrics such as encumbered assets as percentage of total assets (supervisory expectations typically below 25-30% in normal times), distinction between encumbered and unencumbered assets by quality and liquidity, assessment of over-collateralization in secured funding, collateral upgrade and downgrade triggers, collateral substitution rights, legal and operational arrangements for mobilizing collateral, stress testing of encumbrance including scenarios with increased margin calls and haircuts, disclosure requirements on asset encumbrance, and management of encumbrance levels to maintain sufficient unencumbered HQLA for LCR compliance.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.8',
        name: 'Deposit Stability & Retail Funding',
        description: "Deposit stability analysis assesses the reliability of retail and corporate deposits as funding sources, considering customer behavior during normal and stressed conditions. This includes classification of retail deposits into stable deposits (covered by deposit guarantee schemes, established customer relationships, transactional accounts) receiving lower runoff rates, and less stable deposits (high-value accounts, internet-only accounts, non-resident deposits) with higher runoff assumptions, analysis of corporate operational deposits from clearing, custody, and cash management services receiving preferential treatment due to stickiness, and assessment of wholesale deposits from financial institutions and corporates typically assumed to run off rapidly in stress. Requirements include granular deposit analysis by customer segment, product type, coverage by deposit guarantee schemes, and geographic location, monitoring of deposit concentration to large depositors, early warning indicators of deposit flight such as declining balances or increased withdrawal requests, pricing strategies balancing funding needs with profitability, customer relationship management to enhance stickiness, stress testing of deposit runoff under various scenarios, and validation of behavioral assumptions through historical analysis and peer benchmarking.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.9',
        name: 'Wholesale Funding & Market Access',
        description: "Wholesale funding includes unsecured and secured borrowing from financial institutions, corporates, and institutional investors through instruments such as interbank deposits, commercial paper, certificates of deposit, medium-term notes, covered bonds, securitizations, and repos. This encompasses assessment of wholesale funding stability with recognition that most wholesale funding is less stable than retail deposits, diversification across investor types and markets, term funding strategies to reduce rollover frequency, relationship management with key investors and counterparties, and monitoring of market conditions and access. Requirements include limits on wholesale funding as percentage of total funding, minimum term funding requirements, monitoring of rollover success rates and funding costs as early warning indicators, assessment of funding capacity in different markets, contingency arrangements for loss of market access, participation in multiple funding markets to maintain optionality, credit rating considerations given investor requirements, disclosure and transparency to maintain investor confidence, and stress testing of wholesale funding availability including scenarios where markets freeze or become accessible only at prohibitive costs.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '3.10',
        name: 'Central Bank Facilities & Lender of Last Resort',
        description: "Central bank facilities provide liquidity support through standing facilities, open market operations, and emergency lending, serving as backstop for solvent institutions facing temporary liquidity stress. This includes standing deposit and lending facilities available at penalty rates, main refinancing operations providing regular liquidity against eligible collateral, longer-term refinancing operations (LTRO, TLTRO) with extended maturities, marginal lending facilities for overnight borrowing, discount window access in some jurisdictions, and emergency liquidity assistance (ELA) for solvent institutions facing acute stress. Requirements include maintaining operational readiness to access facilities through pre-positioning of collateral, understanding eligibility criteria for collateral with haircuts applied based on asset quality and liquidity, legal documentation and operational procedures, regular testing of access mechanisms, assessment of available collateral and potential borrowing capacity, treatment of central bank funding in liquidity metrics (typically not counted as stable funding in NSFR, but eligible collateral supports LCR), stigma considerations that may deter usage during stress, and coordination with supervisors given that emergency access may trigger enhanced oversight.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
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
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Operational risk is the risk of loss resulting from inadequate or failed internal processes, human errors, system failures, or external events including natural disasters. This covers business continuity planning and disaster recovery, fraud prevention including internal fraud and external fraud, employment practices and workplace safety, damage to physical assets, business disruption and system failures, execution errors and process breakdowns, transaction processing failures, product flaws and fiduciary breaches, outsourcing risk from third-party service providers, legal risk from litigation and regulatory penalties, conduct risk from employee behavior, key person risk and succession planning, and operational resilience ensuring critical services remain within tolerance during disruption.",
    subCategories: [
      {
        id: '4.1',
        name: 'Internal Fraud',
        description: "Internal fraud involves intentional acts by employees or insiders to defraud, misappropriate assets, or circumvent regulations, laws, or company policies, excluding discrimination and diversity events. This encompasses unauthorized trading activities including rogue trading and exceeding position limits, theft and embezzlement of cash or assets, fraudulent loan origination or credit decisions for personal benefit, manipulation of financial records or reporting, bribery and kickbacks from vendors or customers, insider trading using confidential information, falsification of documents or signatures, unauthorized access to systems or data for fraudulent purposes, and collusion between employees or with external parties. Prevention and detection measures include segregation of duties preventing single individuals from controlling entire processes, maker-checker controls requiring independent verification, access controls and system permissions based on least privilege principle, monitoring of employee activities and transactions for unusual patterns, whistleblower programs and anonymous reporting channels, background checks and screening during hiring, mandatory vacation policies forcing job rotation, regular audits and surprise inspections, and disciplinary procedures including termination and legal action when fraud is detected.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.2',
        name: 'External Fraud',
        description: "External fraud results from intentional acts by third parties to defraud, misappropriate assets, or circumvent laws, including theft, robbery, forgery, check kiting, and electronic fraud. This encompasses payment fraud including card fraud, check fraud, and wire transfer fraud, identity theft and account takeover where criminals impersonate legitimate customers, phishing and social engineering attacks tricking employees or customers into revealing credentials or authorizing transactions, business email compromise (BEC) targeting payment processes, ATM skimming and physical theft, counterfeit currency and instruments, loan fraud with false information or documentation, insurance fraud with false claims, vendor and supplier fraud, and money laundering attempts using the institution. Controls include customer authentication mechanisms such as multi-factor authentication, transaction monitoring systems detecting unusual patterns, velocity checks limiting transaction frequency and amounts, verification procedures for high-risk transactions, employee training on fraud indicators and social engineering tactics, collaboration with law enforcement and industry groups, fraud detection analytics using machine learning, customer education on security practices, and incident response procedures for confirmed fraud including account freezing, fund recovery, and regulatory reporting.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.3',
        name: 'Employment Practices & Workplace Safety',
        description: "Employment practices and workplace safety risk arises from acts inconsistent with employment, health, or safety laws or agreements, including workers compensation claims, discrimination, harassment, and workplace safety violations. This includes discrimination based on protected characteristics such as race, gender, age, religion, or disability in hiring, promotion, compensation, or termination decisions, sexual harassment and hostile work environment, wrongful termination and unfair dismissal claims, violation of labor laws including wage and hour regulations, failure to provide safe working conditions leading to injuries or occupational illnesses, inadequate training on safety procedures and equipment, non-compliance with health and safety regulations, retaliation against whistleblowers or complainants, failure to accommodate disabilities, and violations of employee privacy rights. Risk management includes comprehensive employment policies and codes of conduct, regular training on discrimination, harassment, and workplace safety, clear reporting mechanisms and investigation procedures for complaints, health and safety programs with risk assessments and protective equipment, workers compensation insurance, legal review of employment decisions, documentation of performance issues and disciplinary actions, diversity and inclusion initiatives, ergonomic assessments, and regular audits of compliance with employment and safety regulations.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.4',
        name: 'Clients, Products & Business Practices',
        description: "Risks from clients, products, and business practices include unintentional or negligent failures to meet professional obligations to clients, or from the nature or design of products. This encompasses mis-selling of products unsuitable for customer needs or risk profiles, inadequate disclosure of product features, risks, or costs, breach of fiduciary duties or advisory obligations, improper sales practices including aggressive tactics or misleading representations, product design flaws creating unexpected risks or customer detriment, inadequate product governance and oversight, failure to conduct suitability or appropriateness assessments, conflicts of interest not properly managed or disclosed, churning or excessive trading generating commissions, unauthorized trading or exceeding customer mandates, errors in account administration or transaction processing, failure to execute customer instructions properly, privacy breaches exposing customer information, and reputational damage from poor customer outcomes. Controls include robust product approval processes with customer outcome assessments, suitability and appropriateness testing frameworks, clear product documentation and disclosure, sales process monitoring and quality assurance, training and competence requirements for customer-facing staff, conflicts of interest policies, complaint handling and root cause analysis, regular product reviews, mystery shopping programs, and regulatory compliance monitoring.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.5',
        name: 'Damage to Physical Assets',
        description: "Damage to physical assets results from natural disasters or other events causing loss or damage to physical property including buildings, equipment, and infrastructure. This encompasses natural disasters such as earthquakes, floods, hurricanes, tornadoes, and wildfires, terrorism and vandalism, fire and explosions, water damage from burst pipes or flooding, power failures and electrical issues, structural failures or building collapse, damage to IT infrastructure and data centers, damage to ATMs and branch facilities, loss of transportation assets, and environmental contamination. Risk mitigation includes property insurance with adequate coverage limits and appropriate deductibles, business continuity planning with alternate facilities and work arrangements, preventive maintenance programs, physical security measures including surveillance and access controls, fire suppression and detection systems, backup power generators and uninterruptible power supplies (UPS), geographic diversification of critical facilities, building standards and seismic reinforcement in high-risk areas, emergency response procedures, regular inspections and risk assessments of facilities, and coordination with emergency services and authorities.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.6',
        name: 'Business Disruption & System Failures',
        description: "Business disruption and system failures involve disruption of business operations or system failures including hardware, software, telecommunications, and utility outages. This encompasses IT system outages affecting core banking systems, payment processing, or trading platforms, hardware failures including servers, storage, and network equipment, software bugs and application errors, telecommunications failures disrupting connectivity, utility outages including power, water, or HVAC systems, capacity issues from insufficient system resources, performance degradation affecting service levels, failed system changes or upgrades, integration issues between systems, vendor or third-party service provider failures, cloud service disruptions, and cascading failures where one system failure triggers others. Resilience measures include redundant systems and failover capabilities, high availability architectures with no single points of failure, disaster recovery sites with regular testing, backup and recovery procedures with defined recovery time objectives (RTO) and recovery point objectives (RPO), change management processes with testing and rollback procedures, capacity planning and performance monitoring, incident management and escalation procedures, vendor management with service level agreements (SLAs) and penalties, regular system maintenance and patching, and business continuity arrangements ensuring critical services continue during disruptions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.7',
        name: 'Execution, Delivery & Process Management',
        description: "Execution, delivery, and process management failures result from failed transaction processing, process management errors, or disputes with trade counterparties and vendors. This includes transaction processing errors such as incorrect payments, duplicate transactions, or failed settlements, data entry mistakes and manual processing errors, reconciliation breaks and unmatched items, failed or delayed trade settlements, collateral management errors, corporate actions processing failures, reference data errors affecting pricing or risk calculations, document management failures including lost or misfiled documents, service level agreement breaches, vendor disputes over services or pricing, customer disputes over transactions or fees, operational losses from process inefficiencies, and errors in regulatory reporting. Controls include straight-through processing (STP) reducing manual intervention, automated reconciliations with exception reporting, four-eyes principle for critical transactions, transaction limits and approval authorities, process documentation and standard operating procedures, quality assurance and control checks, exception management and investigation procedures, key risk indicators (KRIs) monitoring error rates and processing times, root cause analysis of errors, process improvement initiatives including lean and six sigma methodologies, and training programs ensuring staff competence.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.8',
        name: 'Outsourcing & Third-Party Risk',
        description: "Outsourcing and third-party risk arises from reliance on external service providers for critical functions, creating dependencies and potential vulnerabilities. This encompasses IT outsourcing including cloud services, data centers, and application development, business process outsourcing such as payment processing, customer service, and back-office functions, professional services including legal, audit, and consulting, concentration risk from critical service providers, vendor financial stability and business continuity, data security and confidentiality at vendor sites, compliance with regulations by vendors, subcontracting and fourth-party risk, vendor lock-in and exit challenges, and cross-border outsourcing with jurisdictional issues. Risk management includes due diligence before vendor selection assessing capabilities, financial strength, security, and compliance, contractual protections including service levels, audit rights, data ownership, termination rights, and liability provisions, ongoing monitoring of vendor performance against SLAs, regular audits and assessments of vendor controls, business continuity requirements for vendors, information security requirements and testing, exit strategies and transition planning, vendor concentration limits, regulatory compliance including outsourcing notifications to supervisors, and governance with clear accountability for outsourced activities remaining with the institution.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.9',
        name: 'Legal & Regulatory Risk',
        description: "Legal and regulatory risk involves exposure to fines, penalties, or punitive damages resulting from supervisory actions or private settlements due to non-compliance with laws, regulations, or legal obligations. This encompasses violations of banking regulations including capital, liquidity, and large exposure requirements, anti-money laundering (AML) and counter-terrorist financing (CTF) breaches, sanctions violations and prohibited transactions, consumer protection violations, data protection and privacy breaches under GDPR or similar regulations, securities law violations, tax non-compliance, contractual disputes and litigation, intellectual property infringement, competition law violations, employment law breaches, and failure to obtain required licenses or approvals. Management includes legal and compliance functions with sufficient resources and authority, regulatory change management processes tracking and implementing new requirements, compliance monitoring and testing programs, legal review of products, services, and contracts, training on legal and regulatory obligations, policies and procedures aligned with legal requirements, incident reporting to regulators within required timeframes, engagement with regulators and supervisors, legal reserves for known litigation, and insurance coverage for legal risks where available.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '4.10',
        name: 'Operational Resilience & Business Continuity',
        description: "Operational resilience ensures critical operations and services remain within tolerance levels during disruption, enabling institutions to continue serving customers and meeting obligations. This encompasses identification of important business services based on customer impact, financial stability implications, and regulatory requirements, setting impact tolerances defining maximum acceptable disruption for each service, mapping dependencies including people, processes, technology, facilities, and third parties supporting critical services, scenario testing with severe but plausible disruptions including cyber attacks, pandemics, natural disasters, and loss of key infrastructure, response and recovery capabilities to restore services within tolerance, communication strategies with customers, regulators, and stakeholders during disruption, lessons learned and continuous improvement from incidents and tests, and governance with board and senior management oversight. Requirements under operational resilience frameworks include self-assessment of resilience capabilities, identification of vulnerabilities and single points of failure, investment in resilience improvements, documentation of playbooks and procedures, regular testing at least annually with realistic scenarios, coordination across business lines and support functions, third-party resilience requirements, and regulatory reporting on resilience capabilities and material incidents.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'capital-adequacy--solvency',
    name: 'Capital Adequacy & Solvency',
    icon: 'Circle',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Capital adequacy and solvency risk relates to maintaining sufficient capital resources to absorb unexpected losses and meet minimum regulatory requirements. This encompasses common equity tier 1 (CET1) capital as the highest quality loss-absorbing capital, additional tier 1 (AT1) capital instruments, tier 2 capital including subordinated debt, capital conservation buffer requiring institutions to build up capital in good times, countercyclical capital buffer varying with credit cycle, systemic risk buffers for systemically important institutions, leverage ratio as non-risk-based backstop measure, minimum requirement for own funds and eligible liabilities (MREL) for resolution planning, total loss-absorbing capacity (TLAC) for global systemically important banks, capital planning and stress testing, dividend restrictions when buffers are breached, and internal capital adequacy assessment process (ICAAP) under Pillar 2.",
    subCategories: [
      {
        id: '5.1',
        name: 'Common Equity Tier 1 (CET1) Capital',
        description: "Common Equity Tier 1 (CET1) capital represents the highest quality capital consisting primarily of common shares, retained earnings, accumulated other comprehensive income (AOCI), and other disclosed reserves, subject to regulatory adjustments and deductions. This encompasses paid-in common stock meeting criteria including perpetual nature, subordination to all other claims, discretionary dividends, and full loss absorption, retained earnings accumulated over time from profitable operations, other comprehensive income including fair value reserves, regulatory adjustments reducing CET1 including goodwill and intangible assets, deferred tax assets relying on future profitability, cash flow hedge reserves, gains on sale related to securitizations, defined benefit pension fund assets, own credit risk adjustments on fair valued liabilities, insufficient provisions relative to expected losses under IRB approach, and reciprocal cross-holdings in financial institutions. Requirements include minimum CET1 ratio of 4.5% of risk-weighted assets, additional buffers increasing effective minimum, restrictions on distributions when buffers are breached through maximum distributable amount (MDA) mechanism, disclosure of capital composition and reconciliation to accounting balance sheet, and supervisory assessment of capital quality.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.2',
        name: 'Additional Tier 1 (AT1) Capital',
        description: "Additional Tier 1 (AT1) capital consists of instruments subordinated to depositors and general creditors, capable of absorbing losses while the institution remains a going concern, typically through write-down or conversion to equity when capital ratios fall below triggers. This includes perpetual subordinated instruments with no maturity date or incentive to redeem, discretionary coupon payments that can be cancelled without triggering default or acceleration, principal loss absorption through temporary or permanent write-down or conversion to common equity, trigger levels typically set at 5.125% CET1 ratio for write-down or conversion, full subordination to depositors and senior creditors, call options only after minimum five years and subject to supervisory approval, and restrictions on distributions when capital buffers are breached. Regulatory requirements include minimum Tier 1 capital ratio (CET1 plus AT1) of 6% of RWA, eligibility criteria ensuring genuine loss absorption, grandfathering provisions for legacy instruments not meeting current criteria, limits on recognition of AT1 issued by subsidiaries, and assessment of trigger mechanisms and loss absorption features ensuring effectiveness during stress.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.3',
        name: 'Tier 2 Capital & Subordinated Debt',
        description: "Tier 2 capital provides additional loss absorption on a gone-concern basis, primarily consisting of subordinated debt instruments and certain loan loss provisions. This encompasses subordinated debt with original maturity of at least five years, subordinated to depositors and general creditors but ranking above equity and AT1 instruments, amortization in final five years of maturity reducing recognition by 20% per year, general provisions or loan loss allowances for standardized approach exposures up to 1.25% of credit RWA, revaluation reserves for certain assets, and instruments issued by subsidiaries subject to limits. Requirements include minimum total capital ratio (Tier 1 plus Tier 2) of 8% of RWA, eligibility criteria for Tier 2 instruments including lock-in clauses preventing payment of coupons if capital falls below minimum, prohibition on credit-sensitive features linking coupon to institution's credit rating, call options only after five years and with supervisory approval, loss absorption through statutory write-down or conversion mechanisms in resolution, and limits on inclusion of excess provisions and subsidiary-issued capital in consolidated Tier 2.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.4',
        name: 'Capital Conservation Buffer',
        description: "The capital conservation buffer requires institutions to hold CET1 capital above minimum requirements to absorb losses during stress while maintaining capacity to lend, set at 2.5% of RWA above the minimum 4.5% CET1 requirement. This creates an effective CET1 minimum of 7% in normal times, with the buffer designed to be drawn down during stress periods when losses erode capital, followed by rebuilding through earnings retention during recovery. When the buffer is breached, institutions face restrictions on discretionary distributions including dividends, share buybacks, and variable compensation through the maximum distributable amount (MDA) framework. MDA calculation depends on the extent of buffer breach, with four quartiles determining the maximum percentage of distributable items that can be paid, ranging from 60% when in the top quartile to 0% when CET1 falls below minimum requirements. Requirements include buffer maintenance in normal times, automatic restrictions without need for supervisory intervention when breached, capital planning ensuring buffer adequacy, stress testing assessing buffer sufficiency, disclosure of buffer levels and compliance, and supervisory expectations that institutions operate above combined buffer requirements to avoid restrictions and maintain market confidence.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.5',
        name: 'Countercyclical Capital Buffer (CCyB)',
        description: "The countercyclical capital buffer (CCyB) varies between 0% and 2.5% of RWA based on credit cycle conditions, increasing during periods of excessive credit growth to build resilience and decreasing during downturns to support lending. National authorities set CCyB rates for their jurisdictions based on indicators including credit-to-GDP gap, credit growth rates, asset prices, and supervisory judgment, with institutions calculating their institution-specific buffer as weighted average of buffers in jurisdictions where they have credit exposures. This encompasses buffer accumulation during credit booms when systemic risks build, buffer release during stress to absorb losses and maintain lending capacity, reciprocity arrangements where authorities recognize foreign CCyB rates, and communication of buffer decisions with pre-announcement period typically 12 months before increases take effect. Requirements include quarterly calculation of institution-specific CCyB based on geographic distribution of credit exposures, compliance with combined buffer requirement including CCyB, MDA restrictions when combined buffer is breached, disclosure of CCyB exposure by jurisdiction, and supervisory assessment of credit cycle conditions and systemic risk indicators informing buffer decisions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.6',
        name: 'Systemic Risk Buffers & G-SII/O-SII',
        description: "Systemic risk buffers apply to systemically important institutions whose failure would have significant negative externalities on the financial system and real economy. Global systemically important institutions (G-SIIs) face additional CET1 requirements ranging from 1% to 3.5% based on systemic importance scores considering size, interconnectedness, substitutability, complexity, and cross-border activity, with annual assessment and publication of G-SII list. Other systemically important institutions (O-SIIs) designated at national level face buffers typically 0% to 2% based on domestic systemic importance, with authorities considering size relative to domestic economy, importance for domestic financial system, and complexity. This includes higher loss absorbency requirements reflecting greater risk to financial stability, expectations for enhanced supervision and resolution planning, resolvability assessments ensuring orderly failure without taxpayer support, and potential additional requirements for institutions approaching G-SII threshold. Requirements include annual assessment and notification of systemic importance designation, phase-in periods for newly designated institutions, disclosure of systemic importance scores and buffer requirements, enhanced supervision including more frequent reporting and on-site inspections, and recovery and resolution planning with credible strategies for failure scenarios.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.7',
        name: 'Leverage Ratio',
        description: "The leverage ratio serves as non-risk-based backstop to risk-weighted capital requirements, calculated as Tier 1 capital divided by total exposure measure, with minimum requirement of 3% and higher requirements for systemically important institutions. Total exposure measure includes on-balance sheet exposures at accounting value without risk weighting, derivatives exposures calculated using standardized approach for counterparty credit risk (SA-CCR) or replacement cost plus potential future exposure, securities financing transactions (SFT) using comprehensive approach with supervisory haircuts or own estimates, and off-balance sheet items with credit conversion factors typically 10% for commitments or 100% for guarantees. This encompasses treatment of central bank reserves included in exposure measure, netting benefits for derivatives and SFT subject to enforceable agreements, exclusion of certain items such as accounting provisions, and calibration to limit excessive leverage while not unduly constraining low-risk activities. Requirements include quarterly calculation and disclosure of leverage ratio and components, minimum 3% requirement with potential for higher buffers, restrictions on distributions when leverage ratio falls below requirements, supervisory monitoring of leverage trends and business model implications, and assessment of whether risk-weighted or leverage ratio is binding constraint on capital.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.8',
        name: 'MREL & TLAC Requirements',
        description: "Minimum requirement for own funds and eligible liabilities (MREL) and total loss-absorbing capacity (TLAC) ensure institutions have sufficient loss-absorbing and recapitalization capacity to support resolution without taxpayer support. TLAC applies to G-SIIs requiring minimum 18% of RWA and 6.75% of leverage exposure from January 2022, consisting of regulatory capital plus eligible subordinated liabilities meeting criteria including sufficient subordination, minimum remaining maturity of one year, and no set-off rights. MREL applies more broadly with requirements set institution-specifically based on resolution strategy, typically requiring loss absorption amount to cover losses and recapitalization amount to restore market confidence post-resolution, with subordination requirements ensuring bail-in without contagion to senior creditors. This encompasses eligible instruments including capital, subordinated debt, and potentially senior debt if sufficiently subordinated, internal MREL for material subsidiaries ensuring loss absorption at entity level, and transitional arrangements with phase-in periods. Requirements include calculation of MREL/TLAC ratios, issuance of eligible instruments to meet requirements, disclosure of MREL/TLAC composition and compliance, resolution planning ensuring effective use of loss-absorbing capacity, and contractual recognition of bail-in for instruments governed by non-EU law.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.9',
        name: 'Capital Planning & Stress Testing',
        description: "Capital planning ensures institutions maintain adequate capital under baseline and stress scenarios, supporting business strategy while meeting regulatory requirements and market expectations. This encompasses forward-looking capital projections over multi-year planning horizon typically three to five years, baseline scenario reflecting expected business performance and economic conditions, stress scenarios including supervisory scenarios from ECB/EBA stress tests and institution-specific scenarios, assessment of capital generation through retained earnings and capital consumption from RWA growth and losses, evaluation of capital actions including dividends, buybacks, and issuance, and contingency planning for capital shortfalls. Supervisory stress testing includes common scenarios applied across institutions enabling peer comparison, assessment of capital adequacy under adverse conditions, evaluation of risk management and governance, and potential supervisory actions if capital inadequate including Pillar 2 requirements, restrictions on distributions, or requirements for capital raising. Requirements include annual capital planning process with board approval, stress testing at least annually with severe but plausible scenarios, documentation of assumptions and methodologies, integration with business planning and risk appetite, reverse stress testing identifying scenarios causing capital to fall below minimum, and supervisory review of capital plans and stress test results.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '5.10',
        name: 'Internal Capital Adequacy Assessment (ICAAP)',
        description: "Internal Capital Adequacy Assessment Process (ICAAP) requires institutions to assess capital adequacy relative to risk profile, considering all material risks including those not fully captured in Pillar 1 requirements. This encompasses identification and assessment of material risks including credit, market, operational, interest rate risk in banking book (IRRBB), concentration risk, business risk, strategic risk, reputational risk, and other institution-specific risks, quantification of capital needs for material risks using internal models, stress testing, or other methodologies, assessment of capital adequacy under current and forward-looking scenarios, evaluation of capital management and planning processes, and documentation of ICAAP framework and results. Supervisory Review and Evaluation Process (SREP) assesses ICAAP quality and determines Pillar 2 requirements (P2R) as binding minimum capital add-ons for risks not adequately covered in Pillar 1, and Pillar 2 guidance (P2G) as non-binding supervisory expectations for additional capital. Requirements include proportionate ICAAP appropriate to size, complexity, and risk profile, annual update and submission to supervisors, board and senior management ownership, independent validation and review, integration with risk management and business planning, stress testing and scenario analysis, assessment of risk concentrations and diversification effects, and documentation of methodologies, assumptions, and governance arrangements.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
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
    icon: 'Circle',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Concentration risk arises from large exposures to individual counterparties, groups of connected clients, economic sectors, geographic regions, or specific instruments that could result in significant losses if exposures materialize simultaneously. This includes large exposure limits typically set at 25% of eligible capital to single counterparties, concentration to specific industries or sectors such as real estate or commodities, geographic concentration creating country risk or regional economic dependency, intra-financial system exposures between banks and other financial institutions, asset class concentration in particular types of lending or securities, funding concentration from limited number of depositors or creditors, foreign currency concentration exposures, and granularity analysis measuring portfolio diversification across the exposure base.",
    subCategories: [
      {
        id: '6.1',
        name: 'Large Exposures & Single Name Concentration',
        description: "Large exposures framework limits concentration to individual counterparties or groups of connected clients to prevent excessive loss from single obligor default. The fundamental limit restricts exposures to single counterparties to 25% of eligible capital, with lower 10% limit for exposures between G-SIIs to reduce interconnectedness in the financial system. Exposure value includes all on-balance sheet and off-balance sheet exposures after credit risk mitigation, with derivatives calculated using counterparty credit risk methods, securities financing transactions included, and exposures to connected clients aggregated based on control relationships or economic interdependence. This encompasses identification of groups of connected clients through ownership links, control relationships, or economic dependencies where financial difficulties of one would cause difficulties for others, exemptions for certain exposures including intragroup exposures subject to conditions, exposures to central governments and central banks, covered bonds meeting eligibility criteria, and trade finance exposures with short maturity. Requirements include daily monitoring of large exposures, reporting to supervisors of all exposures exceeding 10% of eligible capital, prior supervisory approval for exposures exceeding limits in exceptional circumstances, systems and controls for identifying connected clients, and governance with board-level oversight of concentration risk.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.2',
        name: 'Sectoral & Industry Concentration',
        description: "Sectoral concentration risk arises from excessive exposure to specific industries or economic sectors that may be affected by common risk factors, creating correlated losses during sector-specific downturns. This includes concentration to real estate sector including commercial real estate, residential mortgages, and construction lending, energy sector exposures to oil and gas, renewables, and utilities, financial sector exposures to banks, insurance companies, and other financial institutions, retail and consumer sectors, manufacturing and industrial sectors, technology and telecommunications, agriculture and commodities, shipping and transportation, and sovereign and public sector exposures. Assessment encompasses identification of material sector concentrations relative to total portfolio and capital, analysis of sector-specific risk drivers including regulatory changes, technological disruption, commodity prices, and economic cycles, stress testing of sector concentrations under adverse scenarios specific to each sector, correlation analysis examining co-movement of defaults within sectors, and diversification metrics measuring portfolio granularity. Risk management includes sector limits and risk appetite thresholds, enhanced due diligence for concentrated sectors, sector-specific expertise and monitoring, early warning indicators for sector deterioration, and capital allocation reflecting concentration risk through Pillar 2 assessments.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.3',
        name: 'Geographic & Country Concentration',
        description: "Geographic concentration risk involves excessive exposure to specific countries, regions, or geographic areas, creating vulnerability to localized economic shocks, political events, natural disasters, or regulatory changes. This encompasses country risk from sovereign default or political instability, transfer risk preventing cross-border payments due to foreign exchange restrictions or capital controls, regional economic concentration to specific economic zones or trading blocs, emerging market exposures with higher volatility and political risk, concentration to home country creating domestic economic dependency, cross-border exposures requiring assessment of legal enforceability and recovery prospects, and correlation of defaults within geographic regions during regional crises. Assessment includes country risk ratings from external agencies and internal assessments, exposure measurement including direct exposures and indirect exposures through guarantees or collateral, stress testing of geographic concentrations under country-specific and regional scenarios, analysis of economic fundamentals including GDP growth, fiscal position, external debt, and political stability, and monitoring of early warning indicators such as credit default swap spreads, currency depreciation, and capital outflows. Risk management encompasses country limits and risk appetite by country risk rating, diversification strategies across geographies, hedging of country risk through credit derivatives or political risk insurance, enhanced monitoring of high-risk countries, and contingency planning for country crises including exposure reduction strategies.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.4',
        name: 'Intra-Financial System Exposures',
        description: "Intra-financial system exposures represent concentration risk from interconnectedness between financial institutions, creating potential for contagion and systemic risk amplification during stress. This includes interbank exposures from unsecured lending, deposits, and credit lines between banks, exposures to other financial institutions including insurance companies, asset managers, and hedge funds, central counterparty (CCP) exposures from clearing membership and default fund contributions, correspondent banking relationships, securities financing transactions with financial counterparties, derivative exposures to financial institutions, and indirect exposures through common asset holdings or funding sources. Regulatory framework includes reduced large exposure limit of 10% of eligible capital for exposures between G-SIIs, enhanced monitoring of financial sector concentration, assessment of interconnectedness in systemic risk evaluations, and resolution planning considering financial sector exposures. Risk management encompasses limits on financial sector concentration, counterparty credit risk assessment of financial institutions, monitoring of financial sector stress indicators, diversification of banking relationships and funding sources, collateralization of exposures to financial counterparties, stress testing of financial sector concentration including scenarios where multiple financial institutions fail simultaneously, and contingency planning for loss of key financial sector relationships.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.5',
        name: 'Product & Asset Class Concentration',
        description: "Product and asset class concentration risk arises from excessive exposure to specific lending products, asset types, or financial instruments that may be affected by common risk factors or market conditions. This encompasses concentration to specific loan products such as commercial real estate loans, residential mortgages, consumer loans, credit cards, or auto loans, concentration to asset classes including corporate bonds, sovereign bonds, equities, or structured products, concentration to specific collateral types affecting recovery rates, concentration to particular derivative products or trading strategies, and concentration to securitization exposures or off-balance sheet vehicles. Assessment includes measurement of product concentrations relative to total assets and capital, analysis of product-specific risk characteristics including credit quality, maturity profile, and loss history, stress testing of product concentrations under adverse scenarios affecting specific products, correlation analysis of defaults or losses within product categories, and evaluation of diversification benefits across products. Risk management encompasses product limits and risk appetite by asset class, product approval processes assessing concentration implications, portfolio rebalancing strategies to reduce concentrations, capital allocation for product concentration risk under Pillar 2, monitoring of product performance metrics and early warning indicators, and strategic planning considering product diversification objectives.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.6',
        name: 'Funding Source Concentration',
        description: "Funding source concentration creates liquidity and refinancing risk from over-reliance on specific funding providers, instruments, or markets, making the institution vulnerable if access is disrupted. This includes concentration to individual depositors or deposit-taking relationships, concentration to specific wholesale funding providers or investor types, concentration to particular funding instruments such as commercial paper, covered bonds, or securitizations, concentration to specific funding markets or currencies, concentration to related parties or group entities, and time concentration with large amounts maturing simultaneously. Assessment encompasses identification of material funding concentrations across multiple dimensions, measurement of concentration metrics including Herfindahl index for depositor concentration, analysis of funding stability and rollover risk for concentrated sources, stress testing of funding concentration under scenarios where concentrated sources are lost, and evaluation of funding market capacity and institution's market share. Risk management includes limits on funding concentrations with escalation procedures, diversification strategies across funding sources, instruments, tenors, and markets, relationship management with key funding providers, contingency funding plans addressing loss of concentrated sources, monitoring of funding costs and availability as early warning indicators, and strategic funding planning promoting diversification while balancing cost efficiency.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.7',
        name: 'Currency Concentration',
        description: "Currency concentration risk involves excessive exposure to specific foreign currencies in assets, liabilities, or off-balance sheet positions, creating vulnerability to exchange rate movements and foreign currency liquidity stress. This encompasses asset-liability mismatches in foreign currencies creating foreign exchange risk, concentration of foreign currency assets or liabilities relative to capital, concentration to emerging market currencies with higher volatility, foreign currency liquidity risk from inability to obtain specific currencies during stress, and structural foreign currency positions from investments in foreign subsidiaries. Assessment includes measurement of net open foreign currency positions by currency, analysis of foreign currency asset-liability maturity mismatches, stress testing of currency concentrations under exchange rate shock scenarios, evaluation of foreign currency liquidity sources and market depth, and assessment of natural hedges from correlated foreign currency assets and liabilities. Risk management encompasses limits on foreign currency exposures and concentrations, hedging strategies using foreign exchange derivatives or natural hedges, foreign currency liquidity management ensuring access to material currencies, diversification across currencies for international operations, monitoring of foreign exchange markets and currency-specific risks, and contingency planning for foreign currency liquidity stress including access to foreign exchange swap lines or currency conversion capabilities.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.8',
        name: 'Collateral & Security Concentration',
        description: "Collateral concentration risk arises from over-reliance on specific types of collateral or security for credit risk mitigation, creating vulnerability if collateral values decline or enforceability is challenged. This includes concentration to real estate collateral with exposure to property market cycles, concentration to financial collateral such as securities or cash deposits, concentration to specific asset types as collateral including inventory, equipment, or receivables, concentration to guarantees from specific guarantors or types of guarantors, geographic concentration of collateral locations, and correlation between obligor creditworthiness and collateral value creating wrong-way risk. Assessment encompasses measurement of collateral concentrations by type, location, and quality, analysis of collateral valuation methodologies and revaluation frequency, stress testing of collateral values under adverse scenarios affecting specific collateral types, evaluation of legal enforceability and recovery timelines for different collateral types, and assessment of collateral correlation with obligor default probability. Risk management includes limits on collateral concentrations and loan-to-value ratios, diversification of collateral types accepted, conservative collateral valuation with appropriate haircuts, regular revaluation of collateral especially for volatile asset types, legal review of security documentation and enforceability, monitoring of collateral quality and coverage ratios, and contingency planning for collateral liquidation including market capacity and execution strategies.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.9',
        name: 'Concentration Risk Measurement & Metrics',
        description: "Concentration risk measurement quantifies the degree of concentration and potential impact on capital adequacy using various metrics and methodologies. This encompasses Herfindahl-Hirschman Index (HHI) measuring concentration across exposures with higher values indicating greater concentration, calculation of exposure shares to largest counterparties or sectors, granularity analysis examining number and size distribution of exposures, concentration ratios such as top 10 or top 20 exposures relative to capital, name concentration metrics for single obligor risk, and sector concentration indices. Advanced approaches include portfolio credit risk models such as CreditMetrics or CreditRisk+ incorporating concentration effects through correlation assumptions, economic capital models allocating capital for concentration risk, stress testing and scenario analysis quantifying losses under concentrated exposure defaults, marginal risk contribution analysis identifying exposures contributing most to portfolio risk, and diversification metrics measuring risk reduction from portfolio effects. Requirements under Pillar 2 include assessment of concentration risk not fully captured in Pillar 1, quantification of additional capital needs for material concentrations, documentation of concentration risk measurement methodologies, validation of models and assumptions, and supervisory review of concentration risk management and capital adequacy.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '6.10',
        name: 'Concentration Risk Limits & Governance',
        description: "Concentration risk governance establishes frameworks for identifying, measuring, monitoring, and controlling concentration risk through limits, policies, and oversight structures. This encompasses risk appetite statements defining acceptable concentration levels across dimensions including single name, sector, geography, and product, limit frameworks with quantitative thresholds for different concentration types, escalation procedures when limits are approached or breached, exception approval processes for limit excesses with appropriate authority levels, and periodic limit reviews ensuring continued appropriateness. Governance structure includes board oversight of concentration risk strategy and appetite, senior management responsibility for concentration risk management, risk committee review of concentration exposures and limit utilization, independent risk function monitoring and reporting, and business line accountability for managing concentrations within limits. Reporting includes regular concentration risk reports to board and senior management, monitoring of concentration metrics and trends, early warning indicators for emerging concentrations, stress testing results for concentrated exposures, and regulatory reporting of large exposures and concentrations. Risk culture encompasses awareness of concentration risk across organization, training on concentration risk identification and management, incentive structures discouraging excessive concentration, and challenge culture enabling escalation of concentration concerns.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'governance,-risk-management--internal-controls',
    name: 'Governance, Risk Management & Internal Controls',
    icon: 'Circle',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Governance and risk management encompasses the organizational framework, oversight structures, risk culture, and control systems ensuring effective identification, measurement, monitoring and mitigation of risks. This includes board of directors responsibilities and composition requirements, management body duties and fit and proper assessments, risk appetite framework defining risk tolerance levels, three lines of defense model separating risk-taking, risk control, and independent assurance functions, risk committee establishment and responsibilities, chief risk officer independence and authority, internal audit scope and reporting lines, remuneration policies aligning incentives with risk management, conflicts of interest identification and management, risk data aggregation and reporting capabilities, escalation procedures for risk limit breaches, risk culture assessment and improvement, and internal capital and liquidity adequacy assessment processes (ICAAP and ILAAP).",
    subCategories: [
      {
        id: '7.1',
        name: 'Board of Directors & Management Body',
        description: "The board of directors or management body bears ultimate responsibility for the institution's strategy, risk appetite, and oversight of risk management, requiring appropriate composition, expertise, and functioning. This encompasses board composition with sufficient size, diversity of skills, experience, and backgrounds, independence requirements with adequate non-executive and independent directors, collective suitability ensuring board possesses necessary competencies in banking, finance, risk management, and relevant business areas, individual suitability of board members assessed through fit and proper requirements including reputation, experience, and time commitment, separation of chair and CEO roles or appropriate checks and balances, board committees including risk committee, audit committee, remuneration committee, and nomination committee with clear mandates, board meeting frequency and attendance requirements, access to information and management, and succession planning for board positions. Responsibilities include approval of strategy and business plan, setting risk appetite and limits, oversight of risk management framework, approval of policies and key decisions, monitoring of performance and risk profile, ensuring adequate capital and liquidity, oversight of compliance and internal controls, and accountability to shareholders and supervisors. Requirements include documented board charter and committee terms of reference, minutes of board meetings, annual board self-assessment, induction and ongoing training programs, and supervisory assessment of board effectiveness.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.2',
        name: 'Senior Management & Executive Oversight',
        description: "Senior management implements board-approved strategy and risk appetite, manages day-to-day operations, and ensures effective risk management and control environment. This includes CEO responsibility for overall management and execution of strategy, CFO oversight of financial management and reporting, CRO independence and authority over risk management, heads of business lines accountable for risks in their areas, heads of control functions including compliance, internal audit, and risk management, management committees such as executive committee, asset-liability committee (ALCO), and credit committee, clear reporting lines and accountability, delegation of authority framework, and succession planning for key management positions. Responsibilities encompass implementation of board decisions and strategy, development of policies and procedures, allocation of resources to business and control functions, establishment and maintenance of risk management framework, monitoring of risk profile and limit utilization, escalation of issues to board, ensuring compliance with laws and regulations, and fostering appropriate risk culture. Requirements include fit and proper assessments of senior management, documented roles and responsibilities, management committee charters and meeting minutes, performance evaluation and accountability mechanisms, and supervisory assessment of management quality and effectiveness.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.3',
        name: 'Risk Appetite Framework',
        description: "Risk appetite framework (RAF) defines the types and levels of risk the institution is willing to accept in pursuit of business objectives, providing boundaries for risk-taking and guiding strategic and operational decisions. This encompasses risk appetite statement articulating overall risk tolerance approved by board, risk capacity representing maximum risk the institution can assume given capital and liquidity constraints, risk profile showing actual risk exposures, risk limits translating appetite into quantitative thresholds for specific risk types, risk metrics and key risk indicators (KRIs) for monitoring, and risk tolerances for qualitative risks. RAF covers all material risks including credit, market, liquidity, operational, concentration, interest rate, business, strategic, and reputational risks, with metrics such as capital ratios, liquidity ratios, credit quality indicators, earnings volatility, and loss limits. Implementation includes cascading of risk appetite to business lines and legal entities, integration with strategic planning and budgeting, limit setting and monitoring processes, escalation procedures for limit breaches, and periodic review and recalibration. Requirements include board approval of risk appetite, documentation of RAF methodology and governance, stress testing of risk appetite under adverse scenarios, reporting of risk profile against appetite, and supervisory assessment of RAF appropriateness and effectiveness.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.4',
        name: 'Three Lines of Defense Model',
        description: "The three lines of defense model establishes clear roles and responsibilities for risk management and control, ensuring appropriate segregation and independence. First line of defense comprises business and operational management owning and managing risks in their areas, implementing controls, and ensuring compliance with policies and limits, with accountability for risk-taking decisions and day-to-day risk management. Second line of defense includes independent risk management function providing oversight, challenge, and guidance on risk matters, compliance function ensuring adherence to laws and regulations, and other control functions such as finance and legal, with responsibilities for policy development, limit setting, risk monitoring and reporting, independent assessment of first line activities, and escalation of concerns. Third line of defense consists of internal audit providing independent assurance on effectiveness of governance, risk management, and controls, with audit plan based on risk assessment, reporting to board audit committee, and independence from first and second lines. Requirements include clear definition of roles and responsibilities for each line, appropriate independence and authority for second and third lines, adequate resources and expertise in control functions, reporting lines ensuring independence with risk and audit functions reporting to board committees, coordination and information sharing between lines while maintaining independence, and avoidance of conflicts of interest or inappropriate assumption of first line responsibilities by control functions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.5',
        name: 'Chief Risk Officer & Risk Function',
        description: "The Chief Risk Officer (CRO) leads the independent risk management function, providing oversight and challenge to business activities and ensuring effective risk identification, measurement, monitoring, and mitigation. CRO independence is ensured through reporting to board risk committee or CEO with direct access to board, involvement in all material risk decisions, authority to challenge business decisions, protection from removal without board approval, and remuneration not linked to business line performance. Risk function responsibilities include development of risk management framework and policies, implementation of risk appetite and limit framework, independent assessment and validation of risk models, risk monitoring and reporting to senior management and board, oversight of risk-taking activities, stress testing and scenario analysis, emerging risk identification, and coordination of risk management across the organization. Risk function structure encompasses central risk management team and risk officers embedded in business lines with reporting to CRO, coverage of all material risk types, sufficient resources and expertise, and appropriate systems and tools. Requirements include CRO fit and proper assessment, documented risk function charter and authority, independence safeguards, adequate budget and staffing, access to information and management, and supervisory assessment of risk function effectiveness and CRO stature within organization.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.6',
        name: 'Internal Audit Function',
        description: "Internal audit provides independent, objective assurance on the effectiveness of governance, risk management, and internal controls, reporting to board audit committee. This encompasses audit scope covering all activities, processes, and entities including business lines, control functions, IT systems, and outsourced activities, risk-based audit planning prioritizing areas of highest risk, audit execution including testing of controls, assessment of compliance, and evaluation of process effectiveness, audit findings and recommendations for improvement, follow-up on management actions to address findings, and coordination with external auditors and supervisors. Independence requirements include organizational independence with reporting to audit committee, objectivity of individual auditors free from conflicts of interest, no involvement in operational activities or control functions, rotation of audit staff, and protection from interference. Audit committee responsibilities include approval of audit charter and plan, oversight of audit function, review of audit findings, monitoring of management remediation, assessment of auditor independence and effectiveness, and approval of head of internal audit appointment and removal. Requirements include qualified and experienced audit staff, adequate resources and budget, access to all information and personnel, audit methodology and quality assurance, documentation of audit work, and supervisory assessment of audit function effectiveness and independence.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.7',
        name: 'Risk Data Aggregation & Reporting',
        description: "Risk data aggregation and reporting capabilities enable institutions to collect, aggregate, and report risk data accurately and timely, supporting risk management and decision-making. Principles include accuracy and integrity of risk data through validation, reconciliation, and controls, completeness covering all material risk exposures and positions, timeliness enabling reporting within required timeframes including daily for trading risks and more frequent during stress, adaptability allowing generation of ad-hoc reports and stress scenarios, and comprehensiveness covering all risk types and legal entities. Data architecture encompasses data governance framework defining ownership and standards, data quality management with controls and monitoring, data lineage and reconciliation processes, data aggregation capabilities consolidating data across systems and entities, and reporting infrastructure producing management and regulatory reports. Risk reporting includes regular reports to board and senior management on risk profile, limit utilization, and key risk indicators, stress testing results, emerging risks, and material risk events, with reports tailored to audience and providing actionable information. Requirements under BCBS 239 principles include board and senior management oversight of data capabilities, data architecture and IT infrastructure supporting aggregation, accuracy and reliability controls, comprehensiveness and timeliness standards, adaptability for stress and crisis situations, and supervisory assessment of compliance with principles particularly for systemically important institutions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.8',
        name: 'Risk Culture & Conduct',
        description: "Risk culture encompasses the values, beliefs, attitudes, and behaviors relating to risk awareness and risk-taking within the organization, influencing how risks are identified, understood, discussed, and acted upon. Strong risk culture characteristics include tone from the top with board and senior management demonstrating commitment to sound risk management, accountability with clear ownership of risks and consequences for risk decisions, effective communication and challenge enabling open discussion of risks and concerns, incentives aligned with risk appetite and long-term sustainability rather than short-term profits, and competence with adequate training and expertise in risk management. Assessment of risk culture includes surveys and interviews gauging employee perceptions and behaviors, analysis of risk incidents and near-misses for cultural factors, review of decision-making processes and challenge mechanisms, evaluation of incentive structures and performance management, and observation of behaviors and tone in meetings and communications. Risk culture improvement initiatives encompass leadership commitment and role modeling, communication of risk appetite and expectations, training and awareness programs, adjustment of incentives and consequences, empowerment of control functions, and recognition of good risk management behaviors. Requirements include board oversight of risk culture, assessment of culture as part of governance reviews, integration of culture considerations in hiring and promotion, whistleblower protections encouraging reporting of concerns, and supervisory assessment of culture through on-site inspections and thematic reviews.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.9',
        name: 'Remuneration & Incentive Structures',
        description: "Remuneration policies and practices must align incentives with sound risk management, long-term performance, and stakeholder interests, avoiding excessive risk-taking for short-term gains. This encompasses governance with board remuneration committee comprising non-executive directors overseeing remuneration policy and decisions, independence of remuneration decisions from business line influence, and involvement of risk and control functions in remuneration decisions. Principles include alignment with risk appetite and business strategy, balance between fixed and variable compensation with sufficient fixed component, deferral of variable compensation over multi-year periods typically 3-5 years, performance adjustment mechanisms including malus reducing unvested awards and clawback recovering paid compensation based on risk outcomes and conduct, risk adjustment of variable compensation considering risk-adjusted performance metrics, and avoidance of guaranteed bonuses except in limited circumstances. Identified staff subject to enhanced requirements include senior management, material risk-takers, and control function staff, with at least 40-60% of variable compensation deferred, at least 50% in instruments such as shares or contingent capital, and vesting subject to continued employment and performance. Requirements include documented remuneration policy approved by board and shareholders, disclosure of remuneration practices and amounts for identified staff, supervisory review of remuneration policies and practices, and assessment of alignment with risk management and culture.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '7.10',
        name: 'Internal Capital & Liquidity Adequacy Assessment (ICAAP/ILAAP)',
        description: "Internal Capital Adequacy Assessment Process (ICAAP) and Internal Liquidity Adequacy Assessment Process (ILAAP) are institution-owned assessments of capital and liquidity adequacy relative to risk profile and business strategy. ICAAP encompasses identification of all material risks including Pillar 1 risks (credit, market, operational) and other risks such as interest rate risk in banking book, concentration risk, business risk, strategic risk, and reputational risk, quantification of capital needs for material risks using internal models, stress testing, or other methodologies, assessment of capital adequacy under current and forward-looking scenarios including stress, evaluation of capital management and planning processes, and documentation of ICAAP framework, methodologies, and results. ILAAP includes assessment of liquidity risk profile and drivers, quantification of liquidity needs under normal and stress scenarios, evaluation of funding strategy and sources, assessment of liquidity buffers and contingency funding plans, and documentation of ILAAP framework and results. Supervisory Review and Evaluation Process (SREP) assesses ICAAP and ILAAP quality, evaluating risk identification and assessment, methodologies and assumptions, stress testing, governance and controls, and integration with management processes, resulting in Pillar 2 requirements (P2R) as binding capital and liquidity add-ons and Pillar 2 guidance (P2G) as supervisory expectations. Requirements include proportionate ICAAP/ILAAP appropriate to size and complexity, annual update and submission to supervisors, board and senior management ownership, independent validation, integration with risk management and business planning, and documentation of frameworks, methodologies, assumptions, and governance.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'technology,-cybersecurity--information-security',
    name: 'Technology, Cybersecurity & Information Security',
    icon: 'Circle',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Technology and cybersecurity risk involves threats from information and communication technology (ICT) system failures, cyber attacks including malware and ransomware, data breaches compromising personal or confidential information, and inadequate digital operational resilience. This encompasses ICT risk management frameworks under Digital Operational Resilience Act (DORA), incident detection and response procedures, cyber threat intelligence and monitoring, third-party ICT service provider oversight particularly cloud computing services, digital operational resilience testing including threat-led penetration testing, business continuity and disaster recovery for ICT systems, data protection and privacy requirements under GDPR, encryption and access control mechanisms, authentication and identity management, vulnerability management and patch management, network security and segmentation, endpoint protection, and incident reporting obligations to supervisory authorities within specified timeframes.",
    subCategories: [
      {
        id: '8.1',
        name: 'ICT Risk Management Framework',
        description: "ICT risk management framework under Digital Operational Resilience Act (DORA) establishes comprehensive governance, policies, and processes for managing information and communication technology risks. This encompasses ICT risk management strategy approved by management body defining risk appetite and objectives, ICT risk governance with clear roles and responsibilities including board oversight and senior management accountability, identification and classification of ICT assets and systems based on criticality and sensitivity, ICT risk assessment processes evaluating threats, vulnerabilities, and potential impacts, risk treatment decisions including acceptance, mitigation, transfer, or avoidance, and continuous monitoring of ICT risk profile. Framework covers all ICT systems including core banking systems, payment systems, trading platforms, customer-facing applications, data storage and processing, networks and telecommunications, and third-party ICT services. Requirements include documented ICT risk management framework proportionate to size and complexity, integration with overall risk management framework, regular review and updates of ICT risk assessments, reporting to management body on ICT risks and incidents, allocation of sufficient resources and budget for ICT risk management, and supervisory assessment of framework adequacy and effectiveness.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.2',
        name: 'Cybersecurity Threats & Attack Vectors',
        description: "Cybersecurity threats encompass malicious activities targeting confidentiality, integrity, or availability of information systems and data. This includes malware such as viruses, worms, trojans, and spyware designed to damage systems or steal data, ransomware encrypting data and demanding payment for decryption, phishing attacks using fraudulent emails or websites to steal credentials or information, distributed denial-of-service (DDoS) attacks overwhelming systems to disrupt availability, advanced persistent threats (APT) involving sophisticated, prolonged attacks by organized groups or nation-states, SQL injection and other application vulnerabilities exploiting software weaknesses, man-in-the-middle attacks intercepting communications, credential theft and account compromise, insider threats from malicious or negligent employees, supply chain attacks compromising third-party software or services, and zero-day exploits targeting previously unknown vulnerabilities. Attack vectors include email as primary delivery mechanism for phishing and malware, web applications with vulnerabilities, removable media and USB devices, remote access and VPN connections, mobile devices and applications, social engineering manipulating human behavior, and physical access to facilities or equipment. Defense requires layered security controls, threat intelligence monitoring emerging threats, security awareness training, incident detection and response capabilities, and regular security assessments and penetration testing.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.3',
        name: 'Data Protection & Privacy (GDPR)',
        description: "Data protection and privacy requirements under General Data Protection Regulation (GDPR) and similar laws govern collection, processing, storage, and transfer of personal data. This encompasses lawful basis for processing requiring consent, contractual necessity, legal obligation, vital interests, public task, or legitimate interests, data minimization collecting only necessary data, purpose limitation using data only for specified purposes, accuracy ensuring data is correct and up-to-date, storage limitation retaining data only as long as necessary, and integrity and confidentiality protecting data through appropriate security. Rights of data subjects include right to access their data, right to rectification of inaccurate data, right to erasure (right to be forgotten), right to restriction of processing, right to data portability, right to object to processing, and rights related to automated decision-making and profiling. Requirements include data protection impact assessments (DPIA) for high-risk processing, appointment of data protection officer (DPO) for certain organizations, records of processing activities, privacy by design and by default, data breach notification to supervisory authority within 72 hours and to affected individuals when high risk, international data transfer mechanisms such as adequacy decisions, standard contractual clauses, or binding corporate rules, and accountability demonstrating compliance through policies, procedures, and documentation. Penalties for non-compliance can reach up to 4% of annual global turnover or \u20ac20 million.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.4',
        name: 'Incident Detection & Response',
        description: "Incident detection and response capabilities enable timely identification, containment, and recovery from cybersecurity incidents and ICT disruptions. Detection mechanisms include security information and event management (SIEM) systems aggregating and analyzing logs from multiple sources, intrusion detection and prevention systems (IDS/IPS) monitoring network traffic for malicious activity, endpoint detection and response (EDR) monitoring devices for threats, user and entity behavior analytics (UEBA) identifying anomalous behaviors, threat intelligence feeds providing indicators of compromise, security operations center (SOC) with 24/7 monitoring, and automated alerting on suspicious activities. Incident response process encompasses preparation with documented incident response plan, roles and responsibilities, and communication procedures, detection and analysis classifying incidents by severity and impact, containment isolating affected systems to prevent spread, eradication removing threat and closing vulnerabilities, recovery restoring systems and data to normal operations, and post-incident review identifying lessons learned and improvements. Requirements under DORA include classification of ICT-related incidents based on criticality and impact, reporting of major incidents to supervisory authorities within specified timeframes (initial notification, intermediate reports, final report), root cause analysis, maintenance of incident register, testing of incident response procedures, and supervisory assessment of detection and response capabilities.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.5',
        name: 'Third-Party ICT Service Providers',
        description: "Third-party ICT service provider risk arises from outsourcing or procurement of ICT services including cloud computing, data centers, software development, IT support, and payment processing. This encompasses concentration risk from critical service providers, vendor financial stability and business continuity, data security and confidentiality at vendor sites, compliance with regulations by vendors, subcontracting and fourth-party risk, vendor lock-in and exit challenges, and cross-border services with jurisdictional issues. Due diligence before engagement includes assessment of vendor capabilities, security controls, certifications (ISO 27001, SOC 2), financial strength, references, and contractual protections. Contractual requirements include service level agreements (SLAs) defining performance standards, security and data protection obligations, audit and inspection rights, incident notification requirements, business continuity and disaster recovery commitments, data ownership and portability, termination and exit assistance, liability and indemnification, and regulatory compliance including right for supervisors to access information and conduct inspections. Ongoing oversight includes monitoring of vendor performance against SLAs, regular security assessments and audits, review of vendor security incidents and breaches, testing of vendor business continuity capabilities, and vendor risk reviews. Requirements under DORA include register of third-party ICT service providers, risk assessment of critical providers, contractual arrangements meeting regulatory standards, exit strategies, and enhanced oversight of critical third-party providers by supervisors.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.6',
        name: 'Digital Operational Resilience Testing',
        description: "Digital operational resilience testing under DORA ensures ICT systems and processes can withstand, respond to, and recover from ICT-related disruptions. Testing types include vulnerability assessments identifying weaknesses in systems and applications, open source and proprietary vulnerability scanning, penetration testing simulating attacks to exploit vulnerabilities, scenario-based testing evaluating response to specific incident scenarios, business continuity and disaster recovery testing validating recovery capabilities, and threat-led penetration testing (TLPT) simulating sophisticated attacks by skilled threat actors mimicking real-world adversaries. TLPT framework includes scoping identifying critical functions and systems to test, threat intelligence gathering information on relevant threat actors and tactics, red team testing with ethical hackers conducting attacks, blue team defense by institution's security teams, controls testing evaluating detection and response, and closure phase with reporting and remediation. Testing frequency depends on risk profile with annual testing for most institutions and more frequent testing for critical systems, with TLPT required at least every three years for major financial institutions. Requirements include documented testing strategy and plan, independence of testers from tested systems, remediation of identified vulnerabilities within defined timeframes, reporting of testing results to management body, documentation of tests and findings, and supervisory oversight of testing programs particularly TLPT for systemically important institutions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.7',
        name: 'Access Control & Identity Management',
        description: "Access control and identity management ensure only authorized individuals can access systems, data, and facilities based on legitimate business needs. This encompasses user identification and authentication verifying identity through credentials, multi-factor authentication (MFA) requiring multiple verification methods such as password plus token or biometric, single sign-on (SSO) enabling access to multiple systems with one authentication, privileged access management (PAM) controlling and monitoring administrative accounts with elevated privileges, role-based access control (RBAC) granting permissions based on job roles, least privilege principle providing minimum necessary access, segregation of duties preventing single individuals from controlling critical processes, access reviews periodically verifying appropriateness of access rights, and timely deprovisioning removing access when no longer needed such as employee termination or role change. Identity lifecycle management includes provisioning new users with appropriate access, modifications when roles change, and deprovisioning when leaving organization or changing roles. Technical controls include strong password policies with complexity, length, and expiration requirements, account lockout after failed login attempts, session timeouts, encryption of credentials, monitoring of access attempts and privileged activities, and logging of access for audit trails. Requirements include documented access control policies, regular access reviews and recertification, monitoring and alerting on suspicious access patterns, audit trails of access and changes, and assessment of access control effectiveness through audits and testing.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.8',
        name: 'Encryption & Cryptography',
        description: "Encryption and cryptographic controls protect confidentiality and integrity of data in transit and at rest, preventing unauthorized access or tampering. This encompasses encryption of data at rest including databases, file systems, backups, and archives using strong algorithms such as AES-256, encryption of data in transit using TLS/SSL for network communications and secure protocols for file transfers, end-to-end encryption for sensitive communications, encryption of mobile devices and removable media, and tokenization or masking of sensitive data such as payment card numbers. Cryptographic key management includes key generation using secure random number generators, key storage in hardware security modules (HSM) or key management systems, key rotation and lifecycle management, key backup and recovery procedures, and key destruction when no longer needed. Certificate management for public key infrastructure (PKI) includes issuance of digital certificates, certificate validation and revocation checking, certificate renewal before expiration, and trust store management. Requirements include cryptographic standards and algorithms approved by authorities such as NIST or ENISA, key management policies and procedures, separation of duties for key management, regular review and update of cryptographic controls as algorithms become obsolete, and assessment of encryption implementation and key management practices.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.9',
        name: 'Network Security & Segmentation',
        description: "Network security protects network infrastructure and communications from unauthorized access, attacks, and disruptions through defense-in-depth approach. This encompasses network segmentation dividing network into zones based on security requirements and trust levels, firewalls controlling traffic between network segments based on rules, intrusion detection and prevention systems (IDS/IPS) monitoring and blocking malicious traffic, virtual private networks (VPN) for secure remote access, network access control (NAC) enforcing security policies before allowing device connections, demilitarized zones (DMZ) isolating public-facing systems from internal networks, wireless network security with encryption and authentication, and distributed denial-of-service (DDoS) protection. Network architecture principles include defense in depth with multiple layers of security, zero trust model verifying every access request regardless of location, micro-segmentation limiting lateral movement within networks, and separation of production, development, and test environments. Monitoring and management includes network traffic analysis identifying anomalies, security information and event management (SIEM) correlating network events, vulnerability scanning of network devices, configuration management ensuring secure settings, patch management for network equipment, and change control for network modifications. Requirements include documented network architecture and security zones, regular network security assessments and penetration testing, monitoring of network traffic and security events, incident response for network attacks, and review of network security controls.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '8.10',
        name: 'Business Continuity & Disaster Recovery for ICT',
        description: "Business continuity and disaster recovery for ICT ensure critical systems and data can be recovered and operations resumed following disruptions including cyber attacks, system failures, natural disasters, or other incidents. This encompasses business impact analysis (BIA) identifying critical systems and acceptable downtime, recovery time objectives (RTO) defining maximum acceptable downtime for each system, recovery point objectives (RPO) defining maximum acceptable data loss, backup strategies including full, incremental, and differential backups with appropriate frequency, backup storage with offsite or cloud-based copies protected from primary site disasters, backup testing and restoration drills verifying recoverability, disaster recovery sites including hot sites with real-time replication, warm sites with periodic updates, or cold sites requiring setup time, failover and failback procedures for switching to recovery site and returning to primary site, and data replication technologies for continuous data protection. Testing requirements include annual testing of disaster recovery plans, scenario-based testing simulating various disruption types, involvement of business users in testing, documentation of test results and issues, and remediation of identified gaps. Requirements include documented business continuity and disaster recovery plans for ICT, alignment of RTO/RPO with business requirements, regular backups with secure storage, testing of recovery capabilities, incident response integration, and supervisory assessment of resilience and recovery capabilities particularly for critical systems.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'climate--environmental-risk',
    name: 'Climate & Environmental Risk',
    icon: 'Circle',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Climate and environmental risk encompasses both physical risks from climate-related events such as floods, droughts, wildfires and extreme weather, and transition risks from the shift toward a low-carbon economy including policy changes, technological disruption, market sentiment shifts, and reputational damage. This includes climate-related financial disclosures under Task Force on Climate-related Financial Disclosures (TCFD), EU Taxonomy for sustainable activities classification, Sustainable Finance Disclosure Regulation (SFDR) requiring ESG integration, climate stress testing and scenario analysis assessing portfolio resilience, green asset ratio and banking book taxonomy alignment, carbon-intensive sector exposure monitoring, stranded asset risk from fossil fuel investments, environmental and social due diligence in lending decisions, physical risk assessment of collateral locations, transition planning supporting clients in decarbonization, and incorporation of climate risk into credit risk models, capital planning and risk appetite frameworks.",
    subCategories: [
      {
        id: '9.1',
        name: 'Physical Climate Risks',
        description: "Physical climate risks arise from climate-related events and long-term shifts in climate patterns affecting assets, operations, and counterparties. Acute physical risks include extreme weather events such as hurricanes, floods, wildfires, heatwaves, droughts, and storms with increasing frequency and severity, causing direct damage to properties, infrastructure, and collateral, business interruptions, and supply chain disruptions. Chronic physical risks involve gradual changes including rising temperatures, sea level rise, changing precipitation patterns, ocean acidification, and biodiversity loss, affecting asset values, agricultural productivity, water availability, and habitability of regions. Impact channels include credit risk from borrower defaults when physical events damage income-generating assets or collateral, market risk from repricing of assets in affected regions, operational risk from damage to bank facilities and infrastructure, and liquidity risk from sudden large claims or deposit withdrawals. Assessment requires identification of exposures to physical risk including geographic location of borrowers, collateral, and operations, climate hazard mapping using climate models and scenarios, vulnerability assessment of assets and counterparties, and quantification of potential financial impacts. Risk management includes integration of physical risk in credit underwriting and collateral valuation, geographic diversification, insurance requirements for high-risk properties, engagement with clients on adaptation measures, and stress testing of physical risk scenarios.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.2',
        name: 'Transition Risks',
        description: "Transition risks arise from the shift toward a low-carbon economy through policy changes, technological developments, market dynamics, and reputational factors, potentially affecting asset values and business models. Policy and legal risks include carbon pricing mechanisms such as carbon taxes or emissions trading systems increasing costs for carbon-intensive activities, regulatory requirements for emissions reductions or energy efficiency, phase-out of fossil fuel subsidies, restrictions on high-emission activities, and litigation against companies for climate-related damages or disclosure failures. Technology risks involve development of clean technologies making existing technologies obsolete, stranded assets from fossil fuel reserves or carbon-intensive infrastructure becoming uneconomic, disruption of traditional business models, and investment needs for transition. Market risks include changing consumer preferences toward sustainable products, investor pressure for decarbonization, repricing of carbon-intensive assets, and shifts in supply and demand for commodities. Reputational risks arise from association with high-emission activities, failure to address climate change, or perceived greenwashing. Impact channels include credit risk from borrowers in transition-exposed sectors facing declining revenues or stranded assets, market risk from repricing of carbon-intensive securities, and strategic risk from business model disruption. Assessment requires identification of exposures to transition-sensitive sectors including fossil fuels, utilities, transportation, heavy industry, and agriculture, scenario analysis using transition pathways such as orderly, disorderly, or hot house world scenarios, and quantification of financial impacts under different transition speeds and policy approaches.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.3',
        name: 'Climate-Related Financial Disclosures (TCFD)',
        description: "Task Force on Climate-related Financial Disclosures (TCFD) framework provides recommendations for consistent, comparable, and decision-useful climate-related financial disclosures. Four pillars include governance describing board oversight of climate risks and management's role in assessing and managing climate risks, strategy disclosing actual and potential impacts of climate risks and opportunities on business, strategy, and financial planning including resilience under different climate scenarios, risk management describing processes for identifying, assessing, and managing climate risks and integration with overall risk management, and metrics and targets disclosing metrics used to assess climate risks and opportunities and targets for managing climate risks and achieving opportunities. Governance disclosures include board committee responsibilities, management committees and roles, frequency of board and management discussions on climate, and integration in remuneration. Strategy disclosures include short, medium, and long-term climate risks and opportunities, impact on business lines, products, and services, scenario analysis assessing resilience under 2\u00b0C or lower, higher temperature, and other scenarios, and strategic responses and transition planning. Risk management disclosures include processes for identifying and assessing climate risks, prioritization and materiality assessment, integration with enterprise risk management, and monitoring and reporting. Metrics and targets include greenhouse gas emissions (Scope 1, 2, and 3), climate-related risks in lending and investment portfolios, green asset ratios, and targets for emissions reduction, green finance, or portfolio alignment. Requirements include annual disclosure in financial filings, assurance of climate disclosures, and supervisory assessment of disclosure quality and completeness.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.4',
        name: 'EU Taxonomy & Sustainable Finance',
        description: "EU Taxonomy for sustainable activities provides classification system defining environmentally sustainable economic activities based on technical screening criteria. Six environmental objectives include climate change mitigation, climate change adaptation, sustainable use and protection of water and marine resources, transition to circular economy, pollution prevention and control, and protection and restoration of biodiversity and ecosystems. Activity qualifies as sustainable if it makes substantial contribution to at least one objective, does no significant harm (DNSH) to other objectives, meets minimum social safeguards, and complies with technical screening criteria. Technical screening criteria specify thresholds and requirements for activities such as emissions intensity for power generation, energy efficiency for buildings, or sustainable forest management practices. Disclosure requirements under Taxonomy Regulation include proportion of taxonomy-eligible and taxonomy-aligned activities in total assets, turnover, and capital expenditure for non-financial companies, and green asset ratio (GAR) for banks showing proportion of taxonomy-aligned exposures in covered assets. Covered assets include exposures to non-financial corporations, loans for real estate, and certain other exposures, with exclusions for sovereign exposures, central banks, and some other categories. Requirements include data collection from counterparties on taxonomy alignment, assessment of substantial contribution and DNSH criteria, calculation and disclosure of GAR and other taxonomy metrics, and supervisory monitoring of taxonomy implementation and disclosure quality. Challenges include data availability from counterparties, interpretation of technical criteria, and assessment of DNSH and minimum safeguards.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.5',
        name: 'Climate Stress Testing & Scenario Analysis',
        description: "Climate stress testing and scenario analysis assess financial resilience under different climate pathways and transition speeds over long time horizons. Scenarios include orderly transition with early, ambitious policy action enabling smooth transition to net zero by 2050, disorderly transition with late or sudden policy action causing abrupt repricing and disruption, hot house world with limited policy action leading to severe physical risks from temperature increases of 3\u00b0C or more, and current policies scenario continuing existing policies without additional action. Time horizons extend to 2050 or beyond reflecting long-term nature of climate risks, with projections of macroeconomic variables, carbon prices, energy prices, sectoral impacts, and physical damages. Transmission channels include credit risk from defaults and rating migrations in affected sectors, market risk from repricing of assets, operational risk from physical damage to facilities, and income effects from changing business volumes and margins. Methodology includes top-down approaches using macroeconomic models to project portfolio impacts, bottom-up approaches assessing individual exposures or counterparties, and hybrid approaches combining both. Supervisory climate stress tests such as ECB climate stress test assess banking sector resilience, identify vulnerabilities, and inform supervisory dialogue, with results used for risk management improvements rather than capital requirements. Requirements include participation in supervisory stress tests, internal climate stress testing integrated with ICAAP, scenario analysis for strategy and disclosure, documentation of methodologies and assumptions, and use of results for risk management, capital planning, and business strategy.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.6',
        name: 'Green Asset Ratio & Portfolio Alignment',
        description: "Green asset ratio (GAR) measures proportion of bank assets financing taxonomy-aligned environmentally sustainable activities, providing metric for transition progress and comparison across institutions. GAR calculation includes numerator of taxonomy-aligned exposures meeting technical screening criteria for substantial contribution, DNSH, and minimum safeguards, and denominator of covered assets including loans to non-financial corporations, real estate loans, and certain other exposures, excluding sovereign exposures, exposures to financial institutions, and trading book. Disclosure includes GAR for total assets and separate ratios for different asset classes, proportion of taxonomy-eligible but not yet aligned exposures, and proportion of non-eligible exposures. Portfolio alignment metrics assess consistency of lending and investment portfolios with climate goals such as Paris Agreement temperature targets, using methodologies such as implied temperature rise (ITR) showing temperature outcome if all economic activity followed portfolio's emissions intensity, portfolio carbon footprint measuring financed emissions, or sector-based alignment comparing portfolio composition to transition pathways. Alignment assessment requires emissions data from counterparties, forward-looking transition plans, and comparison to sector decarbonization pathways. Requirements include annual disclosure of GAR and components, explanation of changes over time, targets for increasing GAR or portfolio alignment, and integration in business strategy and risk appetite. Challenges include data quality and availability from counterparties, evolving taxonomy criteria, and methodological choices for alignment metrics.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.7',
        name: 'Carbon-Intensive Sector Exposures',
        description: "Carbon-intensive sector exposures create concentration risk and transition vulnerability requiring enhanced monitoring and management. High-emission sectors include fossil fuel extraction (coal, oil, gas), fossil fuel power generation, energy-intensive industries (steel, cement, chemicals), transportation (aviation, shipping, road transport), and agriculture. Assessment includes identification and measurement of exposures to carbon-intensive sectors, analysis of emissions intensity and transition readiness of counterparties, evaluation of business model sustainability under transition scenarios, and assessment of stranded asset risk from reserves or infrastructure becoming uneconomic. Transition readiness indicators include emissions reduction targets and progress, capital expenditure on low-carbon technologies, revenue from sustainable activities, climate governance and strategy, and alignment with sector transition pathways. Risk management includes sector limits and risk appetite for carbon-intensive exposures, enhanced due diligence and monitoring, engagement with clients on transition planning, support for transition through green finance and advisory services, and portfolio rebalancing toward sustainable activities. Supervisory expectations include identification of material carbon-intensive exposures, assessment of transition risks, stress testing of concentrated exposures, integration in credit risk management and capital planning, and disclosure of sector exposures and management approach. Challenges include defining sector boundaries, assessing transition readiness with limited data, balancing transition support with risk management, and managing reputational risks from continued financing of high-emission activities.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.8',
        name: 'Stranded Assets & Fossil Fuel Exposure',
        description: "Stranded assets are assets that suffer unanticipated or premature write-downs, devaluations, or conversion to liabilities due to transition to low-carbon economy. Fossil fuel stranded assets include coal, oil, and gas reserves becoming uneconomic to extract due to carbon pricing, regulation, or demand reduction, fossil fuel power plants retired early or operating at reduced capacity, and fossil fuel infrastructure such as pipelines or refineries becoming obsolete. Other stranded assets include carbon-intensive industrial facilities, internal combustion engine vehicle manufacturing, and real estate in climate-vulnerable locations. Drivers of stranding include policy measures such as carbon pricing or phase-out mandates, technology developments making clean alternatives cheaper, market shifts in investor and consumer preferences, physical climate impacts affecting asset viability, and reputational factors. Financial impacts include credit losses from borrower defaults or collateral value declines, market losses from asset repricing, and write-downs of equity investments. Assessment requires identification of exposures to stranding-vulnerable assets, evaluation of stranding probability and timing under different scenarios, quantification of potential losses, and assessment of borrower capacity to absorb losses or transition. Risk management includes limits on fossil fuel exposures, enhanced due diligence for stranding-vulnerable assets, conservative collateral valuation incorporating transition risks, engagement with clients on transition planning, and portfolio diversification. Requirements include disclosure of fossil fuel exposures, stress testing of stranded asset scenarios, integration in credit risk models and capital planning, and supervisory assessment of stranded asset risk management.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.9',
        name: 'Environmental & Social Due Diligence',
        description: "Environmental and social (E&S) due diligence in lending and investment decisions assesses environmental impacts, climate risks, and social factors affecting credit quality and reputation. Environmental due diligence includes assessment of environmental risks such as pollution, waste management, resource use, and biodiversity impacts, compliance with environmental regulations and permits, environmental liabilities from contamination or remediation obligations, climate risks including physical and transition risks, and environmental management systems and performance. Social due diligence covers labor practices and working conditions, health and safety, community impacts and stakeholder engagement, human rights including indigenous rights, and social license to operate. Due diligence process includes screening for E&S risks based on sector, activity, and location, categorization by risk level with enhanced due diligence for high-risk transactions, assessment of E&S risks and impacts, evaluation of client E&S management capacity, and identification of mitigation measures and covenants. Requirements include E&S policies and standards defining expectations, integration of E&S assessment in credit approval process, training of credit officers on E&S risks, monitoring of E&S performance and covenant compliance, and escalation of significant E&S issues. Exclusion lists prohibit financing of certain activities such as illegal logging, production of certain weapons, or activities in protected areas. Requirements include documented E&S risk management framework, disclosure of E&S policies and exclusions, reporting on E&S risk profile and incidents, and supervisory assessment of E&S risk management practices.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '9.10',
        name: 'Climate Risk Integration in Risk Management',
        description: "Climate risk integration embeds climate considerations across risk management framework including risk identification, assessment, monitoring, mitigation, and reporting. Credit risk integration includes incorporation of climate risks in credit underwriting and approval, adjustment of credit ratings or probability of default for climate-exposed borrowers, climate-sensitive collateral valuation, sector limits for carbon-intensive exposures, and climate stress testing of credit portfolios. Market risk integration includes assessment of climate-related market risks in trading and investment portfolios, scenario analysis of transition repricing, and climate considerations in asset allocation. Operational risk integration includes assessment of physical risks to bank facilities and operations, business continuity planning for climate events, and third-party risk management for climate-exposed suppliers. Liquidity and funding risk integration includes assessment of climate impacts on funding sources and market access, and contingency planning for climate-related liquidity stress. Capital planning integration includes assessment of climate risks in ICAAP, climate stress testing informing capital adequacy, and potential Pillar 2 capital add-ons for material climate risks. Risk appetite integration includes climate risk metrics and limits, board-approved climate risk appetite, and monitoring of climate risk profile against appetite. Governance integration includes board and senior management oversight of climate risks, climate expertise in risk function, and climate risk reporting. Requirements include comprehensive climate risk management framework, integration across all material risk types, documentation of methodologies and processes, regular review and updates, and supervisory assessment of integration quality and effectiveness.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  },
  {
    id: 'conduct,-consumer-protection--market-integrity',
    name: 'Conduct, Consumer Protection & Market Integrity',
    icon: 'Circle',
    regulationCount: 0,
    subCategoryCount: 10,
    overlapCount: 0,
    contradictionCount: 0,
    description: "Conduct and consumer protection risk involves unfair treatment of customers, mis-selling of financial products, market abuse, manipulation, insider trading, conflicts of interest, and failures in market integrity. This includes suitability and appropriateness assessments under MiFID II ensuring products match client needs and knowledge, product governance and oversight ensuring fair design and distribution, target market identification and monitoring, disclosure requirements providing clear information on costs, risks and features, treating vulnerable customers fairly including those in financial difficulty, complaint handling procedures and redress mechanisms, inducement and commission rules preventing conflicts of interest, best execution obligations ensuring optimal client outcomes, market manipulation prevention including surveillance systems, insider dealing prohibitions and insider lists, transaction reporting to regulators, recording of communications, sales process documentation, affordability assessments in consumer lending, responsible lending principles, and early arrears management to prevent consumer detriment.",
    subCategories: [
      {
        id: '10.1',
        name: 'Suitability & Appropriateness Assessments (MiFID II)',
        description: "Suitability and appropriateness assessments under MiFID II ensure financial products and services match client needs, knowledge, experience, and risk tolerance. Suitability assessment applies when providing investment advice or portfolio management, requiring firms to obtain information on client's knowledge and experience in relevant investment types, financial situation including income, assets, liabilities, and regular financial commitments, and investment objectives including time horizon, risk tolerance, and purpose of investment. Assessment determines whether product or service is suitable considering client profile, with unsuitable recommendations prohibited. Appropriateness assessment applies when providing non-advised services such as execution-only, requiring assessment of client knowledge and experience to determine if client understands risks, with warning required if product appears inappropriate but client may proceed. Information collection includes questionnaires and interviews, verification of information provided, periodic updates particularly for ongoing relationships, and documentation of assessments and recommendations. Requirements include policies and procedures for conducting assessments, training of staff on assessment requirements, suitability reports explaining recommendations and how they meet client needs, appropriateness warnings when products appear inappropriate, and monitoring of assessment quality. Exemptions include appropriateness assessment not required for non-complex products such as shares admitted to regulated markets, money market instruments, and certain UCITS funds when provided execution-only without advice. Supervisory focus includes quality of assessments, adequacy of information collection, appropriateness of recommendations, and handling of negative assessments.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.2',
        name: 'Product Governance & Oversight',
        description: "Product governance ensures financial products are designed, distributed, and monitored to meet needs of identified target markets and deliver fair customer outcomes. Product design phase includes identification of target market based on client characteristics, needs, and objectives, assessment of product features, risks, costs, and complexity, stress testing of product performance under adverse scenarios, and approval by product governance committee. Distribution strategy includes identification of appropriate distribution channels, assessment of distributor capabilities and target markets, provision of product information to distributors, and monitoring of distribution activities. Target market definition specifies positive target market of clients for whom product is compatible and negative target market of clients for whom product is not appropriate, considering factors such as knowledge and experience, financial situation, risk tolerance, objectives, and needs. Product monitoring includes regular review of product performance, customer outcomes, complaints, and market developments, assessment of whether product remains consistent with target market, and product modifications or withdrawal if issues identified. Requirements include documented product governance policies and procedures, product approval process with appropriate oversight, target market identification and documentation, distribution agreements specifying responsibilities, regular product reviews at least annually or more frequently for complex or risky products, and management information on product performance and customer outcomes. Supervisory expectations include robust product governance frameworks, clear accountability, adequate resources and expertise, and demonstration of good customer outcomes.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.3',
        name: 'Disclosure & Transparency Requirements',
        description: "Disclosure and transparency requirements ensure clients receive clear, accurate, and timely information on products, services, costs, and risks enabling informed decisions. Pre-contractual disclosures include key information documents (KID) for packaged retail investment and insurance products (PRIIPs) providing standardized information on product features, risks, costs, and performance scenarios, terms and conditions of products and services, information on firm and its services, conflicts of interest and how managed, and costs and charges including all fees, commissions, and third-party payments. Ongoing disclosures include periodic statements showing portfolio composition, performance, and costs, transaction confirmations, information on material changes to products or services, and annual cost and charges disclosure. Cost disclosure includes all costs and charges expressed in monetary terms and as percentage, breakdown of product costs, service costs, and third-party payments, illustration of cumulative effect of costs on returns, and disclosure of inducements received from third parties. Risk disclosure includes description of risks associated with products and services, risk indicators such as summary risk indicator in KID, warnings for high-risk or complex products, and information on investor protection schemes. Requirements include clear, fair, and not misleading communications, prominent disclosure of material information, plain language avoiding jargon, timely provision of information before client commitment, and accessibility of information. Supervisory focus includes adequacy and clarity of disclosures, prominence of risk warnings, completeness of cost disclosure, and whether disclosures enable informed decisions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.4',
        name: 'Treating Customers Fairly & Vulnerable Customers',
        description: "Treating customers fairly (TCF) principle requires firms to place fair treatment of customers at center of business culture and decision-making. Six TCF outcomes include fair treatment embedded in corporate culture, products and services designed to meet needs of identified customer groups, clear information provided before, during, and after sale, advice suitable for customer circumstances, products performing as expected, and no unreasonable barriers to switching, complaining, or claiming. Vulnerable customers include those with characteristics such as low financial literacy, physical or mental health conditions, life events like bereavement or job loss, or resilience factors like low income or over-indebtedness, requiring additional care and support. Requirements for vulnerable customers include identification of vulnerability through customer interactions and data analysis, staff training on recognizing and supporting vulnerable customers, flexible and accessible communication methods, additional time and support for decision-making, proactive monitoring for signs of difficulty, and tailored solutions such as payment arrangements or product modifications. Specific protections include restrictions on aggressive sales tactics, cooling-off periods allowing cancellation, forbearance measures for customers in financial difficulty, and safeguards for customers lacking mental capacity. Requirements include TCF policies and frameworks, management information on customer outcomes, monitoring of vulnerable customer treatment, staff training and competence, and regular assessment of fairness of products, services, and processes. Supervisory approach includes thematic reviews of TCF, mystery shopping, analysis of complaints and customer outcomes, and enforcement action for poor treatment.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.5',
        name: 'Complaint Handling & Redress',
        description: "Complaint handling procedures ensure customer complaints are resolved fairly, promptly, and consistently, with appropriate redress for valid complaints. Complaint definition includes any expression of dissatisfaction about products, services, or complaint handling, whether oral or written, with broad interpretation to capture all grievances. Complaint handling process includes acknowledgment of complaint promptly, investigation of facts and circumstances, assessment of whether complaint is justified, communication of decision with clear explanation, and provision of redress if complaint upheld. Redress may include financial compensation for losses or distress, correction of errors, apology, or other appropriate remedy. Timeframes include acknowledgment within specified period (typically 5 business days), resolution within maximum period (typically 15-35 business days depending on jurisdiction), and information on escalation to ombudsman or alternative dispute resolution if customer dissatisfied. Requirements include documented complaint handling procedures, accessible complaint channels, free complaint handling for customers, fair and consistent assessment, root cause analysis identifying systemic issues, management information on complaints including volumes, types, outcomes, and trends, and reporting to senior management and board. Alternative dispute resolution includes referral rights to financial ombudsman services or similar schemes providing independent review, with firms required to cooperate and comply with decisions. Supervisory focus includes complaint handling quality and timeliness, fairness of outcomes, identification and remediation of systemic issues, and use of complaints data for improving products and processes.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.6',
        name: 'Inducements & Conflicts of Interest',
        description: "Inducements and conflicts of interest rules prevent or manage situations where firm or staff interests conflict with client interests, ensuring clients receive unbiased advice and fair treatment. Conflicts of interest include situations where firm or staff have financial or other interests that may influence recommendations or decisions, such as commissions from product providers, proprietary products, related party transactions, or personal trading. Requirements include identification of conflicts through conflicts register and assessment processes, disclosure of conflicts to clients in clear and prominent manner, management of conflicts through organizational and administrative arrangements such as information barriers, segregation of functions, and supervision, and avoidance of conflicts where management insufficient to ensure fair treatment. Inducements include fees, commissions, or non-monetary benefits received from third parties in relation to services provided to clients, with restrictions under MiFID II including prohibition on inducements for independent advice and portfolio management, and requirement that inducements for non-independent advice enhance quality of service and are disclosed. Permitted inducements include minor non-monetary benefits such as market information or research below threshold, and inducements that enhance service quality such as training or technology. Requirements include inducements policy defining acceptable and prohibited inducements, disclosure of inducements to clients including amounts or calculation methodology, assessment of quality enhancement for permitted inducements, and monitoring of inducements received and paid. Supervisory focus includes adequacy of conflicts identification and management, quality and prominence of disclosures, compliance with inducements restrictions, and whether conflicts or inducements lead to customer detriment.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.7',
        name: 'Best Execution Obligations',
        description: "Best execution requires firms to take all sufficient steps to obtain best possible result for clients when executing orders, considering price, costs, speed, likelihood of execution and settlement, size, nature, and other relevant factors. Execution factors include price as typically most important factor, costs including commissions and fees, speed of execution, likelihood of execution and settlement, size and nature of order, and any other relevant considerations. Relative importance of factors depends on client characteristics (retail or professional), order characteristics, product characteristics, and execution venues. Execution venues include regulated markets, multilateral trading facilities (MTF), organized trading facilities (OTF), systematic internalizers, market makers, and other liquidity providers. Execution policy includes description of execution venues used, factors affecting venue selection, how factors are weighted, and how policy ensures best execution. Requirements include establishment and implementation of execution policy, annual review and update of policy, monitoring of execution quality, use of data and market information to assess venues, and notification of material changes to execution arrangements. Client consent required for executing outside regulated markets or MTF, with disclosure of execution policy and summary of execution quality. Order handling includes prompt and fair execution, prohibition on front-running or misuse of client order information, and aggregation of orders only when unlikely to disadvantage clients. Supervisory focus includes adequacy of execution policies, monitoring of execution quality, use of execution venues, and whether firms achieve best execution in practice.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.8',
        name: 'Market Abuse & Manipulation Prevention',
        description: "Market abuse prevention includes detection and prevention of insider dealing, unlawful disclosure of inside information, and market manipulation, maintaining market integrity and investor confidence. Insider dealing involves using inside information (precise, non-public, price-sensitive information) to trade or recommend trading in financial instruments, with prohibition on trading, disclosure, and recommending based on inside information. Market manipulation includes transactions or orders giving false or misleading signals about supply, demand, or price, transactions or orders securing price at abnormal or artificial level, dissemination of false or misleading information, and other conduct likely to manipulate market. Detection mechanisms include transaction monitoring systems identifying suspicious patterns such as unusual trading volumes, price movements, or timing, surveillance of communications including phone calls and electronic messages, monitoring of order book activity, and analysis of trading behavior. Suspicious transaction and order reports (STORs) required when firms have reasonable suspicion of market abuse, with reporting to competent authorities. Requirements include policies and procedures for preventing market abuse, systems and controls for detection, insider lists identifying persons with access to inside information, restrictions on personal account dealing by staff, training on market abuse regulations, and cooperation with authorities in investigations. Market soundings regime allows communication of inside information to potential investors before announcements to gauge interest, with specific procedures and record-keeping. Supervisory approach includes transaction surveillance, investigation of suspicious activity, enforcement action including fines and criminal prosecution, and cooperation between authorities across jurisdictions.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.9',
        name: 'Responsible Lending & Affordability',
        description: "Responsible lending principles ensure credit is provided only to borrowers who can afford repayments without financial distress, preventing over-indebtedness and consumer harm. Affordability assessment includes evaluation of borrower income from employment, benefits, or other sources, committed expenditure including existing credit obligations, housing costs, and essential living expenses, and discretionary expenditure on non-essential items, with assessment of whether borrower can afford new credit without undue hardship. Assessment methodology includes income verification through payslips, bank statements, or tax returns, expenditure assessment using declared expenditure, bank transaction analysis, or statistical models, stress testing of affordability under adverse scenarios such as interest rate increases or income reduction, and consideration of borrower's credit history and existing indebtedness. Requirements include documented affordability assessment for all credit applications, proportionate assessment with more detailed assessment for larger or longer-term credit, declining applications where credit appears unaffordable, and monitoring of affordability during credit relationship. Responsible lending practices include clear and balanced marketing avoiding encouragement of excessive borrowing, appropriate credit limits based on affordability, forbearance and support for customers in financial difficulty, and avoiding aggressive collection practices. Specific requirements for high-cost credit include affordability warnings, creditworthiness assessments, and caps on costs and charges. Requirements include responsible lending policies and procedures, staff training on affordability assessment, monitoring of lending decisions and outcomes, and assessment of whether lending is responsible and sustainable. Supervisory focus includes quality of affordability assessments, lending to customers in financial difficulty, outcomes including arrears and defaults, and fair treatment of borrowers.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      },
      {
        id: '10.10',
        name: 'Early Arrears Management & Forbearance',
        description: "Early arrears management and forbearance ensure customers in financial difficulty receive appropriate support and fair treatment, preventing escalation to serious arrears or default. Early arrears management includes proactive contact with customers at first sign of difficulty, assessment of customer circumstances and reasons for difficulty, discussion of options for resolving arrears, and agreement on sustainable solution. Forbearance measures include temporary payment arrangements such as payment holidays, reduced payments, or interest-only periods, permanent modifications such as term extensions, interest rate reductions, or principal forgiveness, refinancing or consolidation of debts, and other concessions appropriate to customer circumstances. Assessment of forbearance includes evaluation of customer's financial situation and ability to resume payments, assessment of whether forbearance is appropriate and sustainable, consideration of customer's engagement and willingness to resolve situation, and documentation of forbearance decision and terms. Requirements include forbearance policies and procedures, training of staff on forbearance options and assessment, fair and consistent treatment of customers in difficulty, monitoring of forbearance arrangements and customer compliance, and reporting on forbearance volumes and outcomes. Customer communications include clear information on forbearance options, implications of forbearance including impact on credit file, and ongoing support and contact. Prohibition on unfair practices includes restrictions on aggressive collection tactics, requirements for reasonable efforts to contact customers before enforcement action, and safeguards for vulnerable customers. Supervisory expectations include early identification and support for customers in difficulty, appropriate and sustainable forbearance, fair treatment throughout arrears process, and use of enforcement action only as last resort after exhausting forbearance options.",
        paragraphsAnalyzed: 0,
        overlapCount: 0,
        contradictionCount: 0,
        regulations: [],
        overlaps: [],
        contradictions: []
      }
    ]
  }
];
