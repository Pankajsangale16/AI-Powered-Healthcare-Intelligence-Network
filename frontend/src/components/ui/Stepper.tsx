import React from 'react';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StepItem {
  id: string;
  title: string;
  description?: string;
}

interface StepperProps {
  steps: StepItem[];
  currentStep: number;
  onStepClick?: (stepIndex: number) => void;
  className?: string;
}

export const Stepper: React.FC<StepperProps> = ({
  steps,
  currentStep,
  onStepClick,
  className,
}) => {
  return (
    <nav aria-label="Progress Stepper" className={cn('w-full py-2', className)}>
      <ol className="flex items-center justify-between w-full">
        {steps.map((step, idx) => {
          const isCompleted = idx < currentStep;
          const isCurrent = idx === currentStep;

          return (
            <li
              key={step.id}
              className={cn('relative flex-1 flex flex-col items-center', idx !== steps.length - 1 && 'pr-2')}
            >
              {/* Connector line */}
              {idx !== steps.length - 1 && (
                <div
                  className={cn(
                    'absolute top-4 left-1/2 w-full h-[2px] -translate-y-1/2 transition-colors duration-300',
                    idx < currentStep ? 'bg-primary' : 'bg-muted'
                  )}
                  style={{ width: '100%', left: '50%' }}
                  aria-hidden="true"
                />
              )}

              {/* Step Circle */}
              <button
                type="button"
                disabled={!onStepClick || idx > currentStep}
                onClick={() => onStepClick && onStepClick(idx)}
                className={cn(
                  'relative z-10 flex h-9 w-9 items-center justify-center rounded-full text-xs font-semibold transition-all duration-200 select-none touch-target',
                  isCompleted && 'bg-primary text-primary-foreground',
                  isCurrent && 'border-2 border-primary bg-background text-primary shadow-sm ring-4 ring-primary/15',
                  !isCompleted && !isCurrent && 'border border-border bg-muted/60 text-muted-foreground',
                  onStepClick && idx <= currentStep && 'cursor-pointer hover:scale-105 active:scale-95'
                )}
                aria-current={isCurrent ? 'step' : undefined}
                aria-label={`Step ${idx + 1}: ${step.title}`}
              >
                {isCompleted ? <Check className="h-4 w-4" /> : idx + 1}
              </button>

              {/* Label */}
              <span
                className={cn(
                  'mt-2 text-xs font-medium text-center truncate max-w-[80px] sm:max-w-none transition-colors',
                  isCurrent ? 'text-primary font-semibold' : isCompleted ? 'text-foreground' : 'text-muted-foreground'
                )}
              >
                {step.title}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
};
