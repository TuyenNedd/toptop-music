"use client";

import { useEffect, useState } from "react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export function SearchBar({
  onSearch,
  placeholder = "Search sounds...",
}: SearchBarProps) {
  const [query, setQuery] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => {
      if (query.trim()) {
        onSearch(query.trim());
      }
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [query, onSearch]);

  return (
    <div className="sticky top-0 z-10 bg-bg py-2 px-4">
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={placeholder}
          className="w-full px-4 py-2 pl-10 bg-surface border border-border rounded-full text-text focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary">
          🔍
        </span>
        {query && (
          <button
            onClick={() => {
              setQuery("");
              onSearch("");
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}
