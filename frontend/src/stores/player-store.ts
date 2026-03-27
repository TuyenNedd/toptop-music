/**
 * Zustand player store — manages playback state across the app.
 */

interface Sound {
  id: number;
  tiktok_sound_id: string;
  title: string;
  artist: string;
  cover_url: string | null;
  duration: number;
}

interface PlayerState {
  currentTrack: Sound | null;
  queue: Sound[];
  isPlaying: boolean;
  volume: number;
  progress: number;
  duration: number;

  play: (track: Sound, queue?: Sound[]) => void;
  pause: () => void;
  resume: () => void;
  skipNext: () => void;
  skipPrevious: () => void;
  setVolume: (v: number) => void;
  setProgress: (p: number) => void;
  setDuration: (d: number) => void;
  removeFromQueue: (id: number) => void;
}

// Simple store without zustand dependency for now — will add zustand in install step
let state: PlayerState;

export function createPlayerStore(): PlayerState {
  const listeners = new Set<() => void>();

  state = {
    currentTrack: null,
    queue: [],
    isPlaying: false,
    volume: 1,
    progress: 0,
    duration: 0,

    play(track, queue = []) {
      state.currentTrack = track;
      state.queue = queue;
      state.isPlaying = true;
      state.progress = 0;
    },
    pause() {
      state.isPlaying = false;
    },
    resume() {
      state.isPlaying = true;
    },
    skipNext() {
      if (state.queue.length > 0) {
        const [next, ...rest] = state.queue;
        state.currentTrack = next;
        state.queue = rest;
        state.progress = 0;
      } else {
        state.isPlaying = false;
      }
    },
    skipPrevious() {
      state.progress = 0;
    },
    setVolume(v) {
      state.volume = v;
    },
    setProgress(p) {
      state.progress = p;
    },
    setDuration(d) {
      state.duration = d;
    },
    removeFromQueue(id) {
      state.queue = state.queue.filter((s) => s.id !== id);
    },
  };

  return state;
}

export { type PlayerState, type Sound as PlayerSound };
