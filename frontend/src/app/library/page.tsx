import Link from "next/link";

export default function LibraryPage() {
  return (
    <main className="max-w-2xl mx-auto px-4 py-6 lg:ml-64">
      <h1 className="text-2xl font-bold text-text mb-6">Library</h1>
      <div className="space-y-4">
        <Link
          href="/library/favorites"
          className="block p-4 bg-surface rounded-lg hover:bg-surface-hover transition-colors"
        >
          <span className="text-lg">❤️ Favorites</span>
        </Link>
        <Link
          href="/library/playlists"
          className="block p-4 bg-surface rounded-lg hover:bg-surface-hover transition-colors"
        >
          <span className="text-lg">📋 Playlists</span>
        </Link>
      </div>
    </main>
  );
}
