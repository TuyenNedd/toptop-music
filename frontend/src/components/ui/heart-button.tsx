"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api-client";

interface HeartButtonProps {
  soundId: number;
  initialFavorited?: boolean;
}

export function HeartButton({
  soundId,
  initialFavorited = false,
}: HeartButtonProps) {
  const [favorited, setFavorited] = useState(initialFavorited);
  const [loading, setLoading] = useState(false);

  async function toggle() {
    setLoading(true);
    const prev = favorited;
    setFavorited(!prev); // Optimistic

    try {
      if (prev) {
        await fetch(`/api/sounds/${soundId}/favorite`, {
          method: "DELETE",
          credentials: "include",
        });
      } else {
        await apiPost(`/api/sounds/${soundId}/favorite`, {});
      }
    } catch {
      setFavorited(prev); // Revert on error
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={toggle}
      disabled={loading}
      className={`text-xl transition-transform active:scale-125 ${
        favorited ? "text-secondary" : "text-text-tertiary"
      }`}
      aria-label={favorited ? "Remove from favorites" : "Add to favorites"}
    >
      {favorited ? "❤️" : "🤍"}
    </button>
  );
}
