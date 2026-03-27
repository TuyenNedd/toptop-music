"use client";

interface QueueSound {
  id: number;
  title: string;
  artist: string;
}

interface QueueDrawerProps {
  queue: QueueSound[];
  currentTrackId: number | null;
  onRemove: (id: number) => void;
  onClose: () => void;
}

export function QueueDrawer({
  queue,
  currentTrackId,
  onRemove,
  onClose,
}: QueueDrawerProps) {
  return (
    <div
      className="fixed right-0 top-0 bottom-0 w-80 bg-surface border-l border-border z-40 flex flex-col"
      role="dialog"
      aria-label="Play queue"
    >
      <div className="flex items-center justify-between p-4 border-b border-border">
        <h3 className="text-text font-semibold">Queue</h3>
        <button
          onClick={onClose}
          className="text-text-secondary"
          aria-label="Close queue"
        >
          ✕
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {queue.length === 0 ? (
          <p className="text-text-secondary text-center py-8">Queue is empty</p>
        ) : (
          queue.map((sound) => (
            <div
              key={sound.id}
              className={`flex items-center gap-3 px-4 py-3 ${sound.id === currentTrackId ? "text-primary" : "text-text"}`}
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{sound.title}</p>
                <p className="text-xs text-text-secondary truncate">
                  {sound.artist}
                </p>
              </div>
              <button
                onClick={() => onRemove(sound.id)}
                className="text-text-tertiary hover:text-error text-sm"
                aria-label={`Remove ${sound.title}`}
              >
                ✕
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
