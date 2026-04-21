'use client'

import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
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

  const mutation = useMutation({
    mutationFn: ({ id, text }: { id: string; text: string }) => sendMessage(id, text),
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: 'assistant', data }])
    },
    onError: (err) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          data: {
            type: 'question',
            question: `Something went wrong: ${err instanceof Error ? err.message : 'Unknown error'}. Please try again.`,
          },
        },
      ])
    },
  })

  const handleSend = useCallback(
    (text: string) => {
      setMessages((prev) => [...prev, { role: 'user', text }])
      mutation.mutate({ id: sessionId, text })
    },
    [sessionId, mutation],
  )

  const handleNew = useCallback(async () => {
    await clearSession(sessionId)
    const newId = crypto.randomUUID()
    setSessionId(newId)
    setMessages([WELCOME])
  }, [sessionId])

  return (
    <div className="flex h-screen overflow-hidden bg-[#fbf8fc]">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <ChatArea
          messages={messages}
          isPending={mutation.isPending}
          onSend={handleSend}
          onNew={handleNew}
        />
      </main>
    </div>
  )
}
