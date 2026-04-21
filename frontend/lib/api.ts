export type GrantResult = {
  id: string
  name: string
  fit: 'high' | 'medium' | 'low'
  reason: string
  cited: Record<string, unknown>
  caveats: string
}

export type ChatResponse =
  | { type: 'question'; question: string }
  | { type: 'recommendation'; grants: GrantResult[]; tradeoffs: string }

const API = 'http://localhost:8000'

export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const res = await fetch(`${API}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

export async function clearSession(sessionId: string): Promise<void> {
  await fetch(`${API}/api/session/${sessionId}`, { method: 'DELETE' })
}
