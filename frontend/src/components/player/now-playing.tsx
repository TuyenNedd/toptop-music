"use client";

interface NowPlayingProps {
  track: { title: string; artist: string; coverUrl: string | null };
  isPlaying: boolean;
  progress: number;
  duration: number;
  volume: number;
  onPlayPause: () => void;
  onSkipNext: () => void;
  onSkipPrevious: () => void;
  onSeek: (time: number) => void;
  onVolumeChange: (v: number) => void;
  onClose: () => void;
}

function formatTime(s: number): string {
  const m = Math.floor(s / 60);
  const sec = Math.floor(s % 60);
  return `${m}:${sec.toString().padStart(2, "0")}`;
}

export function NowPlaying({
  track,
  isPlaying,
  progress,
  duration,
  volume,
  onPlayPause,
  onSkipNext,
  onSkipPrevious,
  onSeek,
  onVolumeChange,
  onClose,
}: NowPlayingProps) {
  return (
    <div
      className="fixed inset-0 bg-bg z-50 flex flex-col items-center justify-center px-6"
      role="dialog"
      aria-label="Now Playing"
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-text-secondary text-2xl"
        aria-label="Close"
      >
        ✕
      </button>

      {/* Cover art */}
      <div className="w-72 h-72 md:w-80 md:h-80 rounded-2xl bg-surface-active overflow-hidden mb-8">
        {track.coverUrl ? (
          <img
            src={track.coverUrl}
            alt=""
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-6xl text-text-tertiary">
            ♪
          </div>
        )}
      </div>

      <h2 className="text-text text-xl font-bold text-center">{track.title}</h2>
      <p className="text-text-secondary text-center mb-6">{track.artist}</p>

      {/* Progress */}
      <div className="w-full max-w-sm mb-4">
        <input
          type="range"
          min={0}
          max={duration}
          value={progress}
          onChange={(e) => onSeek(Number(e.target.value))}
          className="w-full accent-primary"
          aria-label="Seek"
        />
        <div className="flex justify-between text-text-tertiary text-xs">
          <span>{formatTime(progress)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-8">
        <button
          onClick={onSkipPrevious}
          className="text-text text-2xl w-11 h-11 flex items-center justify-center"
          aria-label="Previous"
        >
          ⏮
        </button>
        <button
          onClick={onPlayPause}
          className="w-16 h-16 rounded-full bg-primary text-bg text-3xl flex items-center justify-center"
          aria-label={isPlaying ? "Pause" : "Play"}
        >
          {isPlaying ? "⏸" : "▶"}
        </button>
        <button
          onClick={onSkipNext}
          className="text-text text-2xl w-11 h-11 flex items-center justify-center"
          aria-label="Next"
        >
          ⏭
        </button>
      </div>

      {/* Volume */}
      <div className="mt-6 w-full max-w-xs">
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={volume}
          onChange={(e) => onVolumeChange(Number(e.target.value))}
          className="w-full accent-primary"
          aria-label="Volume"
        />
      </div>
    </div>
  );
}
