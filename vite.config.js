import { sveltekit } from '@sveltejs/kit/vite';

/** @type {import('vite').UserConfig} */
const config = {
	plugins: [sveltekit()],
	test: {
		include: ['frontend/src/**/*.{test,spec}.{js,ts}']
	},
};

export default config;
