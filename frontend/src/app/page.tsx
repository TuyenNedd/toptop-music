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

interface TrendingResponse {
  data: Sound[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    has_next: boolean;
  };
  error: null;
}

export default async function HomePage() {
  // SSR: fetch trending on server
  let sounds: Sound[] = [];
  try {
    const res = await fetch(
      `${process.env.BACKEND_URL ?? "http://localhost:8000"}/api/sounds/trending?page=1&page_size=20`,
      { next: { revalidate: 300 } }, // Revalidate every 5 min
    );
    if (res.ok) {
      const data: TrendingResponse = await res.json();
      sounds = data.data ?? [];
    }
  } catch {
    // Backend not available — show empty state
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-6 lg:ml-64">
      <h1 className="text-2xl font-bold text-text mb-6">Trending Sounds</h1>
      <SoundList sounds={sounds} />
    </main>
  );
}
