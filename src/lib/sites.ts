/**
 * The oriz family — single source of truth for project links shown in the
 * footer and header search dropdown. Mirrors oriz-home/src/lib/sites.ts.
 */

export interface Site {
  slug: string
  name: string
  url: string
  tagline: string
  emoji: string
  category: 'reading' | 'tools' | 'finance' | 'personal'
}

export const SITES: Site[] = [
  {
    slug: 'blog',
    name: 'Blog',
    url: 'https://blog.oriz.in',
    tagline: 'Long-form writing on engineering, finance, and books',
    emoji: '✍️',
    category: 'reading',
  },
  {
    slug: 'books',
    name: 'Books',
    url: 'https://books.oriz.in',
    tagline: 'NCERT textbook directory + client-side PDF merger',
    emoji: '📚',
    category: 'reading',
  },
  {
    slug: 'cards',
    name: 'Cards',
    url: 'https://cards.oriz.in',
    tagline: '750 India card profiles — credit, debit, prepaid',
    emoji: '💳',
    category: 'finance',
  },
  {
    slug: 'finance',
    name: 'Finance',
    url: 'https://finance.oriz.in',
    tagline: 'SIP, EMI, FIRE, tax — calculators that show the math',
    emoji: '📊',
    category: 'finance',
  },
  {
    slug: 'journal',
    name: 'Journal',
    url: 'https://journal.oriz.in',
    tagline: 'Privacy-first PWA journal — ten journal types, offline',
    emoji: '📓',
    category: 'personal',
  },
  {
    slug: 'urls-to-md',
    name: 'URLs to Markdown',
    url: 'https://urls-to-md.oriz.in',
    tagline: 'Batch-convert any URL to clean Markdown — 100% client-side',
    emoji: '🔗',
    category: 'tools',
  },
  {
    slug: 'image-tools',
    name: 'Image Tools',
    url: 'https://image.oriz.in',
    tagline: 'Compress, convert, resize — runs in your browser',
    emoji: '🖼️',
    category: 'tools',
  },
  {
    slug: 'pdf-tools',
    name: 'PDF Tools',
    url: 'https://pdf.oriz.in',
    tagline: 'Merge, split, compress, sign — never uploaded',
    emoji: '📄',
    category: 'tools',
  },
]
