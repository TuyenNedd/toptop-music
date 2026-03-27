"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const tabs = [
  { href: "/", label: "Home", icon: "🏠" },
  { href: "/search", label: "Search", icon: "🔍" },
  { href: "/library", label: "Library", icon: "📚" },
];

export function TabBar() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-player-mobile left-0 right-0 bg-surface border-t border-border flex md:hidden z-20">
      {tabs.map((tab) => {
        const isActive = pathname === tab.href;
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`flex-1 flex flex-col items-center py-2 text-xs transition-colors ${
              isActive ? "text-primary" : "text-text-secondary"
            }`}
          >
            <span className="text-lg">{tab.icon}</span>
            <span>{tab.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
