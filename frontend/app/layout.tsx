import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Africa Data Platform", template: "%s · Africa Data Platform" },
  description:
    "Clean, ready-to-use African data on mining, tourism, agriculture, finance and healthcare — via API, AI chat and downloads.",
};

const nav = [
  { href: "/catalog", label: "Catalogue" },
  { href: "/chat", label: "Ask AI" },
  { href: "/docs", label: "Docs" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-zinc-900 antialiased dark:bg-zinc-950 dark:text-zinc-100">
        <header className="border-b border-zinc-200 dark:border-zinc-800">
          <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
            <Link href="/" className="font-semibold tracking-tight">
              <span className="text-brand-600 dark:text-brand-500">Africa</span> Data Platform
            </Link>
            <nav className="flex gap-4 text-sm text-zinc-600 dark:text-zinc-400">
              {nav.map((item) => (
                <Link key={item.href} href={item.href} className="hover:text-zinc-900 dark:hover:text-white">
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-10">{children}</main>
      </body>
    </html>
  );
}
