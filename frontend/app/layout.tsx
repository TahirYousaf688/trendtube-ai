import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TrendTube AI - AI-Powered YouTube Content Factory',
  description:
    'Automated trend discovery, research, scripting, voice, editing, and publishing for modern creators.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}
