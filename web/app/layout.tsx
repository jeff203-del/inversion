import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Defend It — prove you own the work",
  description: "An evidence-backed way to assess how developers understand their code."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><head>
    <meta name="theme-color" content="#0e1014" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
    <link href="/styles.css" rel="stylesheet" />
  </head><body>{children}</body></html>;
}
