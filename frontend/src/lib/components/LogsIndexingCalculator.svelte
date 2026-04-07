<script lang="ts">
	import { slide, fade } from 'svelte/transition';
	import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as Tabs from '$lib/components/ui/tabs';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import { formatCurrency, formatNumber } from '$lib/utils';
	import type { Product } from '$lib/api';

	export let products: Product[] = [];
	export let onAddToQuote: (items: { product: Product; quantity: number }[], label?: string) => void = () => {};

	// Wizard state
	let currentStep = 'volume';
	let showAdvancedOptions = false;

	// User inputs
	let ingestedLogsGB = 100;
	let avgLogSizeKB = 2;
	let indexingPercentage = 30;
	let retentionDays: 3 | 7 | 15 | 30 = 15;

	// Additional options
	let enableFlexStarter = false;
	let enableFlexStorage = false;
	let enableForwarding = false;
	let flexStarterEvents = 10;
	let flexStorageEvents = 50;
	let forwardingGB = 20;

	const flexStarterPresets = [
		{ label: '1×', multiplier: 1, description: 'Same as indexed' },
		{ label: '2×', multiplier: 2, description: '2× indexed' },
		{ label: '5×', multiplier: 5, description: '5× indexed' },
		{ label: '10×', multiplier: 10, description: '10× indexed' },
	];

	const forwardingPresets = [
		{ label: '25%', ratio: 0.25 },
		{ label: '50%', ratio: 0.5 },
		{ label: '75%', ratio: 0.75 },
		{ label: '100%', ratio: 1 },
	];

	function applyFlexPreset(multiplier: number) {
		flexStarterEvents = Math.max(1, Math.ceil(indexedLogsInMillions * multiplier));
	}

	function applyForwardingPreset(ratio: number) {
		forwardingGB = Math.max(1, Math.ceil(ingestedLogsGB * ratio));
	}

	// Presets
	const useCasePresets = [
		{ name: 'Minimal', percentage: 5, description: 'Errors only' },
		{ name: 'Standard', percentage: 15, description: 'Debug + Errors' },
		{ name: 'Extended', percentage: 30, description: 'Most logs' },
		{ name: 'Full', percentage: 100, description: 'Everything' },
	];

	const retentionOptions = [
		{ days: 3 as const, label: '3 days', description: 'Quick debugging' },
		{ days: 7 as const, label: '7 days', description: 'Weekly review' },
		{ days: 15 as const, label: '15 days', description: 'Standard' },
		{ days: 30 as const, label: '30 days', description: 'Extended' },
	];

	function retentionPrice(days: number): string | null {
		const p = products.find(pr =>
			pr.product.toLowerCase().includes('indexed log events') &&
			pr.billing_unit.toLowerCase().includes(`${days}-day`)
		);
		return p?.billed_annually ?? null;
	}

	// Calculations
	$: totalLogsPerMonth = (ingestedLogsGB * 1024 * 1024) / avgLogSizeKB;
	$: indexedLogsCount = totalLogsPerMonth * (indexingPercentage / 100);
	$: indexedLogsInMillions = indexedLogsCount / 1_000_000;

	// Products lookup
	$: ingestionProduct = products.find(p => 
		p.product.toLowerCase().includes('logs') && 
		p.product.toLowerCase().includes('ingestion')
	);
	$: indexedProduct = products.find(p => 
		p.product.toLowerCase().includes('indexed log events') &&
		p.billing_unit.toLowerCase().includes(`${retentionDays}-day`)
	);
	$: flexStarterProduct = products.find(p => p.product === 'Flex Logs Starter');
	$: flexStorageProduct = products.find(p => p.product === 'Flex Logs Storage');
	$: forwardingProduct = products.find(p => p.product === 'Logs - Forwarding to Custom Destinations');

	function parsePrice(priceStr: string | null): number {
		if (!priceStr) return 0;
		const match = priceStr.match(/[\d.]+/);
		return match ? parseFloat(match[0]) : 0;
	}

	$: ingestionPrice = parsePrice(ingestionProduct?.billed_annually);
	$: indexedPrice = parsePrice(indexedProduct?.billed_annually);
	$: flexStarterPrice = parsePrice(flexStarterProduct?.billed_annually);
	$: flexStoragePrice = parsePrice(flexStorageProduct?.billed_annually);
	$: forwardingPrice = parsePrice(forwardingProduct?.billed_annually);

	$: ingestionCost = ingestedLogsGB * ingestionPrice;
	$: indexedCost = indexedLogsInMillions * indexedPrice;
	$: flexStarterCost = enableFlexStarter ? flexStarterEvents * flexStarterPrice : 0;
	$: flexStorageCost = enableFlexStorage ? flexStorageEvents * flexStoragePrice : 0;
	$: forwardingCost = enableForwarding ? forwardingGB * forwardingPrice : 0;
	$: additionalCost = flexStarterCost + flexStorageCost + forwardingCost;
	$: totalMonthlyCost = ingestionCost + indexedCost + additionalCost;

	let customLabel = '';

	function addToQuote() {
		const items: { product: Product; quantity: number }[] = [];
		if (ingestionProduct && ingestedLogsGB > 0) {
			items.push({ product: ingestionProduct, quantity: Math.ceil(ingestedLogsGB) });
		}
		if (indexedProduct && indexedLogsInMillions > 0) {
			items.push({ product: indexedProduct, quantity: Math.ceil(indexedLogsInMillions) });
		}
		if (enableFlexStarter && flexStarterProduct && flexStarterEvents > 0) {
			items.push({ product: flexStarterProduct, quantity: Math.ceil(flexStarterEvents) });
		}
		if (enableFlexStorage && flexStorageProduct && flexStorageEvents > 0) {
			items.push({ product: flexStorageProduct, quantity: Math.ceil(flexStorageEvents) });
		}
		if (enableForwarding && forwardingProduct && forwardingGB > 0) {
			items.push({ product: forwardingProduct, quantity: Math.ceil(forwardingGB) });
		}
		const label = customLabel.trim() || undefined;
		if (items.length > 0) onAddToQuote(items, label);
	}
</script>

<Card class="border-border overflow-hidden">
	<CardContent class="p-0">
		<!-- ROW 1: Title -->
		<div class="px-6 py-4 border-b border-border flex items-start gap-3">
			<div class="flex h-9 w-9 items-center justify-center rounded-sm bg-muted flex-shrink-0">
				<svg class="h-5 w-5 text-black" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
					<polyline points="14 2 14 8 20 8" />
					<line x1="16" y1="13" x2="8" y2="13" />
					<line x1="16" y1="17" x2="8" y2="17" />
					<polyline points="10 9 9 9 8 9" />
				</svg>
			</div>
			<div>
				<h2 class="text-lg font-semibold">Logging Without Limits</h2>
				<p class="text-sm text-muted-foreground">Estimate your log indexing needs based on ingestion volume</p>
			</div>
		</div>

		<!-- ROW 2: Summary -->
		<div class="px-6 py-3 border-b border-border">
			<p class="text-[13px] text-muted-foreground">
				From <span class="font-mono font-medium text-foreground">{ingestedLogsGB} GB</span>/mo, indexing <span class="font-mono font-medium text-foreground">{indexingPercentage}%</span> gives you <span class="font-mono font-medium text-foreground">{indexedLogsInMillions.toFixed(1)}M</span> searchable events{#if enableFlexStarter || enableFlexStorage || enableForwarding} + extras{/if} for <span class="font-mono font-medium text-foreground">{retentionDays} days</span> at <span class="font-mono font-bold text-foreground text-base">{formatCurrency(totalMonthlyCost)}</span>/mo.
			</p>
		</div>

		<!-- ROW 3: Tabs -->
		<div class="px-6 py-3 border-b border-border bg-muted/30">
			<Tabs.Root bind:value={currentStep}>
				<Tabs.List class="w-full grid grid-cols-4 gap-0.5 p-0.5">
					<Tabs.Trigger value="volume" class="w-full cursor-pointer">Ingesting</Tabs.Trigger>
					<Tabs.Trigger value="indexing" class="w-full cursor-pointer">Indexing</Tabs.Trigger>
					<Tabs.Trigger value="retention" class="w-full cursor-pointer">Retention</Tabs.Trigger>
					<Tabs.Trigger value="extras" class="w-full cursor-pointer">Extras</Tabs.Trigger>
				</Tabs.List>
			</Tabs.Root>
		</div>

		<!-- ROW 4: Form Content -->
		<div class="grid grid-cols-[1fr_1px_2fr_1px_1fr] min-h-[300px]">
			
			<!-- Left Panel: Info -->
			<div class="p-6 flex flex-col justify-center">
				{#if currentStep === 'volume'}
					<h3 class="text-lg font-semibold mb-2">Log Ingesting</h3>
					<p class="text-xs text-muted-foreground">
						Enter your monthly log ingestion volume and average log size to calculate the number of log events.
					</p>
				<div class="mt-4 p-3 bg-muted border-l-2 border-foreground">
					<div class="text-xs text-muted-foreground">Calculated logs</div>
					<div class="text-xl font-bold font-mono">{formatNumber(Math.round(totalLogsPerMonth))}</div>
					<div class="text-xs text-muted-foreground">events/month</div>
				</div>
				{:else if currentStep === 'retention'}
					<h3 class="text-lg font-semibold mb-2">Retention Period</h3>
					<p class="text-xs text-muted-foreground">
						Choose how long indexed logs should remain searchable. Longer retention costs more per event.
					</p>
				{:else if currentStep === 'indexing'}
					<h3 class="text-lg font-semibold mb-2">Indexing Strategy</h3>
					<p class="text-xs text-muted-foreground">
						Select what percentage of logs to index for search. Index only what you need to query.
					</p>
				<div class="mt-4 p-3 bg-muted border-l-2 border-foreground">
					<div class="text-xs text-muted-foreground">Indexed logs</div>
					<div class="text-xl font-bold font-mono">{formatNumber(Math.round(indexedLogsCount))}</div>
					<div class="text-xs text-muted-foreground">{indexedLogsInMillions.toFixed(2)}M events</div>
				</div>
				{:else if currentStep === 'extras'}
					<h3 class="text-lg font-semibold mb-2">Additional Options</h3>
					<p class="text-xs text-muted-foreground">
						Optional Flex Logs and paid forwarding to <strong class="font-medium text-foreground">custom</strong> destinations.
						S3, Azure, and GCS forwarding stays free—leave forwarding unchecked if that is all you use.
					</p>
				{/if}
			</div>

			<!-- Separator -->
			<div class="bg-border"></div>

			<!-- Center Panel: Form -->
			<div class="p-6">
				{#if currentStep === 'volume'}
					<div class="space-y-6">
						<div class="space-y-2">
							<label for="ingestedLogs" class="text-sm font-medium">
								Monthly ingestion volume (GB)
							</label>
							<Input 
								id="ingestedLogs"
								type="number" 
								bind:value={ingestedLogsGB} 
								min="1" 
								class="font-mono text-lg max-w-xs"
							/>
							{#if ingestionProduct}
								<p class="text-xs text-muted-foreground font-mono">{ingestionProduct.billed_annually}/GB ingested</p>
							{/if}
						</div>

						<!-- Advanced Options (Collapsible) -->
						<div class="border-t border-border pt-4">
							<button
								type="button"
								class="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
								on:click={() => showAdvancedOptions = !showAdvancedOptions}
							>
								<svg 
									class="w-4 h-4 transition-transform {showAdvancedOptions ? 'rotate-90' : ''}" 
									viewBox="0 0 24 24" 
									fill="none" 
									stroke="currentColor" 
									stroke-width="2"
								>
									<path d="M9 18l6-6-6-6"/>
								</svg>
								Advanced options
							</button>
							
							{#if showAdvancedOptions}
								<div class="mt-4 space-y-2" transition:slide={{ duration: 150 }}>
									<label for="avgLogSize" class="text-sm font-medium">
										Average log entry size (KB)
									</label>
									<Input 
										id="avgLogSize"
										type="number" 
										bind:value={avgLogSizeKB} 
										min="0.1" 
										step="0.1"
										class="font-mono max-w-xs"
									/>
									<p class="text-xs text-muted-foreground">
										Typical: JSON ~1-2KB, plain text ~0.5KB
									</p>
								</div>
							{/if}
						</div>
					</div>

				{:else if currentStep === 'retention'}
					<div class="grid grid-cols-2 gap-3">
						{#each retentionOptions as option}
							<button
								type="button"
								class="w-full touch-manipulation p-3 border text-left transition-all rounded-sm
									{retentionDays === option.days 
										? 'border-foreground bg-muted' 
										: 'border-border hover:border-foreground/50 hover:bg-muted/50'}"
								on:click={() => retentionDays = option.days}
							>
								<div class="font-semibold text-sm">{option.label}</div>
								<div class="text-xs text-muted-foreground">{option.description}</div>
								{#if retentionPrice(option.days)}
									<div class="text-[10px] font-mono text-muted-foreground/70 mt-1">{retentionPrice(option.days)}/1M events</div>
								{/if}
							</button>
						{/each}
					</div>

				{:else if currentStep === 'indexing'}
					<div class="space-y-6">
						<div class="grid grid-cols-2 gap-3">
							{#each useCasePresets as preset}
								<button
									type="button"
									class="w-full touch-manipulation p-3 border text-left transition-all rounded-sm
										{indexingPercentage === preset.percentage 
											? 'border-foreground bg-muted' 
											: 'border-border hover:border-foreground/50 hover:bg-muted/50'}"
									on:click={() => indexingPercentage = preset.percentage}
								>
									<div class="flex items-center justify-between">
										<span class="font-semibold text-sm">{preset.name}</span>
										<span class="text-xs font-mono bg-muted px-1.5 py-0.5 rounded">{preset.percentage}%</span>
									</div>
									<div class="text-xs text-muted-foreground">{preset.description}</div>
								</button>
							{/each}
						</div>
						<div class="space-y-2">
							<div class="flex justify-between text-sm">
								<span>Custom percentage</span>
								<span class="font-mono font-bold">{indexingPercentage}%</span>
							</div>
							<input 
								type="range" 
								bind:value={indexingPercentage} 
								min="1" 
								max="100" 
								class="w-full accent-foreground h-2"
							/>
						</div>
					</div>

				{:else if currentStep === 'extras'}
					<div class="space-y-3">
					<label
						class="flex items-start gap-3 p-4 border cursor-pointer touch-manipulation transition-all rounded-sm
							{enableFlexStarter ? 'border-foreground bg-muted' : 'border-border hover:border-foreground/50 hover:bg-muted/50'}"
					>
						<input 
							type="checkbox" 
							bind:checked={enableFlexStarter}
							class="mt-0.5 h-4 w-4 shrink-0 accent-foreground"
						/>
						<div class="min-w-0 flex-1">
							<div class="font-medium text-sm">Flex Logs Starter</div>
							<div class="text-xs text-muted-foreground">Archive non-indexed events for cost-effective querying</div>
							{#if enableFlexStarter}
								<div class="mt-2 space-y-2" transition:slide={{ duration: 150 }}>
									<div class="flex flex-wrap gap-1">
										{#each flexStarterPresets as preset}
											<Tooltip.Root>
												<Tooltip.Trigger asChild let:builder>
													<button
														use:builder.action
														{...builder}
														type="button"
														class="px-2 py-0.5 rounded text-[10px] font-mono border transition-all
															{flexStarterEvents === Math.max(1, Math.ceil(indexedLogsInMillions * preset.multiplier))
																? 'border-foreground bg-foreground text-background'
																: 'border-border hover:border-foreground/50 text-muted-foreground hover:text-foreground'}"
														on:click|preventDefault|stopPropagation={() => applyFlexPreset(preset.multiplier)}
													>
														{preset.label}
													</button>
												</Tooltip.Trigger>
												<Tooltip.Content>{preset.description} — {Math.max(1, Math.ceil(indexedLogsInMillions * preset.multiplier))}M events</Tooltip.Content>
											</Tooltip.Root>
										{/each}
									</div>
									<div class="flex flex-wrap items-center gap-2">
										<Input type="number" bind:value={flexStarterEvents} min="1" class="min-h-9 min-w-[5.5rem] font-mono text-sm" />
										<span class="text-xs text-muted-foreground">M events</span>
										{#if flexStarterPrice > 0}
											<span class="text-xs ml-auto">{formatCurrency(flexStarterCost)}/mo</span>
										{/if}
									</div>
								</div>
							{/if}
						</div>
					</label>

					<label
						class="flex items-start gap-3 p-4 border cursor-pointer touch-manipulation transition-all rounded-sm
							{enableFlexStorage ? 'border-foreground bg-muted' : 'border-border hover:border-foreground/50 hover:bg-muted/50'}"
					>
						<input 
							type="checkbox" 
							bind:checked={enableFlexStorage}
							class="mt-0.5 h-4 w-4 shrink-0 accent-foreground"
						/>
						<div class="min-w-0 flex-1">
							<div class="font-medium text-sm">Flex Logs Storage</div>
							<div class="text-xs text-muted-foreground">Long-term storage for compliance</div>
							{#if enableFlexStorage}
								<div class="mt-2 flex flex-wrap items-center gap-2" transition:slide={{ duration: 150 }}>
									<Input type="number" bind:value={flexStorageEvents} min="1" class="min-h-9 min-w-[5.5rem] font-mono text-sm" />
									<span class="text-xs text-muted-foreground">M events</span>
									{#if flexStoragePrice > 0}
										<span class="text-xs ml-auto">{formatCurrency(flexStorageCost)}/mo</span>
									{/if}
								</div>
							{/if}
						</div>
					</label>

					<label
						class="flex items-start gap-3 p-4 border cursor-pointer touch-manipulation transition-all rounded-sm
							{enableForwarding ? 'border-foreground bg-muted' : 'border-border hover:border-foreground/50 hover:bg-muted/50'}"
					>
						<input 
							type="checkbox" 
							bind:checked={enableForwarding}
							class="mt-0.5 h-4 w-4 shrink-0 accent-foreground"
						/>
						<div class="min-w-0 flex-1">
							<div class="font-medium text-sm flex items-center gap-1.5">
								Custom log forwarding
								<Tooltip.Root>
									<Tooltip.Trigger asChild let:builder>
										<span use:builder.action {...builder} class="inline-flex cursor-help">
											<svg class="h-3.5 w-3.5 text-muted-foreground/50 hover:text-muted-foreground transition-colors" viewBox="0 0 24 24" fill="currentColor">
												<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
											</svg>
										</span>
									</Tooltip.Trigger>
									<Tooltip.Content class="max-w-xs">Forwarding to S3, Azure Blob, and GCS is free. This option estimates the cost for custom destinations only (e.g. Splunk, generic HTTP)—billed per GB forwarded.</Tooltip.Content>
								</Tooltip.Root>
							</div>
							{#if enableForwarding}
								<div class="mt-2 space-y-2" transition:slide={{ duration: 150 }}>
									<div class="flex flex-wrap gap-1">
										{#each forwardingPresets as preset}
											<Tooltip.Root>
												<Tooltip.Trigger asChild let:builder>
													<button
														use:builder.action
														{...builder}
														type="button"
														class="px-2 py-0.5 rounded text-[10px] font-mono border transition-all
															{forwardingGB === Math.max(1, Math.ceil(ingestedLogsGB * preset.ratio))
																? 'border-foreground bg-foreground text-background'
																: 'border-border hover:border-foreground/50 text-muted-foreground hover:text-foreground'}"
														on:click|preventDefault|stopPropagation={() => applyForwardingPreset(preset.ratio)}
													>
														{preset.label}
													</button>
												</Tooltip.Trigger>
												<Tooltip.Content>{preset.label} of ingested volume — {Math.max(1, Math.ceil(ingestedLogsGB * preset.ratio))} GB</Tooltip.Content>
											</Tooltip.Root>
										{/each}
									</div>
									<div class="flex flex-wrap items-center gap-2">
										<Input type="number" bind:value={forwardingGB} min="1" class="min-h-9 min-w-[5.5rem] font-mono text-sm" />
										<span class="text-xs text-muted-foreground">GB/mo (custom only)</span>
										{#if forwardingPrice > 0}
											<span class="text-xs ml-auto">{formatCurrency(forwardingCost)}/mo</span>
										{/if}
									</div>
								</div>
							{/if}
						</div>
					</label>
					</div>
				{/if}
			</div>

			<!-- Separator -->
			<div class="bg-border"></div>

			<!-- Right Panel: Cost Breakdown -->
			<div class="p-6">
				<h4 class="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-4">Cost Breakdown</h4>
				<div class="space-y-3 text-sm">
					<div>
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 bg-sky-500"></div>
							<span>Ingestion</span>
						</div>
						<div class="font-mono text-right">{formatCurrency(ingestionCost)}</div>
					</div>
					<div>
						<div class="flex items-center gap-2">
							<div class="w-2 h-2 bg-amber-500"></div>
							<span>Indexed ({retentionDays}d)</span>
						</div>
						<div class="font-mono text-right">{formatCurrency(indexedCost)}</div>
					</div>
					{#if enableFlexStarter}
						<div>
							<div class="flex items-center gap-2">
								<div class="w-2 h-2 bg-emerald-500"></div>
								<span>Flex Starter</span>
							</div>
							<div class="font-mono text-right">{formatCurrency(flexStarterCost)}</div>
						</div>
					{/if}
					{#if enableFlexStorage}
						<div>
							<div class="flex items-center gap-2">
								<div class="w-2 h-2 bg-emerald-500"></div>
								<span>Flex Storage</span>
							</div>
							<div class="font-mono text-right">{formatCurrency(flexStorageCost)}</div>
						</div>
					{/if}
					{#if enableForwarding}
						<div>
							<div class="flex items-center gap-2">
								<div class="w-2 h-2 bg-emerald-500"></div>
								<span>Custom forwarding</span>
							</div>
							<div class="font-mono text-right">{formatCurrency(forwardingCost)}</div>
						</div>
					{/if}
				</div>

				<!-- Visual bar -->
				{#if totalMonthlyCost > 0}
					<div class="mt-4">
						<div class="h-2 flex overflow-hidden rounded-sm">
							<div class="bg-sky-500" style="width: {(ingestionCost / totalMonthlyCost) * 100}%"></div>
							<div class="bg-amber-500" style="width: {(indexedCost / totalMonthlyCost) * 100}%"></div>
							{#if additionalCost > 0}
								<div class="bg-emerald-500" style="width: {(additionalCost / totalMonthlyCost) * 100}%"></div>
							{/if}
						</div>
					</div>
				{/if}

				<div class="mt-4 pt-4 border-t border-border">
					<div class="flex justify-between items-center text-muted-foreground text-xs">
						<span>Monthly</span>
						<span class="font-mono">{formatCurrency(totalMonthlyCost)}</span>
					</div>
					<div class="flex justify-between items-center mt-2">
						<span class="font-medium">Annual</span>
						<span class="font-mono font-bold text-lg">{formatCurrency(totalMonthlyCost * 12)}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- ROW 5: Action Button -->
		<div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-border">
			<input
				type="text"
				bind:value={customLabel}
				on:input={() => { customLabel = customLabel.replace(/[<>"'`;]/g, ''); }}
				placeholder="Label (e.g. production)"
				maxlength="50"
				class="h-9 w-48 rounded-md border border-border bg-background px-3 text-xs placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1 focus:ring-ring"
			/>
			<Button 
				class="bg-foreground text-background hover:bg-foreground/80"
				on:click={addToQuote}
				disabled={!ingestionProduct || !indexedProduct}
			>
				+ Add to Quote
			</Button>
		</div>

		{#if !ingestionProduct || !indexedProduct}
			<div class="px-6 py-2 bg-amber-50 border-t border-amber-200 text-xs text-amber-700 text-center">
				⚠️ Some log products not found. Please sync pricing data.
			</div>
		{/if}
	</CardContent>
</Card>
