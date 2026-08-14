// BottomBar.astro exports `BottomBarAction` only from its .astro frontmatter,
// which tsc can't resolve from a plain .ts module. Mirror the shape here.
export interface BottomBarAction {
  icon: string
  label: string
  href: string
  active?: boolean
}
export const bottomBarActions: BottomBarAction[] = [
  { icon: '⌂', label: 'Home', href: '/' },
  { icon: '⊞', label: 'Collections', href: '/collections/' },
  { icon: '☷', label: 'All', href: '/all/' },
  { icon: '⌕', label: 'Search', href: '/search/' },
  { icon: '☰', label: 'Menu', href: '#sb-toggle' },
]
