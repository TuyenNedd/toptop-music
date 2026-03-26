import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "TopTop Music",
  description: "TikTok trending sounds player",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={`${inter.variable} dark`}>
      <body className="bg-bg text-text font-sans antialiased min-h-screen">
        {/* PlayerBar — persistent bottom player, added in Story 5.2 */}
        {/* Navigation (TabBar mobile / Sidebar desktop) — added in Story 4.4 */}
        {children}
      </body>
    </html>
  );
}
