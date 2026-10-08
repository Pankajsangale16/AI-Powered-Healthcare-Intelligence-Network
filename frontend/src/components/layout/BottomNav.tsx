import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, Stethoscope, Pill, Heart, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export const bottomTabs = [
  { path: '/', label: 'Home', icon: Activity },
  { path: '/disease', label: 'Disease', icon: Stethoscope },
  { path: '/drugs', label: 'Drugs', icon: Pill },
  { path: '/heart', label: 'Heart', icon: Heart },
  { path: '/medibot', label: 'Medibot', icon: MessageSquare },
];

export const BottomNav: React.FC = () => {
  return (
    <nav
      aria-label="Mobile Navigation"
      className="md:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-card/95 backdrop-blur-md safe-pb shadow-lg"
    >
      <div className="flex h-16 items-center justify-around px-1">
        {bottomTabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={({ isActive }) =>
                cn(
                  'flex flex-1 flex-col items-center justify-center py-1 transition-all touch-target select-none',
                  isActive
                    ? 'text-primary font-semibold'
                    : 'text-muted-foreground hover:text-foreground'
                )
              }
            >
              {({ isActive }) => (
                <>
                  <div
                    className={cn(
                      'flex h-8 w-12 items-center justify-center rounded-full transition-colors',
                      isActive ? 'bg-primary/15' : 'bg-transparent'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="text-[11px] leading-tight mt-0.5">{tab.label}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};
