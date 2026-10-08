import React from 'react';
import { AlertTriangle } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full border-t border-border bg-card/60 text-card-foreground mt-auto">
      {/* Disclaimer Strip */}
      <div className="bg-amber-500/10 border-b border-amber-500/20 py-2.5 px-4 text-center">
        <p className="text-xs text-amber-700 dark:text-amber-300 flex items-center justify-center gap-1.5 font-medium">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          <span>Educational use only — not a substitute for clinical diagnosis or emergency medical care.</span>
        </p>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          {/* Brand & Attribution */}
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">
              AI-Powered Healthcare Intelligence Network © 2026
            </p>
            <p className="text-xs text-muted-foreground">
              Developed for clinical exploration, predictive insights & health education.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

