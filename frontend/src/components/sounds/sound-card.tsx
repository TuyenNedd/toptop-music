"use client";

interface SoundCardProps {
  id: number;
  title: string;
  artist: string;
  coverUrl: string | null;
  duration: number;
  usageCount: number;
  trendRank: number | null;
  isPlaying?: boolean;
  onPlay?: () => void;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export function SoundCard({
  title,
  artist,
  coverUrl,
  duration,
  usageCount,
  trendRank,
  isPlaying = false,
  onPlay,
}: SoundCardProps) {
  return (
    <button
      onClick={onPlay}
      className={`w-full flex items-center gap-3 p-3 rounded-lg transition-colors hover:bg-surface-hover ${
        isPlaying ? "border-l-2 border-primary bg-surface" : ""
      }`}
    >
      {/* Cover art */}
      <div className="w-12 h-12 md:w-14 md:h-14 rounded-lg bg-surface-active overflow-hidden flex-shrink-0">
        {coverUrl ? (
          <img
            src={coverUrl}
            alt={title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-text-tertiary">
            ♪
          </div>
        )}
      </div>

      {/* Metadata */}
      <div className="flex-1 min-w-0 text-left">
        <p className="text-text font-medium truncate">{title}</p>
        <p className="text-text-secondary text-sm truncate">{artist}</p>
      </div>

      {/* Duration */}
      <span className="text-text-tertiary text-sm">
        {formatDuration(duration)}
      </span>

      {/* Usage count */}
      <span className="text-text-secondary text-xs hidden md:block">
        {formatCount(usageCount)}
      </span>

      {/* Trend rank badge */}
      {trendRank && (
        <span
          className={`text-xs font-bold px-2 py-1 rounded-full ${
            trendRank <= 3
              ? "bg-primary text-bg"
              : "bg-surface-active text-text-secondary"
          }`}
        >
          #{trendRank}
        </span>
      )}
    </button>
  );
}
