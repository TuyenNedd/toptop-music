"use client";

import Link from "next/link";
import { useCallback, useState } from "react";

import { apiGet } from "@/lib/api-client";
import { SearchBar } from "@/components/ui/search-bar";
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

export default function SearchPage() {
  const [sounds, setSounds] = useState<Sound[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = useCallback(async (query: string) => {
    if (!query) {
      setSounds([]);
      setSearched(false);
      return;
    }
    const res = await apiGet<{ data: Sound[] }>(
      `/api/sounds/search?q=${encodeURIComponent(query)}`,
    );
    setSounds((res.data as unknown as { data: Sound[] })?.data ?? []);
    setSearched(true);
  }, []);

  return (
    <main className="max-w-2xl mx-auto lg:ml-64">
      <SearchBar onSearch={handleSearch} />
      <div className="px-4 py-4">
        {searched && sounds.length === 0 ? (
          <div className="text-center py-12 text-text-secondary">
            <p className="text-lg">No sounds found</p>
            <p className="text-sm mt-2">Trending updates every 30-60 min.</p>
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
      </div>
    </main>
  );
}
