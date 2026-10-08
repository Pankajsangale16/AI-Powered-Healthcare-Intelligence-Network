import React, { useState } from 'react';
import { Bot, User, Copy, Check, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatBubbleProps {
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: string[];
  isStreaming?: boolean;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({
  role,
  content,
  sources = [],
  isStreaming = false,
}) => {
  const [copied, setCopied] = useState(false);

  const isUser = role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Safe formatting of text with bold, bullet points, headers without dangerous HTML injection
  const formatMarkdown = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      // Heading 1 or 2
      if (line.startsWith('### ')) {
        return (
          <h4 key={idx} className="text-base font-bold text-foreground mt-3 mb-1">
            {line.replace('### ', '')}
          </h4>
        );
      }
      if (line.startsWith('## ') || line.startsWith('# ')) {
        return (
          <h3 key={idx} className="text-lg font-bold text-foreground mt-4 mb-2">
            {line.replace(/^#+\s/, '')}
          </h3>
        );
      }
      // Bullet list item
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        const cleanLine = line.trim().replace(/^[-*]\s/, '');
        return (
          <li key={idx} className="ml-4 list-disc text-sm my-0.5 leading-relaxed">
            {renderBoldText(cleanLine)}
          </li>
        );
      }
      // Numbered list item
      if (/^\d+\.\s/.test(line.trim())) {
        const cleanLine = line.trim().replace(/^\d+\.\s/, '');
        return (
          <div key={idx} className="flex items-start gap-2 text-sm my-1 leading-relaxed">
            <span className="font-semibold text-primary">{line.trim().match(/^\d+\./)?.[0]}</span>
            <span>{renderBoldText(cleanLine)}</span>
          </div>
        );
      }
      if (!line.trim()) {
        return <div key={idx} className="h-2" />;
      }
      return (
        <p key={idx} className="text-sm leading-relaxed my-1">
          {renderBoldText(line)}
        </p>
      );
    });
  };

  // Helper to safely render **bold** segments
  const renderBoldText = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={i} className="font-semibold text-foreground">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });
  };

  return (
    <div className={cn('flex w-full gap-3 py-2', isUser ? 'justify-end' : 'justify-start')}>
      {!isUser && (
        <div className="flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-full bg-primary/10 border border-primary/20 text-primary">
          <Bot className="h-5 w-5" />
        </div>
      )}

      <div className={cn('flex flex-col space-y-1.5 max-w-[88%] sm:max-w-[80%]', isUser ? 'items-end' : 'items-start')}>
        <div
          className={cn(
            'relative rounded-2xl px-4 py-3 text-sm shadow-sm transition-all',
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-sm'
              : 'bg-card border border-border text-card-foreground rounded-bl-sm'
          )}
        >
          <div className="prose prose-sm max-w-none break-words">
            {formatMarkdown(content)}
            {isStreaming && (
              <span className="inline-block h-3.5 w-1.5 animate-pulse bg-primary ml-1" />
            )}
          </div>

          {!isUser && content && !isStreaming && (
            <div className="flex justify-end pt-1 mt-1 border-t border-border/40">
              <button
                type="button"
                onClick={handleCopy}
                className="inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground touch-target h-7 px-2 rounded hover:bg-muted/60 transition-colors"
                aria-label="Copy response"
              >
                {copied ? <Check className="h-3 w-3 text-success" /> : <Copy className="h-3 w-3" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          )}
        </div>

        {/* Citations / Sources */}
        {!isUser && sources && sources.length > 0 && (
          <div className="flex flex-wrap items-center gap-1.5 pt-1 pl-1 text-xs text-muted-foreground">
            <span className="font-medium">Sources:</span>
            {sources.map((src, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 rounded bg-muted/80 px-2 py-0.5 text-[11px] border border-border/50"
              >
                <ExternalLink className="h-2.5 w-2.5 opacity-60" />
                {src}
              </span>
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-9 w-9 shrink-0 select-none items-center justify-center rounded-full bg-secondary text-secondary-foreground border border-border">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
};
