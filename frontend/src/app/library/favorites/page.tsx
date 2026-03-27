"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiGet } from "@/lib/api-client";
import { SoundList } from "@/components/sounds/sound-list";

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

export default function FavoritesPage() {
  const [sounds, setSounds] = useState<Sound[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiGet<{ data: Sound[] }>("/api/sounds/favorites").then((res) => {
      setSounds((res.data as unknown as { data: Sound[] })?.data ?? []);
      setLoaded(true);
    });
  }, []);

  if (!loaded)
    return (
      <div className="text-text-secondary text-center py-12">Loading...</div>
    );

  return (
    <main className="max-w-2xl mx-auto px-4 py-6 lg:ml-64">
      <h1 className="text-2xl font-bold text-text mb-6">Favorites</h1>
      {sounds.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg">No favorites yet</p>
          <p className="text-sm mt-2">Tap ❤️ on any sound to save it here.</p>
          <Link
            href="/"
            className="text-primary hover:underline mt-4 inline-block"
          >
            Browse Trending
          </Link>
        </div>
      ) : (
        <SoundList sounds={sounds} />
      )}
    </main>
  );
}
