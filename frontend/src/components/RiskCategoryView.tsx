import { ChevronRight, Filter } from 'lucide-react';
import { RiskCategory } from '../data/mockData';
import { SubCategoryCard } from './SubCategoryCard';
import { useState } from 'react';

interface RiskCategoryViewProps {
  category: RiskCategory;
  onBreadcrumbClick: (level: 'home' | 'category') => void;
  onSubCategoryClick: (subCategoryId: string) => void;
}

type SortOption = 'alphabetical' | 'overlaps' | 'contradictions';

export function RiskCategoryView({ category, onBreadcrumbClick, onSubCategoryClick }: RiskCategoryViewProps) {
  const [sortBy, setSortBy] = useState<SortOption>('alphabetical');

  const sortedSubCategories = [...category.subCategories].sort((a, b) => {
    switch (sortBy) {
      case 'overlaps':
        return b.overlapCount - a.overlapCount;
      case 'contradictions':
        return b.contradictionCount - a.contradictionCount;
      case 'alphabetical':
      default:
        return a.name.localeCompare(b.name);
    }
  });

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
        <span className="text-gray-900">{category.name}</span>
      </nav>

      {/* Category Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
        <h1 className="text-gray-900 mb-4">{category.name}</h1>
        <p className="text-gray-600 mb-6 max-w-3xl">
          {category.description}
        </p>

        {/* Aggregate Statistics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl text-[#1E3A8A] mb-1">{category.regulationCount.toLocaleString()}</p>
            <p className="text-gray-600">Total Regulations</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-2xl text-[#1E3A8A] mb-1">{category.subCategoryCount}</p>
            <p className="text-gray-600">Sub-Categories</p>
          </div>
          <div className="bg-amber-50 rounded-lg p-4">
            <p className="text-2xl text-[#F59E0B] mb-1">{category.overlapCount}</p>
            <p className="text-gray-600">Total Overlaps</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4">
            <p className="text-2xl text-[#DC2626] mb-1">{category.contradictionCount}</p>
            <p className="text-gray-600">Contradictions</p>
          </div>
        </div>
      </div>

      {/* Filter/Sort Section */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-gray-900">Sub-Categories</h2>
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-gray-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="border border-gray-300 rounded-lg px-3 py-2 bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#1E3A8A]"
          >
            <option value="alphabetical">Alphabetical</option>
            <option value="overlaps">Most Overlaps</option>
            <option value="contradictions">Most Contradictions</option>
          </select>
        </div>
      </div>

      {/* Sub-Categories Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {sortedSubCategories.length > 0 ? (
          sortedSubCategories.map((subCategory) => (
            <SubCategoryCard
              key={subCategory.id}
              subCategory={subCategory}
              onClick={() => onSubCategoryClick(subCategory.id)}
            />
          ))
        ) : (
          <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <p className="text-gray-500">Sub-category data is being processed. Please check back later or explore other risk categories.</p>
          </div>
        )}
      </div>
    </div>
  );
}