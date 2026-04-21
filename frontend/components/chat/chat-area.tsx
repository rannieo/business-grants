'use client'

import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import MessageBubble, { type Message } from './message-bubble'
import MessageInput from './message-input'
import SuggestedOpeners from './suggested-openers'

type Props = {
  messages: Message[]
  isPending: boolean
  retryMessage: string | null
  onSend: (text: string) => void
  onRetry: () => void
  onNew: () => void
}

export default function ChatArea({ messages, isPending, retryMessage, onSend, onRetry, onNew }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const showOpeners = messages.length === 1 && !isPending

  return (
    <div className="flex flex-col flex-1 h-screen overflow-hidden">
      {/* Header */}
      <header
        className="flex items-center justify-between px-6 py-4 shrink-0"
        style={{
          background: 'rgba(251, 248, 252, 0.85)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid rgba(197, 198, 207, 0.2)',
        }}
      >
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-[#041635] text-xl">forum</span>
          <span
            className="text-[#1b1b1e] font-semibold text-base"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Grant Advisor
          </span>
        </div>
        <button
          onClick={onNew}
          disabled={isPending}
          aria-label="Start a new conversation"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-[#041635] bg-[#f5f3f6] hover:bg-[#e9e7eb] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <span className="material-symbols-rounded text-base">add</span>
          New
        </button>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1 overflow-hidden">
        <div className="px-6 pt-6" role="log" aria-live="polite" aria-relevant="additions text">
          {messages.map((msg, i) => (
            <MessageBubble
              key={i}
              message={msg}
              onSend={onSend}
              isLast={i === messages.length - 1}
              disableActions={isPending}
            />
          ))}
          {isPending && <TypingIndicator />}
          <div ref={bottomRef} />
        </div>

        {/* Suggested openers shown only before the first user message */}
        {showOpeners && <SuggestedOpeners onSelect={onSend} />}
      </ScrollArea>

      {/* Input */}
      <div className="shrink-0 border-t border-[rgba(197,198,207,0.15)]">
        {retryMessage && !isPending && (
          <div
            className="px-4 py-2 text-xs text-[#44474e] bg-[#f5f3f6] border-b border-[rgba(197,198,207,0.15)] flex items-center justify-between gap-2"
            role="status"
            aria-live="polite"
          >
            <span>Last request failed. Retry the same message.</span>
            <button
              onClick={onRetry}
              className="px-2.5 py-1 rounded-md text-[#041635] bg-[#ffffff] border border-[rgba(197,198,207,0.6)] hover:bg-[#e9e7eb] transition-colors"
              aria-label="Retry last message"
            >
              Retry
            </button>
          </div>
        )}
        <MessageInput onSend={onSend} disabled={isPending} />
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start mb-3 px-0" role="status" aria-live="polite" aria-label="Assistant is typing">
      <div className="flex items-center gap-2.5">
        <div
          className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-[#89f5e7]"
          style={{ background: '#041635' }}
        >
          G
        </div>
        <div className="bg-[#f5f3f6] px-4 py-3 rounded-2xl rounded-tl-sm flex gap-1.5 items-center">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-[#44474e] opacity-40 animate-bounce"
              style={{ animationDelay: `${i * 150}ms` }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
