import type { ChatResponse } from '@/lib/api'
import GrantCard from './grant-card'

type UserMessage = { role: 'user'; text: string }
type AssistantMessage = { role: 'assistant'; data: ChatResponse }
export type Message = UserMessage | AssistantMessage

export default function MessageBubble({ message }: { message: Message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end mb-3">
        <div
          className="max-w-[75%] px-4 py-3 rounded-2xl rounded-tr-sm text-sm text-white leading-relaxed"
          style={{ background: 'linear-gradient(135deg, #041635 0%, #1b2b4b 100%)' }}
        >
          {message.text}
        </div>
      </div>
    )
  }

  const { data } = message

  if (data.type === 'question') {
    return (
      <div className="flex justify-start mb-3">
        <div className="flex items-start gap-2.5 max-w-[80%]">
          <Avatar />
          <div className="bg-[#f5f3f6] px-4 py-3 rounded-2xl rounded-tl-sm text-sm text-[#1b1b1e] leading-relaxed">
            {data.question}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start mb-3">
      <div className="flex items-start gap-2.5 w-full max-w-[85%]">
        <Avatar />
        <div className="flex-1">
          {data.grants.map((g) => (
            <GrantCard key={g.id} grant={g} />
          ))}
          {data.tradeoffs && (
            <p className="mt-3 text-xs text-[#44474e] italic leading-relaxed px-1">
              {data.tradeoffs}
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function Avatar() {
  return (
    <div
      className="shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-[#89f5e7] mt-0.5"
      style={{ background: '#041635' }}
    >
      G
    </div>
  )
}
