import { TrendingDown, BarChart3, Droplet, Settings, Shield, Target, Network, Lock, Leaf, Scale, ChevronRight } from 'lucide-react';
import { RiskCategory } from '../data/mockData';

interface RiskCategoryCardProps {
  category: RiskCategory;
  onClick: () => void;
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  TrendingDown,
  BarChart3,
  Droplet,
  Settings,
  Shield,
  Target,
  Network,
  Lock,
  Leaf,
  Scale
};

export function RiskCategoryCard({ category, onClick }: RiskCategoryCardProps) {
  const IconComponent = iconMap[category.icon] || Settings;
  
  const overlapPercentage = Math.min((category.overlapCount / category.regulationCount) * 100, 100);

  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-lg hover:-translate-y-0.5 transition-all text-left w-full group"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-4 flex-1">
          <div className="flex-shrink-0 w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
            <IconComponent className="h-6 w-6 text-[#1E3A8A]" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-gray-900 mb-2">{category.name}</h3>
            <div className="flex flex-wrap gap-4 text-gray-600">
              <div className="flex items-center gap-1">
                <span>{category.regulationCount.toLocaleString()}</span>
                <span>regulations</span>
              </div>
              <div className="flex items-center gap-1">
                <span>{category.subCategoryCount}</span>
                <span>sub-categories</span>
              </div>
            </div>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-gray-400 group-hover:text-[#1E3A8A] transition-colors flex-shrink-0 mt-1" />
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-amber-50 rounded-lg p-3">
          <p className="text-[#F59E0B] mb-0.5">{category.overlapCount}</p>
          <p className="text-gray-600">Overlaps</p>
        </div>
        <div className="bg-red-50 rounded-lg p-3">
          <p className="text-[#DC2626] mb-0.5">{category.contradictionCount}</p>
          <p className="text-gray-600">Contradictions</p>
        </div>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="flex items-center justify-between mb-2 text-gray-600">
          <span>Overlap density</span>
          <span>{overlapPercentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-[#F59E0B] h-2 rounded-full transition-all"
            style={{ width: `${overlapPercentage}%` }}
          />
        </div>
      </div>
    </button>
  );
}
