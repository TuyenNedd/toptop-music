/**
 * Playback resilience — retry logic, fallback, skip behavior.
 */

export interface RetryResult {
  success: boolean;
  newUrl?: string;
  error?: string;
}

/**
 * Retry audio playback with exponential backoff.
 * Tries up to maxRetries times, requesting a new stream URL each time.
 */
export async function retryPlayback(
  soundId: number,
  maxRetries: number = 3,
): Promise<RetryResult> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const res = await fetch(`/api/sounds/stream-url/${soundId}`, {
        credentials: "include",
      });
      if (res.ok) {
        const data = await res.json();
        const url = data?.data?.url;
        if (url) {
          return { success: true, newUrl: url };
        }
      }
    } catch {
      // Network error — continue retry
    }

    // Exponential backoff
    if (attempt < maxRetries - 1) {
      await new Promise((r) => setTimeout(r, 2 ** (attempt + 1) * 1000));
    }
  }

  return { success: false, error: "All retry attempts failed" };
}

/**
 * Check if a sound is available in cached-only mode.
 */
export function isCachedSound(sound: { cached: boolean }): boolean {
  return sound.cached;
}
