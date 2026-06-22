import type { BottomBarAction } from '@chirag127/astro-chrome/BottomBar.astro'
export const bottomBarActions: BottomBarAction[] = [
  { icon: '⌂', label: 'Home', href: '/' },
  { icon: '⊞', label: 'Collections', href: '/collections/' },
  { icon: '☷', label: 'All', href: '/all/' },
  { icon: '⌕', label: 'Search', href: '/search/' },
  { icon: '☰', label: 'Menu', href: '#sb-toggle' },
]
