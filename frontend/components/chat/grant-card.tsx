import type { GrantResult } from '@/lib/api'

const FIT_CONFIG = {
  high: {
    label: 'HIGH',
    className: 'bg-[#00322d] text-[#89f5e7]',
  },
  medium: {
    label: 'MEDIUM',
    className: 'bg-[#e9e7eb] text-[#44474e]',
  },
  low: {
    label: 'LOW',
    className: 'bg-transparent text-[#44474e] ring-1 ring-[#c5c6cf]',
  },
}

export default function GrantCard({ grant }: { grant: GrantResult }) {
  const fit = FIT_CONFIG[grant.fit]
  const citedEntries = Object.entries(grant.cited)

  return (
    <div
      className="rounded-lg p-5 mb-3 last:mb-0"
      style={{
        background: '#ffffff',
        boxShadow: '0 20px 40px rgba(27, 43, 75, 0.06)',
      }}
    >
      {/* Header: name + fit chip */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3
          className="text-base font-semibold text-[#1b1b1e] leading-snug"
          style={{ fontFamily: 'var(--font-display)' }}
        >
          {grant.name}
        </h3>
        <span
          className={`shrink-0 text-[10px] font-bold tracking-wider px-2 py-1 rounded-full ${fit.className}`}
        >
          {fit.label}
        </span>
      </div>

      {/* Reason */}
      <p className="text-sm text-[#44474e] leading-relaxed mb-4">{grant.reason}</p>

      {/* Cited fields */}
      {citedEntries.length > 0 && (
        <div className="rounded-md bg-[#f5f3f6] px-3 py-2 mb-3">
          <p className="text-[10px] font-semibold text-[#44474e] uppercase tracking-wider mb-1.5">
            Cited
          </p>
          <dl className="space-y-0.5">
            {citedEntries.map(([key, val]) => (
              <div key={key} className="flex gap-2 text-xs">
                <dt className="font-mono text-[#041635] shrink-0">{key}:</dt>
                <dd className="text-[#44474e]">{String(val)}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* Caveats */}
      {grant.caveats && (
        <p className="text-xs text-[#44474e] italic leading-relaxed">{grant.caveats}</p>
      )}
    </div>
  )
}
