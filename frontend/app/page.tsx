'use client'

import { useState, useCallback, useRef } from 'react'
import Sidebar from '@/components/chat/sidebar'
import ChatArea from '@/components/chat/chat-area'
import { type Message } from '@/components/chat/message-bubble'
import { sendMessage, clearSession } from '@/lib/api'

const WELCOME: Message = {
  role: 'assistant',
  data: {
    type: 'question',
    question:
      "Hello! I'm your Grant Advisor. Tell me about your business — your industry, team size, and what you're looking to achieve — and I'll match you with the right Singapore grants.",
  },
}

export default function Page() {
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID())
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [isPending, setIsPending] = useState(false)
  const [retryMessage, setRetryMessage] = useState<string | null>(null)
  const requestSeq = useRef(0)

  const runSend = useCallback(
    async (text: string, options?: { isRetry?: boolean }) => {
      if (isPending) return

      const requestId = ++requestSeq.current
      setIsPending(true)
      setRetryMessage(null)

      if (!options?.isRetry) {
        setMessages((prev) => [...prev, { role: 'user', text }])
      }

      try {
        const data = await sendMessage(sessionId, text)
        if (requestId !== requestSeq.current) return
        setMessages((prev) => [...prev, { role: 'assistant', data }])
      } catch (err) {
        if (requestId !== requestSeq.current) return
        const detail = err instanceof Error ? err.message : 'Unknown error'
        setRetryMessage(text)
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            data: {
              type: 'question',
              question: `I couldn't process that just now. ${detail}`,
            },
          },
        ])
      } finally {
        if (requestId === requestSeq.current) {
          setIsPending(false)
        }
      }
    },
    [isPending, sessionId],
  )

  const handleSend = useCallback(
    (text: string) => {
      void runSend(text)
    },
    [runSend],
  )

  const handleNew = useCallback(async () => {
    if (isPending) return
    requestSeq.current += 1
    try {
      await clearSession(sessionId)
    } catch {
      // Preserve UX even if session clear fails server-side.
    }
    const newId = crypto.randomUUID()
    setSessionId(newId)
    setRetryMessage(null)
    setIsPending(false)
    setMessages([WELCOME])
  }, [isPending, sessionId])

  const handleRetry = useCallback(() => {
    if (!retryMessage || isPending) return
    void runSend(retryMessage, { isRetry: true })
  }, [retryMessage, isPending, runSend])

  return (
    <div className="flex h-screen overflow-hidden bg-[#fbf8fc]">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <ChatArea
          messages={messages}
          isPending={isPending}
          retryMessage={retryMessage}
          onSend={handleSend}
          onRetry={handleRetry}
          onNew={handleNew}
        />
      </main>
    </div>
  )
}
