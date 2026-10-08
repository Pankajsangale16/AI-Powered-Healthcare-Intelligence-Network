import React from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle, AlertTriangle, CheckCircle, Info, RefreshCw } from 'lucide-react';
import { Button } from './Button';

export const Skeleton: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, ...props }) => (
  <div className={cn('animate-pulse rounded-md bg-muted/60', className)} {...props} />
);

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'danger';
  title?: string;
}

export const Alert: React.FC<AlertProps> = ({
  className,
  variant = 'info',
  title,
  children,
  ...props
}) => {
  const icons = {
    info: <Info className="h-5 w-5 text-info shrink-0" />,
    success: <CheckCircle className="h-5 w-5 text-success shrink-0" />,
    warning: <AlertTriangle className="h-5 w-5 text-warning shrink-0" />,
    danger: <AlertCircle className="h-5 w-5 text-destructive shrink-0" />,
  };

  const borders = {
    info: 'border-info/30 bg-info/10 text-foreground',
    success: 'border-success/30 bg-success/10 text-foreground',
    warning: 'border-warning/30 bg-warning/10 text-foreground',
    danger: 'border-destructive/30 bg-destructive/10 text-foreground',
  };

  return (
    <div
      role="alert"
      className={cn('flex items-start gap-3 rounded-xl border p-4 text-sm leading-relaxed', borders[variant], className)}
      {...props}
    >
      {icons[variant]}
      <div className="flex-1">
        {title && <h5 className="font-semibold mb-1 leading-none tracking-tight">{title}</h5>}
        <div className="text-sm opacity-95">{children}</div>
      </div>
    </div>
  );
};

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className,
}) => (
  <div className={cn('flex flex-col items-center justify-center p-8 text-center rounded-xl border border-dashed border-border bg-card/50', className)}>
    {icon && <div className="mb-4 text-muted-foreground p-3 bg-muted rounded-full">{icon}</div>}
    <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
    {description && <p className="text-sm text-muted-foreground max-w-sm mb-4">{description}</p>}
    {action && <div className="mt-2">{action}</div>}
  </div>
);

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
  className?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  onRetry,
  className,
}) => (
  <div className={cn('flex flex-col items-center justify-center p-6 text-center rounded-xl border border-destructive/20 bg-destructive/5', className)}>
    <div className="mb-3 text-destructive p-3 bg-destructive/10 rounded-full">
      <AlertCircle className="h-6 w-6" />
    </div>
    <h4 className="text-base font-semibold text-foreground mb-1">{title}</h4>
    <p className="text-sm text-muted-foreground max-w-md mb-4">{message}</p>
    {onRetry && (
      <Button variant="outline" size="sm" onClick={onRetry} className="gap-2">
        <RefreshCw className="h-4 w-4" /> Try Again
      </Button>
    )}
  </div>
);
