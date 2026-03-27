"use client";

interface PlayerBarProps {
  track: {
    title: string;
    artist: string;
    coverUrl: string | null;
  } | null;
  isPlaying: boolean;
  progress: number;
  duration: number;
  onPlayPause: () => void;
  onExpand?: () => void;
}

export function PlayerBar({
  track,
  isPlaying,
  progress,
  duration,
  onPlayPause,
  onExpand,
}: PlayerBarProps) {
  if (!track) return null;

  const progressPercent = duration > 0 ? (progress / duration) * 100 : 0;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 h-player-mobile md:h-player-desktop bg-surface border-t border-border z-30 flex items-center px-4 gap-3"
      role="region"
      aria-label="Audio player"
    >
      {/* Progress bar */}
      <div className="absolute top-0 left-0 right-0 h-1 bg-surface-active">
        <div
          className="h-full bg-primary transition-all"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Cover art */}
      <button
        onClick={onExpand}
        className="w-10 h-10 rounded bg-surface-active flex-shrink-0 overflow-hidden"
      >
        {track.coverUrl ? (
          <img
            src={track.coverUrl}
            alt=""
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <span className="flex items-center justify-center w-full h-full text-text-tertiary">
            ♪
          </span>
        )}
      </button>

      {/* Track info */}
      <div
        className="flex-1 min-w-0"
        onClick={onExpand}
        role="button"
        tabIndex={0}
      >
        <p className="text-text text-sm font-medium truncate">{track.title}</p>
        <p className="text-text-secondary text-xs truncate">{track.artist}</p>
      </div>

      {/* Play/Pause */}
      <button
        onClick={onPlayPause}
        className="w-11 h-11 flex items-center justify-center rounded-full bg-primary text-bg"
        aria-label={isPlaying ? "Pause" : "Play"}
      >
        {isPlaying ? "⏸" : "▶"}
      </button>
    </div>
  );
}
