import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressRingProps {
  value: number; // 0 to 100
  size?: number;
  strokeWidth?: number;
  className?: string;
  riskLevel?: 'Low' | 'Moderate' | 'High' | 'Very High';
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  value,
  size = 140,
  strokeWidth = 12,
  className,
  riskLevel,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const clampedValue = Math.min(Math.max(value, 0), 100);
  const strokeDashoffset = circumference - (clampedValue / 100) * circumference;

  const getColor = () => {
    if (riskLevel === 'Low' || clampedValue <= 25) return 'text-success stroke-success';
    if (riskLevel === 'Moderate' || clampedValue <= 40) return 'text-warning stroke-warning';
    if (riskLevel === 'High' || clampedValue <= 70) return 'text-amber-500 stroke-amber-500';
    return 'text-destructive stroke-destructive';
  };

  return (
    <div className={cn('relative inline-flex items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-muted/40"
          fill="transparent"
        />
        {/* Progress Arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={cn('transition-all duration-700 ease-out', getColor())}
          fill="transparent"
        />
      </svg>
      {/* Center Value */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="text-3xl font-bold tracking-tight">{clampedValue.toFixed(1)}%</span>
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider mt-0.5">
          {riskLevel || 'Risk Score'}
        </span>
      </div>
    </div>
  );
};
