"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { apiGet } from "@/lib/api-client";

interface PlaylistItem {
  id: number;
  name: string;
  sound_count: number;
}

export default function PlaylistsPage() {
  const [playlists, setPlaylists] = useState<PlaylistItem[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    apiGet<PlaylistItem[]>("/api/playlists").then((res) => {
      setPlaylists((res.data as PlaylistItem[]) ?? []);
      setLoaded(true);
    });
  }, []);

  if (!loaded)
    return (
      <div className="text-text-secondary text-center py-12">Loading...</div>
    );

  return (
    <main className="max-w-2xl mx-auto px-4 py-6 lg:ml-64">
      <h1 className="text-2xl font-bold text-text mb-6">Playlists</h1>
      {playlists.length === 0 ? (
        <div className="text-center py-12 text-text-secondary">
          <p className="text-lg">No playlists yet</p>
          <p className="text-sm mt-2">Create one to organize your sounds.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {playlists.map((p) => (
            <Link
              key={p.id}
              href={`/library/playlists/${p.id}`}
              className="block p-4 bg-surface rounded-lg hover:bg-surface-hover transition-colors"
            >
              <p className="text-text font-medium">{p.name}</p>
              <p className="text-text-secondary text-sm">
                {p.sound_count} sounds
              </p>
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
