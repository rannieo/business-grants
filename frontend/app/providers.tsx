'use client'

import { isServer, QueryClient, QueryClientProvider } from '@tanstack/react-query'

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { staleTime: 60_000 } } })
}

let browserQC: QueryClient | undefined

function getQueryClient() {
  if (isServer) return makeQueryClient()
  return (browserQC ??= makeQueryClient())
}

export default function Providers({ children }: { children: React.ReactNode }) {
  return <QueryClientProvider client={getQueryClient()}>{children}</QueryClientProvider>
}
