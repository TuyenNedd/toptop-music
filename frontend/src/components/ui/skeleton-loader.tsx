"use client";

interface SkeletonLoaderProps {
  count?: number;
}

export function SkeletonLoader({ count = 5 }: SkeletonLoaderProps) {
  return (
    <div className="space-y-2 animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-3">
          <div className="w-12 h-12 rounded-lg bg-surface-active" />
          <div className="flex-1 space-y-2">
            <div className="h-4 bg-surface-active rounded w-3/4" />
            <div className="h-3 bg-surface-active rounded w-1/2" />
          </div>
          <div className="h-3 bg-surface-active rounded w-8" />
        </div>
      ))}
    </div>
  );
}
