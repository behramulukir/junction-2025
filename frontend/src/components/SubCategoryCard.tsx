import { ChevronRight, FileText } from 'lucide-react';
import { SubCategory } from '../data/mockData';

interface SubCategoryCardProps {
  subCategory: SubCategory;
  onClick: () => void;
}

export function SubCategoryCard({ subCategory, onClick }: SubCategoryCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all text-left w-full group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-gray-900 mb-2">{subCategory.name}</h3>
          <div className="flex items-center gap-2 text-gray-600">
            <FileText className="h-4 w-4" />
            <span>Top {subCategory.paragraphsAnalyzed.toLocaleString()} paragraphs analyzed</span>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-[#1E3A8A] transition-colors flex-shrink-0" />
      </div>

      {/* Metrics Row */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#F59E0B]" />
          <span className="text-gray-900">{subCategory.overlapCount}</span>
          <span className="text-gray-600">overlaps</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-[#DC2626]" />
          <span className="text-gray-900">{subCategory.contradictionCount}</span>
          <span className="text-gray-600">contradictions</span>
        </div>
      </div>
    </button>
  );
}
