import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: React.ReactNode;
  isBottomSheetOnMobile?: boolean;
  className?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  isBottomSheetOnMobile = true,
  className,
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 animate-fadeIn">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal/Sheet Container */}
      <div
        className={cn(
          'relative z-50 w-full bg-card text-card-foreground shadow-2xl transition-all',
          isBottomSheetOnMobile
            ? 'rounded-t-2xl sm:rounded-2xl max-h-[90dvh] sm:max-h-[85vh] sm:max-w-lg'
            : 'rounded-2xl max-w-lg max-h-[85vh]',
          'flex flex-col overflow-hidden',
          className
        )}
      >
        {/* Handle bar on mobile bottom sheet */}
        {isBottomSheetOnMobile && (
          <div className="sm:hidden flex justify-center pt-3 pb-1">
            <div className="h-1.5 w-12 rounded-full bg-muted-foreground/30" />
          </div>
        )}

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div>
            {title && <h3 className="text-lg font-semibold leading-none">{title}</h3>}
            {description && <p className="text-xs text-muted-foreground mt-1">{description}</p>}
          </div>
          <button
            onClick={onClose}
            className="touch-target h-10 w-10 -mr-2 rounded-full flex items-center justify-center hover:bg-muted text-muted-foreground transition-colors"
            aria-label="Close modal"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto p-6 safe-pb flex-1">{children}</div>
      </div>
    </div>
  );
};
