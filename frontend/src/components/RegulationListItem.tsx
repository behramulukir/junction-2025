import { ChevronDown, ChevronRight } from 'lucide-react';
import { Regulation } from '../data/mockData';
import { useState } from 'react';

interface RegulationListItemProps {
  regulation: Regulation;
}

export function RegulationListItem({ regulation }: RegulationListItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:border-[#1E3A8A] transition-colors">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 flex items-start justify-between gap-3 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex-1 min-w-0">
          <p className="text-gray-900 mb-1">{regulation.name}</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-[#1E3A8A] h-1.5 rounded-full"
                style={{ width: `${regulation.similarityScore * 100}%` }}
              />
            </div>
            <span className="text-gray-600 flex-shrink-0">
              {(regulation.similarityScore * 100).toFixed(0)}%
            </span>
          </div>
        </div>
        {isExpanded ? (
          <ChevronDown className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
          <p className="text-gray-700">{regulation.description}</p>
        </div>
      )}
    </div>
  );
}
