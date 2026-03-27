"use client";

import { SoundCard } from "./sound-card";

interface Sound {
  id: number;
  tiktok_sound_id: string;
  title: string;
  artist: string;
  cover_url: string | null;
  duration: number;
  usage_count: number;
  trend_rank: number | null;
  cached: boolean;
}

interface SoundListProps {
  sounds: Sound[];
  playingSoundId?: number;
  onPlay?: (sound: Sound) => void;
}

export function SoundList({ sounds, playingSoundId, onPlay }: SoundListProps) {
  if (sounds.length === 0) {
    return (
      <div className="text-center py-12 text-text-secondary">
        <p className="text-lg">No sounds found</p>
        <p className="text-sm mt-2">Trending updates every 30-60 min.</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {sounds.map((sound) => (
        <SoundCard
          key={sound.id}
          id={sound.id}
          title={sound.title}
          artist={sound.artist}
          coverUrl={sound.cover_url}
          duration={sound.duration}
          usageCount={sound.usage_count}
          trendRank={sound.trend_rank}
          isPlaying={sound.id === playingSoundId}
          onPlay={() => onPlay?.(sound)}
        />
      ))}
    </div>
  );
}
