import { FileText } from 'lucide-react';

interface MetricCardProps {
  value: string;
  label: string;
  iconColor: string;
}

export function MetricCard({ value, label, iconColor }: MetricCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-3xl text-gray-900 mb-1">{value}</p>
          <p className="text-gray-600">{label}</p>
        </div>
        <div className={`${iconColor}`}>
          <FileText className="h-8 w-8" />
        </div>
      </div>
    </div>
  );
}
