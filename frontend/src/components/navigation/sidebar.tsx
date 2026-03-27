"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home", icon: "🏠" },
  { href: "/search", label: "Search", icon: "🔍" },
  { href: "/library", label: "Library", icon: "📚" },
  { href: "/admin", label: "Admin", icon: "⚙️" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex flex-col w-64 bg-surface border-r border-border h-screen fixed left-0 top-0 z-20 py-6">
      <h1 className="text-xl font-bold text-primary px-6 mb-8">TopTop Music</h1>
      <nav className="flex flex-col gap-1 px-3">
        {links.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive
                  ? "text-primary border-l-2 border-primary bg-surface-hover"
                  : "text-text-secondary hover:bg-surface-hover"
              }`}
            >
              <span>{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
