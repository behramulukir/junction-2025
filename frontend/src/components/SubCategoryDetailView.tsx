import { ChevronRight } from 'lucide-react';
import { RiskCategory, SubCategory } from '../data/mockData';
import { RegulationListItem } from './RegulationListItem';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { OverlapCard } from './OverlapCard';
import { ContradictionCard } from './ContradictionCard';

interface SubCategoryDetailViewProps {
  category: RiskCategory;
  subCategory: SubCategory;
  onBreadcrumbClick: (level: 'home' | 'category') => void;
}

export function SubCategoryDetailView({ category, subCategory, onBreadcrumbClick }: SubCategoryDetailViewProps) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 mb-6 text-gray-600">
        <button
          onClick={() => onBreadcrumbClick('home')}
          className="hover:text-[#1E3A8A] transition-colors"
        >
          Home
        </button>
        <ChevronRight className="h-4 w-4" />
        <button
          onClick={() => onBreadcrumbClick('category')}
          className="hover:text-[#1E3A8A] transition-colors"
        >
          {category.name}
        </button>
        <ChevronRight className="h-4 w-4" />
        <span className="text-gray-900">{subCategory.name}</span>
      </nav>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
        <h1 className="text-gray-900 mb-4">{subCategory.name}</h1>
        <div className="flex flex-wrap gap-6 text-gray-600">
          <div>
            <span className="text-gray-900">{subCategory.paragraphsAnalyzed.toLocaleString()}</span> paragraphs analyzed
          </div>
          <div>
            <span className="text-[#F59E0B]">{subCategory.overlapCount}</span> overlaps found
          </div>
          <div>
            <span className="text-[#DC2626]">{subCategory.contradictionCount}</span> contradictions detected
          </div>
        </div>
      </div>

      {/* Two-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left Panel - Regulations List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-24">
            <h2 className="text-gray-900 mb-4">Relevant Regulations</h2>
            <div className="space-y-3 max-h-[calc(100vh-300px)] overflow-y-auto">
              {subCategory.regulations.length > 0 ? (
                subCategory.regulations.map((regulation) => (
                  <RegulationListItem key={regulation.id} regulation={regulation} />
                ))
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No regulations data available for this sub-category</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right Panel - Overlaps and Contradictions */}
        <div className="lg:col-span-3">
          <Tabs defaultValue="overlaps" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="overlaps" className="data-[state=active]:bg-[#1E3A8A] data-[state=active]:text-white">
                Overlaps ({subCategory.overlapCount})
              </TabsTrigger>
              <TabsTrigger value="contradictions" className="data-[state=active]:bg-[#1E3A8A] data-[state=active]:text-white">
                Contradictions ({subCategory.contradictionCount})
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overlaps" className="space-y-4">
              {subCategory.overlaps.length > 0 ? (
                subCategory.overlaps.map((overlap) => (
                  <OverlapCard key={overlap.id} overlap={overlap} />
                ))
              ) : (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                  <p className="text-gray-500">No overlaps detected for this sub-category</p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="contradictions" className="space-y-4">
              {subCategory.contradictions.length > 0 ? (
                subCategory.contradictions.map((contradiction) => (
                  <ContradictionCard key={contradiction.id} contradiction={contradiction} />
                ))
              ) : (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
                  <p className="text-gray-500">No contradictions detected for this sub-category</p>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
