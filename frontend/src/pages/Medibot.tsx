import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Bot,
  Trash2,
  RefreshCw,
  Sparkles,
  AlertTriangle,
  Loader2,
  ArrowDown,
} from 'lucide-react';
import { api, ChatMessage } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { ChatBubble } from '@/components/ui/ChatBubble';
import { cn } from '@/lib/utils';

interface DisplayMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sources?: string[];
  isStreaming?: boolean;
}

const INITIAL_MESSAGES: DisplayMessage[] = [
  {
    id: 'welcome-1',
    role: 'assistant',
    content: `Hello! I am **Medibot**, your AI health education assistant.

Describe any symptom or medical inquiry (for example: **back pain**, **fever**, **acidity**, or **skin rash**). I will summarize:
1. **What it may be** — common possible causes
2. **What you can do now** — home care & posture/diet
3. **Typical medicines** — OTC classes & safety warnings
4. **Which doctor to see** — specialists & urgency flags

*Educational information only — not a personal diagnosis or prescription.*`,
  },
];

const SUGGESTION_CHIPS = [
  'Lower back pain when bending',
  'Persistent mild fever & chills',
  'Severe acidity & heartburn',
  'Dry cough & throat irritation',
  'Migraine with light sensitivity',
];

export const Medibot: React.FC = () => {
  const [messages, setMessages] = useState<DisplayMessage[]>(INITIAL_MESSAGES);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [lastError, setLastError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    scrollToBottom('smooth');
  }, [messages]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputValue.trim();
    if (!textToSend || isLoading) return;

    setLastError(null);
    const userMsgId = `user-${Date.now()}`;
    const assistantMsgId = `asst-${Date.now()}`;

    const newMessages: DisplayMessage[] = [
      ...messages,
      { id: userMsgId, role: 'user', content: textToSend },
      { id: assistantMsgId, role: 'assistant', content: '', isStreaming: true, sources: [] },
    ];

    setMessages(newMessages);
    setInputValue('');
    setIsLoading(true);

    let accumulatedContent = '';
    const abortController = new AbortController();

    try {
      await api.streamChat(
        textToSend,
        (token) => {
          accumulatedContent += token;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMsgId
                ? { ...msg, content: accumulatedContent, isStreaming: true }
                : msg
            )
          );
        },
        (meta) => {
          if (meta.sources) {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId ? { ...msg, sources: meta.sources } : msg
              )
            );
          }
        },
        (err) => {
          console.error('SSE Stream error, falling back to JSON:', err);
          fallbackToJson(textToSend, assistantMsgId);
        },
        abortController.signal
      );

      // Finalize streaming
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId ? { ...msg, isStreaming: false } : msg
        )
      );
    } catch (err: any) {
      console.warn('Stream failed, attempting standard JSON API:', err);
      await fallbackToJson(textToSend, assistantMsgId);
    } finally {
      setIsLoading(false);
    }
  };

  const fallbackToJson = async (query: string, msgId: string) => {
    try {
      const chatHistory: ChatMessage[] = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const res = await api.sendChat(query, chatHistory);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === msgId
            ? {
                ...msg,
                content: res.content,
                sources: res.sources,
                isStreaming: false,
              }
            : msg
        )
      );
    } catch (err: any) {
      setLastError(err.message || 'Failed to communicate with Medibot.');
      setMessages((prev) => prev.filter((msg) => msg.id !== msgId));
    }
  };

  const handleClearChat = () => {
    setMessages(INITIAL_MESSAGES);
    setLastError(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="mx-auto flex h-[calc(100dvh-4rem-5rem)] md:h-[calc(100dvh-4rem-3.5rem)] max-w-4xl flex-col px-3 sm:px-6 py-3 animate-fadeIn">
      {/* Top Header Strip */}
      <div className="flex items-center justify-between border-b border-border pb-3 shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base sm:text-lg font-bold leading-none text-foreground">
              Medibot AI Assistant
            </h1>
            <span className="text-[11px] text-muted-foreground">
              Powered by Groq LLM + FAISS Knowledge Base
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearChat}
            className="text-xs h-8 text-muted-foreground hover:text-foreground gap-1"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Clear Chat</span>
          </Button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto py-4 space-y-2 pr-1">
        {messages.map((msg) => (
          <ChatBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            sources={msg.sources}
            isStreaming={msg.isStreaming}
          />
        ))}

        {/* Loading Indicator */}
        {isLoading && messages[messages.length - 1]?.content === '' && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground py-2 pl-12 animate-pulse">
            <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
            <span>Medibot is synthesizing clinical guidance...</span>
          </div>
        )}

        {/* Error notification */}
        {lastError && (
          <div className="flex items-center justify-between p-3 rounded-xl border border-destructive/30 bg-destructive/10 text-xs text-destructive">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{lastError}</span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={() => handleSend(messages[messages.length - 1]?.content)}
              className="h-7 text-xs"
            >
              <RefreshCw className="h-3 w-3 mr-1" /> Retry
            </Button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Chips */}
      {messages.length <= 2 && (
        <div className="py-2 shrink-0">
          <span className="text-[11px] text-muted-foreground block mb-1.5 font-medium">
            Try asking about:
          </span>
          <div className="flex gap-1.5 overflow-x-auto pb-1 no-scrollbar">
            {SUGGESTION_CHIPS.map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => handleSend(chip)}
                className="touch-target shrink-0 inline-flex items-center rounded-full border border-border bg-card px-3 py-1.5 text-xs text-muted-foreground hover:bg-primary/10 hover:border-primary/30 hover:text-foreground transition-colors"
              >
                <Sparkles className="h-3 w-3 mr-1 text-primary" />
                {chip}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Sticky Bottom Input Area */}
      <div className="shrink-0 pt-2 border-t border-border">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-end gap-2"
        >
          <textarea
            ref={inputRef}
            rows={1}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe symptoms or ask health question..."
            disabled={isLoading}
            className="flex-1 max-h-32 min-h-[48px] rounded-xl border border-input bg-background p-3 pr-10 text-base text-foreground shadow-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring resize-none"
            style={{ fontSize: '16px' }}
          />

          <Button
            type="submit"
            size="icon"
            disabled={!inputValue.trim() || isLoading}
            isLoading={isLoading}
            className="h-12 w-12 rounded-xl shrink-0"
            aria-label="Send message"
          >
            <Send className="h-5 w-5" />
          </Button>
        </form>

        {/* Disclaimer Text */}
        <p className="mt-1.5 text-[11px] text-center text-muted-foreground">
          Educational only — not a substitute for clinical advice. Consult a doctor before taking medication.
        </p>
      </div>
    </div>
  );
};
