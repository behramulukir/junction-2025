import { AlertTriangle, ArrowLeftRight } from 'lucide-react';
import { Contradiction } from '../data/mockData';

interface ContradictionCardProps {
  contradiction: Contradiction;
}

const severityColors = {
  High: 'bg-red-100 text-red-800 border-red-200',
  Medium: 'bg-orange-100 text-orange-800 border-orange-200',
  Low: 'bg-yellow-100 text-yellow-800 border-yellow-200'
};

export function ContradictionCard({ contradiction }: ContradictionCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border-2 border-[#DC2626] overflow-hidden">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start gap-3 mb-4">
          <div className="flex-shrink-0 w-10 h-10 bg-red-50 rounded-lg flex items-center justify-center">
            <AlertTriangle className="h-5 w-5 text-[#DC2626]" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-2">
              <span className="text-gray-900">{contradiction.regulationPair[0]}</span>
              <ArrowLeftRight className="h-4 w-4 text-gray-400" />
              <span className="text-gray-900">{contradiction.regulationPair[1]}</span>
            </div>
            <span className={`inline-block px-3 py-1 rounded-full border text-xs ${severityColors[contradiction.severity]}`}>
              {contradiction.severity} Severity
            </span>
          </div>
        </div>

        {/* Description */}
        <p className="text-gray-700 mb-6">{contradiction.description}</p>

        {/* Side-by-Side Comparison */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-gray-900 mb-2">{contradiction.regulationPair[0]}</p>
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <p className="text-gray-700">"{contradiction.conflictingRequirements.regulation1}"</p>
            </div>
          </div>
          <div>
            <p className="text-gray-900 mb-2">{contradiction.regulationPair[1]}</p>
            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <p className="text-gray-700">"{contradiction.conflictingRequirements.regulation2}"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
