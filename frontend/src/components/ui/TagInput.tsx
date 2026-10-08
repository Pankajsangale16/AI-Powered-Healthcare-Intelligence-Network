import React, { useState, useRef, useEffect } from 'react';
import { X, Plus, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { SymptomItem } from '@/lib/api';

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  availableOptions?: SymptomItem[];
  placeholder?: string;
  label?: string;
  helperText?: string;
  error?: string;
}

export const TagInput: React.FC<TagInputProps> = ({
  value,
  onChange,
  availableOptions = [],
  placeholder = 'Type symptom or paste comma-separated...',
  label,
  helperText,
  error,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter available options based on input
  const filteredOptions = availableOptions
    .filter((opt) => {
      const q = inputValue.toLowerCase().trim();
      if (!q) return false;
      const matches =
        opt.label.toLowerCase().includes(q) ||
        opt.id.toLowerCase().includes(q) ||
        opt.query_name.toLowerCase().includes(q);
      const notSelected = !value.includes(opt.id) && !value.includes(opt.label);
      return matches && notSelected;
    })
    .slice(0, 8);

  const addTag = (tag: string) => {
    const trimmed = tag.trim();
    if (!trimmed) return;
    if (!value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setInputValue('');
    setIsOpen(false);
  };

  const removeTag = (indexToRemove: number) => {
    onChange(value.filter((_, idx) => idx !== indexToRemove));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      if (filteredOptions.length > 0 && isOpen) {
        addTag(filteredOptions[0].label);
      } else if (inputValue.trim()) {
        addTag(inputValue);
      }
    } else if (e.key === 'Backspace' && !inputValue && value.length > 0) {
      removeTag(value.length - 1);
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pastedText = e.clipboardData.getData('text');
    if (pastedText.includes(',')) {
      const items = pastedText
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
      const newTags = [...value];
      for (const item of items) {
        if (!newTags.includes(item)) {
          newTags.push(item);
        }
      }
      onChange(newTags);
      setInputValue('');
    } else {
      setInputValue(pastedText);
    }
  };

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={containerRef} className="w-full space-y-1.5">
      {label && <label className="block text-sm font-medium text-foreground">{label}</label>}

      <div
        onClick={() => inputRef.current?.focus()}
        className={cn(
          'flex min-h-[52px] w-full flex-wrap items-center gap-2 rounded-lg border border-input bg-background p-2 transition-colors duration-150',
          'focus-within:border-ring focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-1',
          error && 'border-destructive'
        )}
      >
        {value.map((tag, idx) => (
          <span
            key={idx}
            className="inline-flex items-center gap-1.5 rounded-md bg-primary/10 border border-primary/20 px-3 py-1.5 text-sm font-medium text-primary select-none animate-fadeIn"
          >
            <span>{tag}</span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                removeTag(idx);
              }}
              className="touch-target -mr-1 -my-1 h-6 w-6 flex items-center justify-center rounded-full hover:bg-primary/20 active:bg-primary/30 text-primary transition-colors"
              aria-label={`Remove ${tag}`}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </span>
        ))}

        <div className="relative flex-1 min-w-[140px]">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            onKeyDown={handleKeyDown}
            onPaste={handlePaste}
            placeholder={value.length === 0 ? placeholder : 'Add more...'}
            className="w-full bg-transparent px-2 py-1 text-base text-foreground placeholder:text-muted-foreground focus:outline-none"
            style={{ fontSize: '16px' }}
          />
        </div>
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && filteredOptions.length > 0 && (
        <div className="relative z-50">
          <ul className="absolute top-1 left-0 right-0 max-h-56 overflow-auto rounded-lg border border-border bg-popover text-popover-foreground shadow-lg py-1">
            {filteredOptions.map((opt) => (
              <li
                key={opt.id}
                onClick={() => addTag(opt.label)}
                className="flex items-center justify-between px-4 py-3 text-sm hover:bg-muted active:bg-muted/80 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-muted-foreground" />
                  <span className="font-medium">{opt.label}</span>
                </div>
                <Plus className="h-4 w-4 text-primary" />
              </li>
            ))}
          </ul>
        </div>
      )}

      {error && <p className="text-xs text-destructive mt-1">{error}</p>}
      {helperText && !error && <p className="text-xs text-muted-foreground mt-1">{helperText}</p>}
    </div>
  );
};
