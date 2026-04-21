'use client'

import { useRef, useState } from 'react'
import { Textarea } from '@/components/ui/textarea'

type Props = {
  onSend: (text: string) => void
  disabled: boolean
}

export default function MessageInput({ onSend, disabled }: Props) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  function handleSubmit() {
    const text = value.trim()
    if (!text || disabled) return
    onSend(text)
    setValue('')
    textareaRef.current?.focus()
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div
      className="px-4 py-3 flex items-end gap-3"
      style={{
        background: 'rgba(251, 248, 252, 0.85)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder="Describe your business — industry, size, and what you're trying to achieve…"
        rows={2}
        className="flex-1 resize-none border-0 bg-[#e9e7eb] text-[#1b1b1e] placeholder:text-[#44474e]/60 text-sm rounded-xl focus-visible:ring-2 focus-visible:ring-[#041635] focus-visible:ring-offset-0 py-3 px-4"
      />
      <button
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        className="shrink-0 h-10 w-10 flex items-center justify-center rounded-xl text-white disabled:opacity-40 transition-opacity"
        style={{
          background: 'linear-gradient(135deg, #041635 0%, #1b2b4b 100%)',
        }}
        aria-label="Send"
      >
        {disabled ? (
          <span className="material-symbols-rounded text-lg animate-spin">progress_activity</span>
        ) : (
          <span className="material-symbols-rounded text-lg">send</span>
        )}
      </button>
    </div>
  )
}
