import { useState, useMemo, useEffect } from 'react';
import { ChevronRight, ChevronDown, Circle, BarChart2, AlertTriangle, Flag } from 'lucide-react';
import { mockRiskCategories, type Regulation, type Overlap, type Contradiction } from './data/mockData';
import { VoiceAssistant } from './components/VoiceAssistant';
import { fetchRegulations, fetchAnalysis, ApiError } from './api/ragApi';

type IssueType = 'overlap' | 'contradiction';

interface Issue {
  id: string;
  type: IssueType;
  reg1: string;
  reg2: string;
  description: string;
  category: string;
  subCategory: string;
  severity?: string;
  confidence?: number;
  requirement1?: string;
  requirement2?: string;
  excerpt1?: string;
  excerpt2?: string;
}

export default function App() {
  const [viewMode, setViewMode] = useState<'issues' | 'requirements'>('requirements');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['credit-risk']));
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['All Issues', 'Overlaps', 'Contradictions']));
  const [selectedCategory, setSelectedCategory] = useState<string | null>('Credit Risk');
  const [selectedSubCategory, setSelectedSubCategory] = useState<string | null>('Credit Assessment & Underwriting Standards');
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [selectedRequirement, setSelectedRequirement] = useState<{ regulation: string; text: string; category: string; subCategory: string } | null>(null);
  const [expandedDescriptions, setExpandedDescriptions] = useState<Set<string>>(new Set());
  const [expandedRegulations, setExpandedRegulations] = useState<Set<string>>(new Set());
  
  // API state
  const [loadingRegulations, setLoadingRegulations] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [regulationsError, setRegulationsError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [apiRegulations, setApiRegulations] = useState<Regulation[]>([]);
  const [apiOverlaps, setApiOverlaps] = useState<Overlap[]>([]);
  const [apiContradictions, setApiContradictions] = useState<Contradiction[]>([]);

  // Fetch regulations when category or subcategory is selected
  useEffect(() => {
    // If neither category nor subcategory is selected, clear data
    if (!selectedCategory && !selectedSubCategory) {
      setApiRegulations([]);
      setRegulationsError(null);
      setApiOverlaps([]);
      setApiContradictions([]);
      setAnalysisError(null);
      return;
    }

    // Clear previous API data when switching
    setApiRegulations([]);
    setApiOverlaps([]);
    setApiContradictions([]);
    setRegulationsError(null);
    setAnalysisError(null);

    // Determine what to search for
    let searchId: string;
    let searchDescription: string;

    if (selectedSubCategory) {
      // Subcategory is selected - use subcategory data
      const category = mockRiskCategories.find(cat =>
        cat.subCategories.some(sub => sub.name === selectedSubCategory)
      );
      const subCategory = category?.subCategories.find(sub => sub.name === selectedSubCategory);
      
      if (!subCategory) return;
      
      searchId = subCategory.id;
      searchDescription = subCategory.description;
    } else if (selectedCategory) {
      // Only category is selected - use category data
      const category = mockRiskCategories.find(cat => cat.name === selectedCategory);
      
      if (!category) return;
      
      searchId = category.id;
      searchDescription = category.description;
    } else {
      return;
    }

    const loadRegulations = async () => {
      setLoadingRegulations(true);
      setRegulationsError(null);
      
      try {
        const regulations = await fetchRegulations(
          searchId,
          searchDescription,
          10
        );
        setApiRegulations(regulations);
      } catch (error) {
        if (error instanceof ApiError) {
          setRegulationsError(error.message);
        } else {
          setRegulationsError('Failed to load regulations');
        }
        console.error('Error fetching regulations:', error);
      } finally {
        setLoadingRegulations(false);
      }
    };

    loadRegulations();
  }, [selectedCategory, selectedSubCategory]);

  // Auto-select first regulation when regulations are loaded
  useEffect(() => {
    if (apiRegulations.length > 0 && !selectedRequirement && viewMode === 'requirements') {
      const firstReg = apiRegulations[0];
      setSelectedRequirement({
        regulation: firstReg.name,
        text: firstReg.description,
        category: selectedCategory || '',
        subCategory: selectedSubCategory || ''
      });
    }
  }, [apiRegulations, selectedRequirement, viewMode, selectedCategory, selectedSubCategory]);

  // Function to trigger analysis
  const loadAnalysis = async () => {
    if (!selectedSubCategory) return;

    const category = mockRiskCategories.find(cat =>
      cat.subCategories.some(sub => sub.name === selectedSubCategory)
    );
    const subCategory = category?.subCategories.find(sub => sub.name === selectedSubCategory);

    if (!subCategory) return;

    setLoadingAnalysis(true);
    setAnalysisError(null);

    try {
      const analysis = await fetchAnalysis(
        subCategory.id,
        subCategory.description,
        30
      );
      setApiOverlaps(analysis.overlaps);
      setApiContradictions(analysis.contradictions);
    } catch (error) {
      if (error instanceof ApiError) {
        setAnalysisError(error.message);
      } else {
        setAnalysisError('Failed to load analysis');
      }
      console.error('Error fetching analysis:', error);
    } finally {
      setLoadingAnalysis(false);
    }
  };

  // Flatten all issues with priority - use API data when available for selected subcategory
  const allIssues: Issue[] = useMemo(() => {
    const issues: Issue[] = [];
    
    mockRiskCategories.forEach(cat => {
      cat.subCategories.forEach(sub => {
        // Use API data if this is the selected subcategory and we have API data
        if (sub.name === selectedSubCategory && (apiOverlaps.length > 0 || apiContradictions.length > 0)) {
          // Add API overlaps
          apiOverlaps.forEach(overlap => {
            issues.push({
              id: overlap.id,
              type: 'overlap' as const,
              reg1: overlap.regulationPair[0],
              reg2: overlap.regulationPair[1],
              description: overlap.description,
              category: cat.name,
              subCategory: sub.name,
              confidence: overlap.confidenceScore,
              excerpt1: overlap.excerpts.regulation1,
              excerpt2: overlap.excerpts.regulation2
            });
          });
          
          // Add API contradictions
          apiContradictions.forEach(contradiction => {
            issues.push({
              id: contradiction.id,
              type: 'contradiction' as const,
              reg1: contradiction.regulationPair[0],
              reg2: contradiction.regulationPair[1],
              description: contradiction.description,
              category: cat.name,
              subCategory: sub.name,
              severity: contradiction.severity,
              requirement1: contradiction.conflictingRequirements.regulation1,
              requirement2: contradiction.conflictingRequirements.regulation2
            });
          });
        } else {
          // Use mock data for other subcategories
          sub.overlaps.forEach(overlap => {
            issues.push({
              id: overlap.id,
              type: 'overlap' as const,
              reg1: overlap.regulationPair[0],
              reg2: overlap.regulationPair[1],
              description: overlap.description,
              category: cat.name,
              subCategory: sub.name,
              confidence: overlap.confidenceScore,
              excerpt1: overlap.excerpts.regulation1,
              excerpt2: overlap.excerpts.regulation2
            });
          });
          
          sub.contradictions.forEach(contradiction => {
            issues.push({
              id: contradiction.id,
              type: 'contradiction' as const,
              reg1: contradiction.regulationPair[0],
              reg2: contradiction.regulationPair[1],
              description: contradiction.description,
              category: cat.name,
              subCategory: sub.name,
              severity: contradiction.severity,
              requirement1: contradiction.conflictingRequirements.regulation1,
              requirement2: contradiction.conflictingRequirements.regulation2
            });
          });
        }
      });
    });
    
    return issues;
  }, [selectedSubCategory, apiOverlaps, apiContradictions]);

  // Merge API regulations into display categories
  const displayCategories = useMemo(() => {
    if (!selectedSubCategory || apiRegulations.length === 0) {
      return mockRiskCategories;
    }

    return mockRiskCategories.map(cat => ({
      ...cat,
      subCategories: cat.subCategories.map(sub => {
        if (sub.name === selectedSubCategory) {
          return {
            ...sub,
            regulations: apiRegulations,
            overlapCount: apiOverlaps.length,
            contradictionCount: apiContradictions.length,
            overlaps: apiOverlaps,
            contradictions: apiContradictions
          };
        }
        return sub;
      })
    }));
  }, [selectedSubCategory, apiRegulations, apiOverlaps, apiContradictions]);

  const filteredIssues = useMemo(() => {
    if (selectedSubCategory) {
      return allIssues.filter(issue => issue.subCategory === selectedSubCategory);
    }
    if (selectedCategory) {
      return allIssues.filter(issue => issue.category === selectedCategory);
    }
    return allIssues;
  }, [allIssues, selectedCategory, selectedSubCategory]);

  // Group issues by type
  const groupedIssues = useMemo(() => {
    const groups: Record<string, Issue[]> = {
      'All Issues': filteredIssues,
      'Overlaps': [],
      'Contradictions': []
    };
    
    filteredIssues.forEach(issue => {
      if (issue.type === 'contradiction') {
        groups['Contradictions'].push(issue);
      } else {
        groups['Overlaps'].push(issue);
      }
    });
    
    return groups;
  }, [filteredIssues]);

  // Extract all requirements flattened
  const allRequirements = useMemo(() => {
    const reqs: { regulation: string; text: string; category: string; subCategory: string }[] = [];
    
    allIssues.forEach(issue => {
      if (issue.type === 'contradiction' && issue.requirement1 && issue.requirement2) {
        reqs.push(
          { regulation: issue.reg1, text: issue.requirement1, category: issue.category, subCategory: issue.subCategory },
          { regulation: issue.reg2, text: issue.requirement2, category: issue.category, subCategory: issue.subCategory }
        );
      } else if (issue.type === 'overlap' && issue.excerpt1 && issue.excerpt2) {
        reqs.push(
          { regulation: issue.reg1, text: issue.excerpt1, category: issue.category, subCategory: issue.subCategory },
          { regulation: issue.reg2, text: issue.excerpt2, category: issue.category, subCategory: issue.subCategory }
        );
      }
    });
    
    // Remove duplicates by creating unique key
    const seen = new Set<string>();
    return reqs.filter(req => {
      const key = `${req.regulation}:${req.text}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [allIssues]);

  // Filter requirements based on selected category/subcategory
  const filteredRequirements = useMemo(() => {
    if (selectedSubCategory) {
      return allRequirements.filter(req => req.subCategory === selectedSubCategory);
    }
    if (selectedCategory) {
      return allRequirements.filter(req => req.category === selectedCategory);
    }
    return allRequirements;
  }, [allRequirements, selectedCategory, selectedSubCategory]);

  const toggleCategory = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const toggleDescription = (key: string) => {
    const newExpanded = new Set(expandedDescriptions);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedDescriptions(newExpanded);
  };

  const toggleRegulationExpansion = (regId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const newExpanded = new Set(expandedRegulations);
    if (newExpanded.has(regId)) {
      newExpanded.delete(regId);
    } else {
      newExpanded.add(regId);
    }
    setExpandedRegulations(newExpanded);
  };

  return (
    <div className="h-screen flex bg-white">
      {/* Sidebar */}
      <div className="w-[280px] bg-white border-r border-gray-200 flex flex-col">
        {/* App Header */}
        <div className="px-4 py-4 border-b border-gray-200">
          <div className="w-full flex items-center gap-3 px-3 py-2">
            <div className="w-6 h-6 bg-[#1E3A8A] rounded flex items-center justify-center">
              <span className="text-white text-sm">L</span>
            </div>
            <span className="text-gray-900 flex-1 text-left">Lex</span>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto py-3">
          {/* View Mode Toggle */}
          <div className="px-5 mb-6">
            <div className="text-xs text-gray-500 mb-3 uppercase tracking-wider">View Mode</div>
            <div className="flex flex-col gap-1 bg-gray-100 p-1">
              <button
                onClick={() => {
                  setViewMode('issues');
                  setSelectedIssue(null);
                }}
                className={`flex items-center justify-center gap-2 px-3 py-2 transition-all ${
                  viewMode === 'issues'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Circle className="h-4 w-4" />
                <span className="text-sm">Issues</span>
              </button>
              <button
                onClick={() => {
                  setViewMode('requirements');
                  setSelectedRequirement(null);
                }}
                className={`flex items-center justify-center gap-2 px-3 py-2 transition-all ${
                  viewMode === 'requirements'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <BarChart2 className="h-4 w-4" />
                <span className="text-sm">Requirements</span>
              </button>
            </div>
          </div>

          <div className="h-px bg-gray-200 my-3 mx-5" />

          {/* Categories */}
          {displayCategories.map((category) => {
            const isExpanded = expandedCategories.has(category.id);
            const categoryIssues = allIssues.filter(i => i.category === category.name);
            
            return (
              <div key={category.id}>
                <button
                  onClick={() => {
                    toggleCategory(category.id);
                    setSelectedCategory(category.name);
                    setSelectedSubCategory(null);
                  }}
                  className={`w-full flex items-center gap-3 px-5 py-2 ${
                    selectedCategory === category.name && !selectedSubCategory
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <ChevronRight 
                    className={`h-4 w-4 transition-transform ${
                      isExpanded ? 'rotate-90' : ''
                    }`}
                  />
                  <span className="truncate flex-1 text-left">{category.name}</span>
                </button>

                {isExpanded && category.subCategories.length > 0 && (
                  <div className="ml-8">
                    {category.subCategories.map((subCat) => {
                      const subCatIssues = allIssues.filter(
                        i => i.category === category.name && i.subCategory === subCat.name
                      );
                      
                      return (
                        <button
                          key={subCat.id}
                          onClick={() => {
                            setSelectedCategory(category.name);
                            setSelectedSubCategory(subCat.name);
                          }}
                          className={`w-full flex items-center gap-3 px-5 py-2 ${
                            selectedSubCategory === subCat.name
                              ? 'bg-gray-100 text-gray-900'
                              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                          }`}
                        >
                          <span className="truncate flex-1 text-left">{subCat.name}</span>
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {viewMode === 'requirements' ? (
          <>
            {/* Requirements List */}
            <div className="w-[480px] bg-white border-r border-gray-200 flex flex-col">
              {/* Loading State */}
              {loadingRegulations && selectedSubCategory && (
                <div className="px-6 py-8 text-center text-gray-500">
                  <div className="animate-spin h-8 w-8 border-4 border-gray-300 border-t-[#1E3A8A] rounded-full mx-auto mb-3"></div>
                  <p>Loading regulations...</p>
                </div>
              )}
              
              {/* Error State */}
              {regulationsError && selectedSubCategory && !loadingRegulations && (
                <div className="px-6 py-4 bg-red-50 border-b border-red-200">
                  <div className="text-sm text-red-600">
                    <p className="font-medium mb-1">Error loading regulations</p>
                    <p>{regulationsError}</p>
                  </div>
                </div>
              )}
              
              <div className="flex-1 overflow-y-auto">
                {!loadingRegulations && selectedSubCategory && apiRegulations.length > 0 && apiRegulations.map((reg) => {
                  const isExpanded = expandedRegulations.has(reg.id);
                  const shouldTruncate = reg.description.length > 200;
                  const displayText = !isExpanded && shouldTruncate 
                    ? reg.description.slice(0, 200) 
                    : reg.description;
                  
                  return (
                    <div
                      key={reg.id}
                      className={`border-b border-gray-100 hover:bg-gray-50 transition-colors cursor-pointer ${
                        selectedRequirement?.regulation === reg.name ? 'bg-gray-50' : ''
                      }`}
                      onClick={() => setSelectedRequirement({
                        regulation: reg.name,
                        text: reg.description,
                        category: selectedCategory || '',
                        subCategory: selectedSubCategory || ''
                      })}
                    >
                      <div className="px-6 py-4">
                        <div className="flex items-center justify-between gap-2 mb-2">
                          <span className="text-sm font-medium text-[#1E3A8A]">
                            {reg.name}
                          </span>
                          <span className="text-xs px-2 py-1 bg-green-50 text-green-700 border border-green-200 rounded whitespace-nowrap">
                            {(reg.similarityScore * 100).toFixed(0)}%
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 leading-relaxed">
                          {displayText}
                          {!isExpanded && shouldTruncate && (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleRegulationExpansion(reg.id, e);
                              }}
                              className="text-[#1E3A8A] hover:underline ml-1 font-medium"
                            >
                              ...
                            </button>
                          )}
                        </div>
                        {isExpanded && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleRegulationExpansion(reg.id, e);
                            }}
                            className="text-[#1E3A8A] hover:underline text-sm mt-2 font-medium"
                          >
                            Show less
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
                
                {/* Show mock requirements if no API data */}
                {!loadingRegulations && !selectedSubCategory && filteredRequirements.map((req, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedRequirement(req)}
                    className={`w-full px-6 py-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                      selectedRequirement === req ? 'bg-gray-50' : ''
                    }`}
                  >
                    <div className="text-left">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="text-gray-400 text-xs font-mono">
                          {req.regulation}
                        </span>
                        <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600">
                          {req.subCategory}
                        </span>
                      </div>
                      <div className="text-sm text-gray-700 line-clamp-3 leading-relaxed">
                        {req.text}
                      </div>
                    </div>
                  </button>
                ))}
                
                {/* Empty state */}
                {!loadingRegulations && selectedSubCategory && apiRegulations.length === 0 && (
                  <div className="px-6 py-12 text-center text-gray-500">
                    <BarChart2 className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p className="mb-2">No regulations found</p>
                    <p className="text-sm">Try selecting a different subcategory</p>
                  </div>
                )}
              </div>
            </div>

            {/* Requirements Detail Panel */}
            <div className="flex-1 bg-white overflow-y-auto relative">
              {/* Voice Assistant Orb */}
              <VoiceAssistant 
                context={{
                  viewMode: 'requirements',
                  selectedCategory,
                  categoryDescription: mockRiskCategories.find(c => c.name === selectedCategory)?.description,
                  selectedSubCategory,
                  subCategoryDescription: mockRiskCategories
                    .find(c => c.name === selectedCategory)
                    ?.subCategories.find(sc => sc.name === selectedSubCategory)?.description,
                  selectedRequirement,
                  totalRequirements: filteredRequirements.length,
                }}
              />
              {selectedRequirement ? (
                <div className="max-w-4xl mx-auto py-12 px-16">
                  <div className="mb-10 pb-10 border-b border-gray-200">
                    <div className="flex items-center gap-3 mb-8">
                      <span className="text-xs px-3 py-1.5 uppercase tracking-wide bg-gray-100 text-gray-600">
                        Requirement
                      </span>
                    </div>
                    <h2 className="text-[#1E3A8A] text-3xl mb-5 font-mono">
                      {selectedRequirement.regulation}
                    </h2>
                  </div>

                  <div className="space-y-10">
                    {/* Context */}
                    <div>
                      <h3 className="text-xs text-gray-500 mb-5 uppercase tracking-wider">Context</h3>
                      <div className="bg-gray-50 border border-gray-200 divide-y divide-gray-200">
                        {(() => {
                          const categoryData = mockRiskCategories.find(c => c.name === selectedRequirement.category);
                          const categoryKey = `req-cat-${selectedRequirement.category}`;
                          const isCategoryExpanded = expandedDescriptions.has(categoryKey);
                          
                          return (
                            <button
                              onClick={() => toggleDescription(categoryKey)}
                              className="w-full text-left hover:bg-gray-100 transition-colors"
                            >
                              <div className="flex p-5">
                                <span className="w-44 text-gray-500 flex items-center gap-2">
                                  Category
                                  <ChevronRight className={`h-3.5 w-3.5 transition-transform ${isCategoryExpanded ? 'rotate-90' : ''}`} />
                                </span>
                                <div className="flex-1">
                                  <div className="text-gray-900">{selectedRequirement.category}</div>
                                  {isCategoryExpanded && categoryData && (
                                    <div className="mt-3 text-sm text-gray-600 leading-relaxed">
                                      {categoryData.description}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </button>
                          );
                        })()}
                        {(() => {
                          const categoryData = mockRiskCategories.find(c => c.name === selectedRequirement.category);
                          const subCategoryData = categoryData?.subCategories.find(sc => sc.name === selectedRequirement.subCategory);
                          const subCategoryKey = `req-subcat-${selectedRequirement.subCategory}`;
                          const isSubCategoryExpanded = expandedDescriptions.has(subCategoryKey);
                          
                          return (
                            <button
                              onClick={() => toggleDescription(subCategoryKey)}
                              className="w-full text-left hover:bg-gray-100 transition-colors"
                            >
                              <div className="flex p-5">
                                <span className="w-44 text-gray-500 flex items-center gap-2">
                                  Sub-category
                                  <ChevronRight className={`h-3.5 w-3.5 transition-transform ${isSubCategoryExpanded ? 'rotate-90' : ''}`} />
                                </span>
                                <div className="flex-1">
                                  <div className="text-gray-900">{selectedRequirement.subCategory}</div>
                                  {isSubCategoryExpanded && subCategoryData && (
                                    <div className="mt-3 text-sm text-gray-600 leading-relaxed">
                                      {subCategoryData.description}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </button>
                          );
                        })()}
                      </div>
                    </div>

                    {/* Requirement Text */}
                    <div>
                      <h3 className="text-xs text-gray-500 mb-5 uppercase tracking-wider">
                        Requirement Text
                      </h3>
                      <div className="border-l-2 border-[#1E3A8A] pl-6 py-4">
                        {(() => {
                          const requirementKey = `req-text-${selectedRequirement.regulation}`;
                          const isExpanded = expandedDescriptions.has(requirementKey);
                          const text = selectedRequirement.text;
                          const shouldTruncate = text.length > 300;
                          const displayText = shouldTruncate && !isExpanded ? text.slice(0, 300) : text;
                          
                          return (
                            <div>
                              <p className="text-gray-700 leading-relaxed text-[15px]">
                                "{displayText}
                                {shouldTruncate && !isExpanded && (
                                  <button
                                    onClick={() => toggleDescription(requirementKey)}
                                    className="text-[#1E3A8A] hover:underline ml-1 font-medium"
                                  >
                                    ...
                                  </button>
                                )}
                                "
                              </p>
                              {shouldTruncate && isExpanded && (
                                <button
                                  onClick={() => toggleDescription(requirementKey)}
                                  className="text-[#1E3A8A] hover:underline text-sm mt-2 font-medium"
                                >
                                  Show less
                                </button>
                              )}
                            </div>
                          );
                        })()}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <BarChart2 className="h-14 w-14 mx-auto mb-4 text-gray-300" />
                    <p className="text-gray-600 mb-2 text-lg">No requirement selected</p>
                    <p className="text-gray-400">Select a requirement to view details</p>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : viewMode === 'issues' ? (
          <>
            {/* Issue List */}
            <div className="w-[480px] bg-white border-r border-gray-200 flex flex-col">
              {/* Analysis Controls */}
              {selectedSubCategory && (
                <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                  <button
                    onClick={loadAnalysis}
                    disabled={loadingAnalysis}
                    className="w-full px-4 py-2 bg-[#1E3A8A] text-white rounded hover:bg-[#1E3A8A]/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {loadingAnalysis ? 'Analyzing...' : 'Analyze Overlaps & Contradictions'}
                  </button>
                  {analysisError && (
                    <div className="mt-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded px-3 py-2">
                      {analysisError}
                    </div>
                  )}
                </div>
              )}
              
              {/* Loading State for Regulations */}
              {loadingRegulations && selectedSubCategory && (
                <div className="px-6 py-8 text-center text-gray-500">
                  <div className="animate-spin h-8 w-8 border-4 border-gray-300 border-t-[#1E3A8A] rounded-full mx-auto mb-3"></div>
                  <p>Loading regulations...</p>
                </div>
              )}
              
              {/* Error State for Regulations */}
              {regulationsError && selectedSubCategory && !loadingRegulations && (
                <div className="px-6 py-4 bg-red-50 border-b border-red-200">
                  <div className="text-sm text-red-600">
                    <p className="font-medium mb-1">Error loading regulations</p>
                    <p>{regulationsError}</p>
                  </div>
                </div>
              )}
              
              <div className="flex-1 overflow-y-auto">
                {!loadingRegulations && Object.entries(groupedIssues).map(([type, issues]) => {
                  if (issues.length === 0) return null;
                  
                  return (
                    <div key={type}>
                      <div className="px-6 py-4 flex items-center gap-3 bg-white sticky top-0 border-b border-gray-100">
                        {type === 'Contradictions' && <Flag className="h-4 w-4 text-red-500" />}
                        <span className="text-gray-600">{type}</span>
                        <ChevronDown 
                          className="h-4 w-4 text-gray-400 cursor-pointer"
                          onClick={() => toggleSection(type)}
                        />
                      </div>

                      {expandedSections.has(type) && issues.map((issue) => (
                        <button
                          key={issue.id}
                          onClick={() => setSelectedIssue(issue)}
                          className={`w-full px-6 py-4 flex items-start gap-4 border-b border-gray-100 hover:bg-gray-50 transition-colors ${
                            selectedIssue?.id === issue.id ? 'bg-gray-50' : ''
                          }`}
                        >
                          <div className="flex-1 min-w-0 text-left pt-0.5">
                            <div className="flex items-center gap-2 mb-1.5">
                              <span className="text-gray-400 text-xs font-mono">
                                {issue.id.toUpperCase()}
                              </span>
                              {issue.type === 'contradiction' && (
                                <Flag className="h-3.5 w-3.5 text-red-500" />
                              )}
                            </div>
                            <div className="text-gray-900 mb-2">
                              {issue.reg1} × {issue.reg2}
                            </div>
                            <div className="text-sm text-gray-500 line-clamp-2 leading-relaxed">
                              {issue.description}
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  );
                })}
                
                {/* Empty state when no issues found */}
                {!loadingRegulations && !loadingAnalysis && selectedSubCategory && filteredIssues.length === 0 && (
                  <div className="px-6 py-12 text-center text-gray-500">
                    <AlertTriangle className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p className="mb-2">No issues found</p>
                    <p className="text-sm">Click "Analyze Overlaps & Contradictions" to search for issues</p>
                  </div>
                )}
              </div>
            </div>

            {/* Detail Panel */}
            <div className="flex-1 bg-white overflow-y-auto relative">
              {/* Voice Assistant Orb */}
              <VoiceAssistant 
                context={{
                  viewMode: 'issues',
                  selectedCategory,
                  categoryDescription: mockRiskCategories.find(c => c.name === selectedCategory)?.description,
                  selectedSubCategory,
                  subCategoryDescription: mockRiskCategories
                    .find(c => c.name === selectedCategory)
                    ?.subCategories.find(sc => sc.name === selectedSubCategory)?.description,
                  selectedIssue,
                  totalIssues: filteredIssues.length,
                }}
              />
              {selectedIssue ? (
                <div className="max-w-4xl mx-auto py-12 px-16">
                  {/* Header */}
                  <div className="mb-10 pb-10 border-b border-gray-200">
                    <div className="flex items-center gap-3 mb-8">
                      <span className={`text-xs px-3 py-1.5 uppercase tracking-wide ${
                        selectedIssue.type === 'overlap'
                          ? 'bg-gray-100 text-gray-600'
                          : 'bg-[#1E3A8A] text-white'
                      }`}>
                        {selectedIssue.type === 'overlap' ? 'Overlap' : 'Contradiction'}
                      </span>
                      {selectedIssue.severity && (
                        <span className={`text-xs px-3 py-1.5 ${
                          selectedIssue.severity === 'High'
                            ? 'bg-red-50 text-red-700 border border-red-200'
                            : selectedIssue.severity === 'Medium'
                            ? 'bg-orange-50 text-orange-700 border border-orange-200'
                            : 'bg-yellow-50 text-yellow-700 border border-yellow-200'
                        }`}>
                          {selectedIssue.severity}
                        </span>
                      )}
                    </div>
                    <h2 className="text-[#1E3A8A] text-3xl mb-5 font-mono">
                      {selectedIssue.reg1} × {selectedIssue.reg2}
                    </h2>
                    <p className="text-gray-600 leading-relaxed text-[15px]">
                      {selectedIssue.description}
                    </p>
                  </div>

                  {/* Details */}
                  <div className="space-y-10">
                    {/* Context */}
                    <div>
                      <h3 className="text-xs text-gray-500 mb-5 uppercase tracking-wider">Context</h3>
                      <div className="bg-gray-50 border border-gray-200 divide-y divide-gray-200">
                        {(() => {
                          const categoryData = mockRiskCategories.find(c => c.name === selectedIssue.category);
                          const categoryKey = `issue-cat-${selectedIssue.category}`;
                          const isCategoryExpanded = expandedDescriptions.has(categoryKey);
                          
                          return (
                            <button
                              onClick={() => toggleDescription(categoryKey)}
                              className="w-full text-left hover:bg-gray-100 transition-colors"
                            >
                              <div className="flex p-5">
                                <span className="w-44 text-gray-500 flex items-center gap-2">
                                  Category
                                  <ChevronRight className={`h-3.5 w-3.5 transition-transform ${isCategoryExpanded ? 'rotate-90' : ''}`} />
                                </span>
                                <div className="flex-1">
                                  <div className="text-gray-900">{selectedIssue.category}</div>
                                  {isCategoryExpanded && categoryData && (
                                    <div className="mt-3 text-sm text-gray-600 leading-relaxed">
                                      {categoryData.description}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </button>
                          );
                        })()}
                        {(() => {
                          const categoryData = mockRiskCategories.find(c => c.name === selectedIssue.category);
                          const subCategoryData = categoryData?.subCategories.find(sc => sc.name === selectedIssue.subCategory);
                          const subCategoryKey = `issue-subcat-${selectedIssue.subCategory}`;
                          const isSubCategoryExpanded = expandedDescriptions.has(subCategoryKey);
                          
                          return (
                            <button
                              onClick={() => toggleDescription(subCategoryKey)}
                              className="w-full text-left hover:bg-gray-100 transition-colors"
                            >
                              <div className="flex p-5">
                                <span className="w-44 text-gray-500 flex items-center gap-2">
                                  Sub-category
                                  <ChevronRight className={`h-3.5 w-3.5 transition-transform ${isSubCategoryExpanded ? 'rotate-90' : ''}`} />
                                </span>
                                <div className="flex-1">
                                  <div className="text-gray-900">{selectedIssue.subCategory}</div>
                                  {isSubCategoryExpanded && subCategoryData && (
                                    <div className="mt-3 text-sm text-gray-600 leading-relaxed">
                                      {subCategoryData.description}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </button>
                          );
                        })()}
                      </div>
                    </div>

                    {/* Conflicting Requirements or Overlap Excerpts */}
                    {selectedIssue.type === 'contradiction' && selectedIssue.requirement1 && selectedIssue.requirement2 ? (
                      <div>
                        <h3 className="text-xs text-gray-500 mb-5 uppercase tracking-wider">
                          Conflicting Requirements
                        </h3>
                        <div className="space-y-5">
                          <div className="border-l-2 border-[#1E3A8A] pl-6 py-3">
                            <p className="text-xs text-gray-500 mb-3 font-mono tracking-wide">
                              {selectedIssue.reg1}
                            </p>
                            <p className="text-gray-700 leading-relaxed text-[15px]">
                              "{selectedIssue.requirement1}"
                            </p>
                          </div>
                          <div className="border-l-2 border-[#1E3A8A] pl-6 py-3">
                            <p className="text-xs text-gray-500 mb-3 font-mono tracking-wide">
                              {selectedIssue.reg2}
                            </p>
                            <p className="text-gray-700 leading-relaxed text-[15px]">
                              "{selectedIssue.requirement2}"
                            </p>
                          </div>
                        </div>
                      </div>
                    ) : selectedIssue.type === 'overlap' && selectedIssue.excerpt1 && selectedIssue.excerpt2 ? (
                      <div>
                        <h3 className="text-xs text-gray-500 mb-5 uppercase tracking-wider">
                          Excerpts
                        </h3>
                        <div className="space-y-5">
                          <div className="border-l-2 border-[#1E3A8A] pl-6 py-3">
                            <p className="text-xs text-gray-500 mb-3 font-mono tracking-wide">
                              {selectedIssue.reg1}
                            </p>
                            <p className="text-gray-700 leading-relaxed text-[15px]">
                              "{selectedIssue.excerpt1}"
                            </p>
                          </div>
                          <div className="border-l-2 border-[#1E3A8A] pl-6 py-3">
                            <p className="text-xs text-gray-500 mb-3 font-mono tracking-wide">
                              {selectedIssue.reg2}
                            </p>
                            <p className="text-gray-700 leading-relaxed text-[15px]">
                              "{selectedIssue.excerpt2}"
                            </p>
                          </div>
                        </div>
                      </div>
                    ) : null}

                    {/* Regulations */}
                    <div>
                      <h3 className="text-xs text-gray-500 mb-5 uppercase tracking-wider">
                        Affected Regulations
                      </h3>
                      <div className="space-y-4">
                        <div className="p-5 bg-gray-50 border border-gray-200">
                          <p className="font-mono text-[#1E3A8A]">{selectedIssue.reg1}</p>
                        </div>
                        <div className="p-5 bg-gray-50 border border-gray-200">
                          <p className="font-mono text-[#1E3A8A]">{selectedIssue.reg2}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Circle className="h-14 w-14 mx-auto mb-4 text-gray-300" />
                    <p className="text-gray-600 mb-2 text-lg">No issue selected</p>
                    <p className="text-gray-400">Select an issue to view details</p>
                  </div>
                </div>
              )}
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}