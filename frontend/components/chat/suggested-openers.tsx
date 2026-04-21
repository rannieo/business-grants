const OPENERS = [
  {
    label: 'Expand overseas',
    text: "We're a Singapore company looking to expand into a new overseas market for the first time.",
  },
  {
    label: 'Build a new product',
    text: 'We want to develop and commercialise a new product or solution.',
  },
  {
    label: 'Automate operations',
    text: 'We want to automate our manual processes to improve efficiency and productivity.',
  },
  {
    label: 'Hire and reskill staff',
    text: "We're looking to hire new staff and reskill them into redesigned roles.",
  },
  {
    label: 'Build digital capabilities',
    text: 'We want to build a digital team and execute a digital transformation initiative.',
  },
  {
    label: 'Get certified',
    text: 'We need to adopt industry standards or certifications to improve our market readiness.',
  },
]

export default function SuggestedOpeners({ onSelect }: { onSelect: (text: string) => void }) {
  return (
    <div className="px-6 pb-6">
      <p className="text-xs text-[#44474e] mb-3 uppercase tracking-wider font-medium">
        Suggested openers
      </p>
      <div className="flex flex-wrap gap-2">
        {OPENERS.map((o) => (
          <button
            key={o.label}
            onClick={() => onSelect(o.text)}
            className="px-3 py-1.5 rounded-full text-sm border text-[#041635] bg-[#ffffff] hover:bg-[#f5f3f6] transition-colors"
            style={{ borderColor: 'rgba(197, 198, 207, 0.6)' }}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  )
}
