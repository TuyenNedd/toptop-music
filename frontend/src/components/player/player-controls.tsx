"use client";

interface PlayerControlsProps {
  isPlaying: boolean;
  onPlayPause: () => void;
  onSkipNext: () => void;
  onSkipPrevious: () => void;
}

export function PlayerControls({
  isPlaying,
  onPlayPause,
  onSkipNext,
  onSkipPrevious,
}: PlayerControlsProps) {
  return (
    <div
      className="flex items-center gap-4"
      role="group"
      aria-label="Playback controls"
    >
      <button
        onClick={onSkipPrevious}
        className="w-11 h-11 flex items-center justify-center text-text hover:text-primary transition-colors"
        aria-label="Previous track"
      >
        ⏮
      </button>
      <button
        onClick={onPlayPause}
        className="w-14 h-14 flex items-center justify-center rounded-full bg-primary text-bg text-xl"
        aria-label={isPlaying ? "Pause" : "Play"}
      >
        {isPlaying ? "⏸" : "▶"}
      </button>
      <button
        onClick={onSkipNext}
        className="w-11 h-11 flex items-center justify-center text-text hover:text-primary transition-colors"
        aria-label="Next track"
      >
        ⏭
      </button>
    </div>
  );
}
