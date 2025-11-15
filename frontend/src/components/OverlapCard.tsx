import { ArrowLeftRight, ChevronDown, ChevronUp } from 'lucide-react';
import { Overlap } from '../data/mockData';
import { useState } from 'react';

interface OverlapCardProps {
  overlap: Overlap;
}

const typeColors = {
  Duplicate: 'bg-purple-100 text-purple-800 border-purple-200',
  Complementary: 'bg-blue-100 text-blue-800 border-blue-200',
  Conflicting: 'bg-orange-100 text-orange-800 border-orange-200'
};

export function OverlapCard({ overlap }: OverlapCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start gap-3 mb-4">
          <div className="flex-shrink-0 w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center">
            <ArrowLeftRight className="h-5 w-5 text-[#F59E0B]" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-gray-900">{overlap.regulationPair[0]}</span>
              <ArrowLeftRight className="h-4 w-4 text-gray-400" />
              <span className="text-gray-900">{overlap.regulationPair[1]}</span>
            </div>
            <span className={`inline-block px-3 py-1 rounded-full border text-xs ${typeColors[overlap.type]}`}>
              {overlap.type}
            </span>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-700 mb-4">{overlap.description}</p>

        {/* Confidence Score */}
        <div className="flex items-center gap-3 mb-4">
          <span className="text-gray-600">Confidence:</span>
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-[#1E3A8A] h-2 rounded-full"
              style={{ width: `${overlap.confidenceScore * 100}%` }}
            />
          </div>
          <span className="text-gray-900">{(overlap.confidenceScore * 100).toFixed(0)}%</span>
        </div>

        {/* View Details Toggle */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-2 text-[#1E3A8A] hover:text-[#1E3A8A]/80 transition-colors"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4" />
              <span>Hide Details</span>
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              <span>View Details</span>
            </>
          )}
        </button>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="bg-gray-50 p-6 border-t border-gray-200 space-y-4">
          <div>
            <p className="text-gray-900 mb-2">{overlap.regulationPair[0]}</p>
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <p className="text-gray-700 italic">"{overlap.excerpts.regulation1}"</p>
            </div>
          </div>
          <div>
            <p className="text-gray-900 mb-2">{overlap.regulationPair[1]}</p>
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <p className="text-gray-700 italic">"{overlap.excerpts.regulation2}"</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
