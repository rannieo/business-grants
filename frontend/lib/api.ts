export type GrantResult = {
  id: string
  name: string
  fit: 'high' | 'medium' | 'low'
  reason: string
  cited: Record<string, unknown>
  caveats: string
}

export type ChatResponse =
  | { type: 'question'; question: string; options?: string[] }
  | { type: 'recommendation'; grants: GrantResult[]; tradeoffs: string }

const API = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'

export async function sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const res = await fetch(`${API}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  })
  if (!res.ok) {
    let detail = `API error ${res.status}`
    try {
      const payload = await res.json()
      if (payload?.detail && typeof payload.detail === 'string') {
        detail = payload.detail
      }
    } catch {
      // keep default detail if response isn't JSON
    }
    throw new Error(detail)
  }
  return res.json()
}

export async function clearSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API}/api/session/${sessionId}`, { method: 'DELETE' })
  if (!res.ok) {
    throw new Error(`Failed to clear session (${res.status})`)
  }
}
