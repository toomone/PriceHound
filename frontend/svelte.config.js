import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
import { mdsvex } from 'mdsvex';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	extensions: ['.svelte', '.md'],
	preprocess: [
		vitePreprocess(),
		mdsvex({
			extensions: ['.md']
		})
	],
	kit: {
		adapter: adapter({
			// Single SPA shell at index.html so hosts that rewrite /* → /index.html (Render default)
			// serve the correct entry for deep links like /quote/:id. Avoid 200.html + prerendered /
			// which breaks when the wrong HTML is served for nested paths.
			fallback: 'index.html'
		}),
		prerender: {
			handleHttpError: 'warn'
		},
		paths: {
			// Root-relative assets so if a host serves prerendered index.html for deep links
			// (e.g. /quote/*) without rewriting to 200.html, JS/CSS still load from /_app/...
			relative: false
		},
		alias: {
			$lib: './src/lib'
		}
	}
};

export default config;

