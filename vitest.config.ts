import { getViteConfig } from 'astro/config'
import { defineConfig } from 'vitest/config'

export default getViteConfig(
  defineConfig({
    test: {
      environment: 'happy-dom',
      globals: true,
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html'],
        include: ['src/**/*.{ts,tsx}'],
        exclude: ['src/**/*.{test,spec}.{ts,tsx}', 'src/**/*.astro'],
      },
    },
  }),
)
