"use client";

interface ProgressBarProps {
  progress: number;
  duration: number;
  onSeek: (time: number) => void;
}

export function ProgressBar({ progress, duration, onSeek }: ProgressBarProps) {
  return (
    <input
      type="range"
      min={0}
      max={duration}
      value={progress}
      onChange={(e) => onSeek(Number(e.target.value))}
      className="w-full accent-primary h-1"
      aria-label="Seek position"
      aria-valuemin={0}
      aria-valuemax={duration}
      aria-valuenow={progress}
    />
  );
}
