"use client";

interface TrendBadgeProps {
  rank: number;
  usageCount?: number;
}

export function TrendBadge({ rank, usageCount }: TrendBadgeProps) {
  const isTop3 = rank <= 3;

  return (
    <div className="flex items-center gap-1">
      <span
        className={`text-xs font-bold px-2 py-0.5 rounded-full ${
          isTop3
            ? "bg-primary text-bg"
            : "bg-surface-active text-text-secondary"
        }`}
        aria-label={`Trending rank ${rank}`}
      >
        #{rank}
      </span>
      {usageCount !== undefined && (
        <span className="text-xs text-text-tertiary">
          {usageCount >= 1_000_000
            ? `${(usageCount / 1_000_000).toFixed(1)}M`
            : usageCount >= 1_000
              ? `${(usageCount / 1_000).toFixed(1)}K`
              : usageCount}
        </span>
      )}
    </div>
  );
}
