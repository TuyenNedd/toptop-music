"use client";

import { useEffect, useState } from "react";

type ToastVariant = "info" | "success" | "warning" | "error";

interface ToastProps {
  message: string;
  variant?: ToastVariant;
  duration?: number;
  onDismiss?: () => void;
}

const variantStyles: Record<ToastVariant, string> = {
  info: "bg-surface border-primary text-text",
  success: "bg-surface border-success text-text",
  warning: "bg-surface border-warning text-text",
  error: "bg-surface border-error text-text",
};

export function Toast({
  message,
  variant = "info",
  duration = 3000,
  onDismiss,
}: ToastProps) {
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false);
      onDismiss?.();
    }, duration);
    return () => clearTimeout(timer);
  }, [duration, onDismiss]);

  if (!visible) return null;

  return (
    <div
      className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 px-4 py-3 rounded-lg border-l-4 shadow-lg ${variantStyles[variant]}`}
      role="alert"
      aria-live="polite"
    >
      <p className="text-sm">{message}</p>
    </div>
  );
}
