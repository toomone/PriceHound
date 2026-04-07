<script lang="ts">
	import { cn } from '$lib/utils';
	import { buttonVariants, type Variant, type Size } from './index';

	let className: string | undefined = undefined;
	export { className as class };
	export let variant: Variant = 'default';
	export let size: Size = 'default';
	export let disabled: boolean = false;
	export let type: 'button' | 'submit' | 'reset' = 'button';
	export let href: string | undefined = undefined;
</script>

{#if href}
	<a
		{href}
		class={cn(buttonVariants({ variant, size }), disabled && 'pointer-events-none opacity-50', className)}
		{...$$restProps}
	>
		<slot />
	</a>
{:else}
	<button
		{type}
		{disabled}
		class={cn(buttonVariants({ variant, size }), className)}
		on:click
		on:keydown
		{...$$restProps}
	>
		<slot />
	</button>
{/if}

