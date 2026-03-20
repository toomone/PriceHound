<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import type { Template } from '$lib/api';

	export let filteredTemplates: Template[] = [];
	export let loadingTemplates = false;
	export let stackFilter = '';
	/** Called when user expands — should load templates if not already loaded */
	export let loadOnExpand: () => void | Promise<void> = () => {};

	const dispatch = createEventDispatcher<{ logs: void; preview: Template }>();

	let expanded = false;

	async function toggleExpand() {
		expanded = !expanded;
		if (expanded) {
			await loadOnExpand();
		}
	}

	function focusProductSearch() {
		const searchInput = document.querySelector('input[placeholder="Search products..."]');
		if (searchInput instanceof HTMLInputElement) searchInput.focus();
	}
</script>

<!-- Static shell: always the same DOM on first paint; expand only adds the panel below -->
<div class="mb-6 rounded-lg border border-border bg-card shadow-sm">
	<div class="flex items-center justify-between p-4">
		<button
			type="button"
			class="flex min-w-0 flex-1 items-center gap-2 text-left hover:opacity-80 transition-opacity"
			aria-expanded={expanded}
			aria-controls="get-started-panel"
			id="get-started-toggle"
			on:click={toggleExpand}
		>
			<svg
				class="h-4 w-4 shrink-0 text-muted-foreground transition-transform duration-200 {expanded ? 'rotate-90' : ''}"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				aria-hidden="true"
			>
				<path d="m9 18 6-6-6-6" />
			</svg>
			<h3 class="text-sm font-semibold flex items-center gap-2">
				<svg class="h-4 w-4 text-datadog-purple" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
					<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
				</svg>
				Get Started
			</h3>
			<span class="text-xs text-muted-foreground hidden sm:inline truncate">
				Pick an example stack or build from scratch
			</span>
		</button>

		<button
			type="button"
			class="ml-2 flex shrink-0 items-center gap-2 px-3 py-1.5 rounded-md border border-datadog-purple/30 hover:border-datadog-purple/50 bg-datadog-purple/5 hover:bg-datadog-purple/10 transition-all text-xs font-medium text-datadog-purple"
			on:click={() => dispatch('logs')}
		>
			<svg class="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
				<rect x="4" y="2" width="16" height="20" rx="2" />
				<path d="M8 6h8M8 10h8M8 14h4" />
			</svg>
			<span class="hidden sm:inline">Logging Without Limits</span>
			<span class="sm:hidden">Logs</span>
		</button>
	</div>

	{#if expanded}
		<div id="get-started-panel" class="px-4 pb-4 border-t border-border/40" role="region" aria-labelledby="get-started-toggle">
			{#if loadingTemplates}
				<div class="flex flex-col items-center justify-center gap-3 py-12" aria-busy="true" aria-live="polite">
					<svg class="h-8 w-8 animate-spin text-datadog-purple" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M21 12a9 9 0 11-6.219-8.56" />
					</svg>
					<p class="text-sm text-muted-foreground">Loading example stacks…</p>
				</div>
			{:else}
				<div class="flex items-center justify-end mb-3 pt-3">
					<div class="relative">
						<svg
							class="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground/50"
							viewBox="0 0 24 24"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							aria-hidden="true"
						>
							<circle cx="11" cy="11" r="8" />
							<path d="m21 21-4.35-4.35" />
						</svg>
						<input
							type="text"
							bind:value={stackFilter}
							placeholder="Filter stacks..."
							class="h-8 w-40 rounded-md border border-border bg-background pl-8 pr-3 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-ring"
							autocomplete="off"
						/>
					</div>
				</div>

				<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3 max-h-[6.5rem] overflow-y-auto pr-1">
					<button
						type="button"
						class="flex flex-col p-2.5 rounded-md border-2 border-dashed border-border hover:border-foreground/30 bg-background hover:bg-muted/30 transition-all text-left group min-h-[5.5rem]"
						on:click={focusProductSearch}
					>
						<div class="flex items-center gap-2">
							<div class="flex items-center justify-center h-6 w-6 rounded-md bg-muted shrink-0 group-hover:bg-foreground/10 transition-colors">
								<svg class="h-3.5 w-3.5 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M12 5v14M5 12h14" />
								</svg>
							</div>
							<div class="text-xs font-medium">Start from scratch</div>
						</div>
						<div class="text-[10px] text-muted-foreground leading-tight mt-1.5">Build your own quote</div>
					</button>

					{#each filteredTemplates as template (template.id)}
						<button
							type="button"
							class="relative flex flex-col p-2.5 rounded-md border border-border hover:border-foreground/30 bg-background hover:bg-muted/30 transition-all text-left min-h-[5.5rem]"
							on:click={() => dispatch('preview', template)}
						>
							<span class="absolute top-2 right-2 flex items-center justify-center h-5 min-w-5 px-1.5 rounded-full bg-datadog-purple text-[10px] font-medium text-white">
								{template.items.length}
							</span>
							<div class="flex items-center gap-2 pr-6">
								<div class="flex items-center justify-center h-6 w-6 rounded-md bg-muted shrink-0">
									<svg class="h-3.5 w-3.5 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
										<path d="M22 12l-10 5-10-5" />
										<path d="M22 7l-10 5-10-5 10-5 10 5z" />
										<path d="M2 17l10 5 10-5" />
									</svg>
								</div>
								<div class="text-xs font-medium">{template.name}</div>
							</div>
							<div class="text-[10px] text-muted-foreground leading-tight mt-1.5 line-clamp-3">
								{template.description || 'Example stack'}
							</div>
						</button>
					{/each}

					{#if filteredTemplates.length === 0 && stackFilter !== ''}
						<div class="col-span-full p-3 flex items-center justify-center text-xs text-muted-foreground">
							No stacks match "{stackFilter}"
						</div>
					{/if}
				</div>
			{/if}
		</div>
	{/if}
</div>
