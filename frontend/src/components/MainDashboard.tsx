import { MetricCard } from './MetricCard';
import { RiskCategoryCard } from './RiskCategoryCard';
import { mockRiskCategories } from '../data/mockData';

interface MainDashboardProps {
  onCategoryClick: (categoryId: string) => void;
}

export function MainDashboard({ onCategoryClick }: MainDashboardProps) {
  const totalOverlaps = mockRiskCategories.reduce((sum, cat) => sum + cat.overlapCount, 0);
  const totalContradictions = mockRiskCategories.reduce((sum, cat) => sum + cat.contradictionCount, 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Hero Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <MetricCard
          value="7M"
          label="Paragraphs Analyzed"
          iconColor="text-[#1E3A8A]"
        />
        <MetricCard
          value="94,000"
          label="Regulations"
          iconColor="text-[#1E3A8A]"
        />
        <MetricCard
          value={totalOverlaps.toString()}
          label="Overlaps Found"
          iconColor="text-[#F59E0B]"
        />
        <MetricCard
          value={totalContradictions.toString()}
          label="Contradictions Detected"
          iconColor="text-[#DC2626]"
        />
      </div>

      {/* Risk Categories Grid */}
      <div>
        <h2 className="text-[#1E3A8A] mb-6">Risk Categories</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {mockRiskCategories.map((category) => (
            <RiskCategoryCard
              key={category.id}
              category={category}
              onClick={() => onCategoryClick(category.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
