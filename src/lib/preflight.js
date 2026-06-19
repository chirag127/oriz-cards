/**
 * Pre-paint script — reads localStorage keys 'oriz:theme' + 'oriz:accent' and
 * writes data-theme/data-accent on <html> BEFORE first paint to avoid flash.
 * Runs as an inline <script is:inline> in BaseLayout's <head>.
 *
 * Defaults: theme=dark, accent=amber. localStorage value 'system' for theme
 * means follow prefers-color-scheme.
 */
;(() => {
  try {
    const t = localStorage.getItem('oriz:theme') || 'dark'
    const a = localStorage.getItem('oriz:accent') || 'amber'
    const theme = t === 'system'
      ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : t
    document.documentElement.setAttribute('data-theme', theme)
    document.documentElement.setAttribute('data-accent', a)
  } catch {
    document.documentElement.setAttribute('data-theme', 'dark')
    document.documentElement.setAttribute('data-accent', 'amber')
  }
})()
