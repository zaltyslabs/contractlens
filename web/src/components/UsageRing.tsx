interface Props {
  used: number;
  limit: number;
}

export default function UsageRing({ used, limit }: Props) {
  const pct = Math.min((used / limit) * 100, 100);
  const circumference = 2 * Math.PI * 28;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <div className="bg-surface border border-white/[0.07] rounded-xl p-5">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-4">
        Monthly Usage
      </h3>
      <div className="flex items-center gap-5">
        <svg width="72" height="72" viewBox="0 0 72 72" className="shrink-0">
          <circle
            cx="36" cy="36" r="28"
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth="5"
          />
          <circle
            cx="36" cy="36" r="28"
            fill="none"
            stroke="#6366f1"
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            transform="rotate(-90 36 36)"
            className="transition-[stroke-dashoffset] duration-700"
          />
        </svg>
        <div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {used}
            <span className="text-sm font-normal text-gray-500"> / {limit}</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">scans used</div>
          <div className="text-[11px] text-gray-600 mt-1">resets monthly</div>
        </div>
      </div>
    </div>
  );
}
