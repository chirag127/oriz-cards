export interface SiteConfig {
  slug: string
  name: string
  origin: string
  tagline: string
  description: string
}

export const SITE_CONFIG: SiteConfig = {
  slug: 'cards',
  name: 'cards',
  origin: 'https://cards.oriz.in',
  tagline: 'A Bloomberg-terminal-for-Indian-credit-cards. 750 profiles, every fee, no rosettes.',
  description:
    'Static catalog of 750 credit, debit, and prepaid cards issued in India — fees, rewards, eligibility, and the small-print every issuer site buries.',
}
