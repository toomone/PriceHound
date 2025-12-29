<script lang="ts">
	import { slide, fade } from 'svelte/transition';
	import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Badge } from '$lib/components/ui/badge';
	import { formatCurrency, formatNumber } from '$lib/utils';
	import type { Product } from '$lib/api';

	export let products: Product[] = [];
	export let onAddToQuote: (items: { product: Product; quantity: number }[]) => void = () => {};

	// Wizard state
	let currentStep = 0;
	const steps = [
		{ id: 'volume', title: 'Log Volume', icon: '📊', description: 'How much data?' },
		{ id: 'retention', title: 'Retention', icon: '📅', description: 'How long to keep?' },
		{ id: 'indexing', title: 'Indexing', icon: '🔍', description: 'What to search?' },
		{ id: 'extras', title: 'Extras', icon: '⚡', description: 'Additional options' },
	];

	// User inputs
	let ingestedLogsGB = 100;
	let avgLogSizeKB = 2;
	let indexingPercentage = 15;
	let retentionDays: 3 | 7 | 15 | 30 = 15;

	// Additional options
	let enableFlexStarter = false;
	let enableFlexStorage = false;
	let enableForwarding = false;
	let flexStarterEvents = 10;
	let flexStorageEvents = 50;
	let forwardingGB = 20;

	// Presets
	const useCasePresets = [
		{ name: 'Minimal', percentage: 5, emoji: '🎯', description: 'Errors only' },
		{ name: 'Standard', percentage: 15, emoji: '⚖️', description: 'Debug + Errors' },
		{ name: 'Extended', percentage: 30, emoji: '🔬', description: 'Most logs' },
		{ name: 'Full', percentage: 100, emoji: '📦', description: 'Everything' },
	];

	const retentionOptions = [
		{ days: 3 as const, label: '3 days', emoji: '⚡', description: 'Quick debugging' },
		{ days: 7 as const, label: '7 days', emoji: '📆', description: 'Weekly review' },
		{ days: 15 as const, label: '15 days', emoji: '📊', description: 'Standard' },
		{ days: 30 as const, label: '30 days', emoji: '🗄️', description: 'Extended' },
	];

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

	// Navigation
	function nextStep() {
		if (currentStep < steps.length - 1) currentStep++;
	}
	function prevStep() {
		if (currentStep > 0) currentStep--;
	}
	function goToStep(index: number) {
		currentStep = index;
	}

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
		if (items.length > 0) onAddToQuote(items);
	}
</script>

<Card class="border-datadog-purple/20 overflow-hidden">
	<CardHeader class="bg-gradient-to-r from-datadog-purple/10 to-datadog-blue/10 pb-4">
		<div class="flex items-center gap-3">
			<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-datadog-purple to-datadog-blue text-xl">
				📋
			</div>
			<div>
				<CardTitle>Log Indexing Wizard</CardTitle>
				<CardDescription>Configure your log indexing step by step</CardDescription>
			</div>
		</div>
	</CardHeader>

	<CardContent class="p-0">
		<div class="grid lg:grid-cols-[240px_1fr_280px]">
			
			<!-- LEFT: Step Navigation -->
			<div class="border-r border-border bg-muted/30 p-4 hidden lg:block">
				<div class="space-y-1">
					{#each steps as step, i}
						<button
							type="button"
							class="w-full flex items-center gap-3 p-3 rounded-lg text-left transition-all
								{currentStep === i 
									? 'bg-datadog-purple text-white shadow-lg' 
									: currentStep > i
										? 'bg-datadog-green/10 text-datadog-green hover:bg-datadog-green/20'
										: 'hover:bg-muted text-muted-foreground'}"
							on:click={() => goToStep(i)}
						>
							<span class="text-lg">{currentStep > i ? '✓' : step.icon}</span>
							<div>
								<div class="font-medium text-sm">{step.title}</div>
								<div class="text-xs opacity-70">{step.description}</div>
							</div>
						</button>
					{/each}
				</div>
			</div>

			<!-- Mobile Step Indicator -->
			<div class="lg:hidden border-b border-border p-4 bg-muted/30">
				<div class="flex items-center justify-between">
					<span class="text-sm font-medium">
						Step {currentStep + 1} of {steps.length}: {steps[currentStep].title}
					</span>
					<div class="flex gap-1">
						{#each steps as _, i}
							<button
								type="button"
								class="w-2.5 h-2.5 rounded-full transition-all {i === currentStep ? 'bg-datadog-purple w-6' : i < currentStep ? 'bg-datadog-green' : 'bg-muted-foreground/30'}"
								on:click={() => goToStep(i)}
							/>
						{/each}
					</div>
				</div>
			</div>

			<!-- CENTER: Current Step Content -->
			<div class="p-6 min-h-[420px] flex flex-col">
				{#key currentStep}
					<div in:fade={{ duration: 150 }} class="flex-1">
						
						<!-- Step 0: Volume -->
						{#if currentStep === 0}
							<div class="space-y-6">
								<div>
									<h3 class="text-lg font-semibold mb-1 flex items-center gap-2">
										<span>📊</span> Log Volume
									</h3>
									<p class="text-sm text-muted-foreground">Tell us about your log ingestion</p>
								</div>

								<div class="space-y-5">
									<div class="space-y-2">
										<label for="ingestedLogs" class="text-sm font-medium">
											How many GB of logs do you ingest per month?
										</label>
										<div class="flex items-center gap-3">
											<Input 
												id="ingestedLogs"
												type="number" 
												bind:value={ingestedLogsGB} 
												min="1" 
												class="font-mono text-lg w-32"
											/>
											<span class="text-muted-foreground">GB / month</span>
										</div>
									</div>

									<div class="space-y-2">
										<label for="avgLogSize" class="text-sm font-medium">
											What's the average size of a single log entry?
										</label>
										<div class="flex items-center gap-3">
											<Input 
												id="avgLogSize"
												type="number" 
												bind:value={avgLogSizeKB} 
												min="0.1" 
												step="0.1"
												class="font-mono text-lg w-32"
											/>
											<span class="text-muted-foreground">KB per log</span>
										</div>
										<p class="text-xs text-muted-foreground">
											Typical: JSON logs ~1-2KB, simple text ~0.5KB
										</p>
									</div>
								</div>

								<div class="rounded-lg bg-datadog-blue/5 border border-datadog-blue/20 p-4">
									<div class="text-sm font-medium text-datadog-blue">📈 That's approximately</div>
									<div class="text-2xl font-bold font-mono mt-1">
										{formatNumber(Math.round(totalLogsPerMonth))}
									</div>
									<div class="text-sm text-muted-foreground">log entries per month</div>
								</div>
							</div>

						<!-- Step 1: Retention -->
						{:else if currentStep === 1}
							<div class="space-y-6">
								<div>
									<h3 class="text-lg font-semibold mb-1 flex items-center gap-2">
										<span>📅</span> Retention Period
									</h3>
									<p class="text-sm text-muted-foreground">How long should indexed logs be searchable?</p>
								</div>

								<div class="grid grid-cols-2 gap-3">
									{#each retentionOptions as option}
										<button
											type="button"
											class="p-5 rounded-xl border-2 text-center transition-all
												{retentionDays === option.days 
													? 'border-datadog-purple bg-datadog-purple/10 ring-2 ring-datadog-purple/50' 
													: 'border-border hover:border-datadog-purple/50 hover:bg-muted/50'}"
											on:click={() => retentionDays = option.days}
										>
											<div class="text-3xl mb-2">{option.emoji}</div>
											<div class="font-bold">{option.label}</div>
											<div class="text-xs text-muted-foreground">{option.description}</div>
										</button>
									{/each}
								</div>

								<div class="text-sm text-muted-foreground flex items-center gap-2">
									<span>💡</span>
									<span>Longer retention = higher cost per indexed log</span>
								</div>
							</div>

						<!-- Step 2: Indexing -->
						{:else if currentStep === 2}
							<div class="space-y-6">
								<div>
									<h3 class="text-lg font-semibold mb-1 flex items-center gap-2">
										<span>🔍</span> Indexing Strategy
									</h3>
									<p class="text-sm text-muted-foreground">What percentage of logs do you need to search?</p>
								</div>

								<div class="grid grid-cols-2 gap-3">
									{#each useCasePresets as preset}
										<button
											type="button"
											class="p-4 rounded-xl border-2 text-left transition-all
												{indexingPercentage === preset.percentage 
													? 'border-datadog-green bg-datadog-green/10' 
													: 'border-border hover:border-datadog-green/50'}"
											on:click={() => indexingPercentage = preset.percentage}
										>
											<div class="flex items-center gap-2 mb-1">
												<span class="text-xl">{preset.emoji}</span>
												<span class="font-bold">{preset.name}</span>
												<Badge variant="outline" class="ml-auto">{preset.percentage}%</Badge>
											</div>
											<div class="text-xs text-muted-foreground">{preset.description}</div>
										</button>
									{/each}
								</div>

								<div class="space-y-2">
									<div class="flex justify-between text-sm">
										<span>Or set custom percentage</span>
										<span class="font-mono font-bold text-datadog-purple">{indexingPercentage}%</span>
									</div>
									<input 
										type="range" 
										bind:value={indexingPercentage} 
										min="1" 
										max="100" 
										class="w-full accent-datadog-purple h-2"
									/>
								</div>

								<div class="rounded-lg bg-datadog-purple/5 border border-datadog-purple/20 p-4">
									<div class="text-sm">You'll index</div>
									<div class="text-2xl font-bold font-mono text-datadog-purple">
										{formatNumber(Math.round(indexedLogsCount))} logs
									</div>
									<div class="text-sm text-muted-foreground">
										({indexedLogsInMillions.toFixed(2)} million events)
									</div>
								</div>
							</div>

						<!-- Step 3: Extras -->
						{:else if currentStep === 3}
							<div class="space-y-5">
								<div>
									<h3 class="text-lg font-semibold mb-1 flex items-center gap-2">
										<span>⚡</span> Additional Options
									</h3>
									<p class="text-sm text-muted-foreground">Optional features for advanced use cases</p>
								</div>

								<div class="space-y-3">
									<!-- Flex Starter -->
									<label
										class="flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all
											{enableFlexStarter ? 'border-datadog-blue bg-datadog-blue/5' : 'border-border hover:border-muted-foreground'}"
									>
										<input 
											type="checkbox" 
											bind:checked={enableFlexStarter}
											class="mt-1 h-5 w-5 rounded accent-datadog-blue"
										/>
										<div class="flex-1">
											<div class="font-medium">Flex Logs Starter</div>
											<div class="text-xs text-muted-foreground">Query archived logs cost-effectively</div>
											{#if enableFlexStarter}
												<div class="mt-2 flex items-center gap-2" transition:slide={{ duration: 150 }}>
													<Input 
														type="number" 
														bind:value={flexStarterEvents} 
														min="1" 
														class="w-24 font-mono"
													/>
													<span class="text-sm text-muted-foreground">M events</span>
													{#if flexStarterPrice > 0}
														<span class="text-xs text-datadog-blue ml-auto">{formatCurrency(flexStarterCost)}/mo</span>
													{/if}
												</div>
											{/if}
										</div>
									</label>

									<!-- Flex Storage -->
									<label
										class="flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all
											{enableFlexStorage ? 'border-datadog-blue bg-datadog-blue/5' : 'border-border hover:border-muted-foreground'}"
									>
										<input 
											type="checkbox" 
											bind:checked={enableFlexStorage}
											class="mt-1 h-5 w-5 rounded accent-datadog-blue"
										/>
										<div class="flex-1">
											<div class="font-medium">Flex Logs Storage</div>
											<div class="text-xs text-muted-foreground">Long-term storage for compliance</div>
											{#if enableFlexStorage}
												<div class="mt-2 flex items-center gap-2" transition:slide={{ duration: 150 }}>
													<Input 
														type="number" 
														bind:value={flexStorageEvents} 
														min="1" 
														class="w-24 font-mono"
													/>
													<span class="text-sm text-muted-foreground">M events</span>
													{#if flexStoragePrice > 0}
														<span class="text-xs text-datadog-blue ml-auto">{formatCurrency(flexStorageCost)}/mo</span>
													{/if}
												</div>
											{/if}
										</div>
									</label>

									<!-- Forwarding -->
									<label
										class="flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all
											{enableForwarding ? 'border-datadog-orange bg-datadog-orange/5' : 'border-border hover:border-muted-foreground'}"
									>
										<input 
											type="checkbox" 
											bind:checked={enableForwarding}
											class="mt-1 h-5 w-5 rounded accent-datadog-orange"
										/>
										<div class="flex-1">
											<div class="font-medium">Log Forwarding</div>
											<div class="text-xs text-muted-foreground">Forward to S3, Azure, GCS</div>
											{#if enableForwarding}
												<div class="mt-2 flex items-center gap-2" transition:slide={{ duration: 150 }}>
													<Input 
														type="number" 
														bind:value={forwardingGB} 
														min="1" 
														class="w-24 font-mono"
													/>
													<span class="text-sm text-muted-foreground">GB/month</span>
													{#if forwardingPrice > 0}
														<span class="text-xs text-datadog-orange ml-auto">{formatCurrency(forwardingCost)}/mo</span>
													{/if}
												</div>
											{/if}
										</div>
									</label>
								</div>

								<p class="text-xs text-muted-foreground text-center">
									Skip these options if you don't need them
								</p>
							</div>
						{/if}
					</div>
				{/key}

				<!-- Navigation Buttons -->
				<div class="flex justify-between mt-6 pt-4 border-t border-border">
					<Button 
						variant="outline" 
						on:click={prevStep}
						disabled={currentStep === 0}
						class="gap-2"
					>
						<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M19 12H5M12 19l-7-7 7-7"/>
						</svg>
						Back
					</Button>
					
					{#if currentStep < steps.length - 1}
						<Button 
							class="bg-datadog-purple hover:bg-datadog-purple/90 gap-2"
							on:click={nextStep}
						>
							Next
							<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M5 12h14M12 5l7 7-7 7"/>
							</svg>
						</Button>
					{:else}
						<Button 
							class="bg-datadog-green hover:bg-datadog-green/90 gap-2"
							on:click={addToQuote}
							disabled={!ingestionProduct || !indexedProduct}
						>
							<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M5 13l4 4L19 7"/>
							</svg>
							Add to Quote
						</Button>
					{/if}
				</div>
			</div>

			<!-- RIGHT: Always-Visible Summary -->
			<div class="border-t lg:border-t-0 lg:border-l border-border bg-gradient-to-b from-muted/50 to-background p-4">
				<div class="lg:sticky lg:top-4 space-y-4">
					<h4 class="font-semibold text-xs uppercase tracking-wide text-muted-foreground flex items-center gap-2">
						<span>💰</span> Cost Summary
					</h4>

					<!-- Quick Stats -->
					<div class="space-y-2 text-sm">
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Volume</span>
							<span class="font-mono font-medium">{ingestedLogsGB} GB</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Retention</span>
							<span class="font-mono font-medium">{retentionDays} days</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Indexing</span>
							<span class="font-mono font-medium">{indexingPercentage}%</span>
						</div>
						<div class="flex justify-between items-center">
							<span class="text-muted-foreground">Indexed logs</span>
							<span class="font-mono text-xs">{indexedLogsInMillions.toFixed(1)}M</span>
						</div>
					</div>

					<hr class="border-border" />

					<!-- Cost Breakdown -->
					<div class="space-y-2 text-sm">
						<div class="flex justify-between">
							<div class="flex items-center gap-2">
								<div class="w-2 h-2 rounded bg-datadog-blue"></div>
								<span>Ingestion</span>
							</div>
							<span class="font-mono">{formatCurrency(ingestionCost)}</span>
						</div>
						<div class="flex justify-between">
							<div class="flex items-center gap-2">
								<div class="w-2 h-2 rounded bg-datadog-purple"></div>
								<span>Indexed</span>
							</div>
							<span class="font-mono">{formatCurrency(indexedCost)}</span>
						</div>
						{#if additionalCost > 0}
							<div class="flex justify-between text-datadog-green">
								<div class="flex items-center gap-2">
									<div class="w-2 h-2 rounded bg-datadog-green"></div>
									<span>Extras</span>
								</div>
								<span class="font-mono">{formatCurrency(additionalCost)}</span>
							</div>
						{/if}
					</div>

					<hr class="border-border" />

					<!-- Total -->
					<div class="rounded-xl bg-datadog-green/10 border border-datadog-green/30 p-4 text-center">
						<div class="text-xs text-muted-foreground">Monthly Total</div>
						<div class="text-2xl font-bold font-mono text-datadog-green">
							{formatCurrency(totalMonthlyCost)}
						</div>
						<div class="text-xs text-muted-foreground">
							~{formatCurrency(totalMonthlyCost * 12)}/year
						</div>
					</div>

					<!-- Cost Visualization Bar -->
					{#if totalMonthlyCost > 0}
						<div class="space-y-1">
							<div class="h-3 rounded-full overflow-hidden bg-muted flex">
								<div 
									class="bg-datadog-blue transition-all duration-300" 
									style="width: {(ingestionCost / totalMonthlyCost) * 100}%"
								></div>
								<div 
									class="bg-datadog-purple transition-all duration-300" 
									style="width: {(indexedCost / totalMonthlyCost) * 100}%"
								></div>
								{#if additionalCost > 0}
									<div 
										class="bg-datadog-green transition-all duration-300" 
										style="width: {(additionalCost / totalMonthlyCost) * 100}%"
									></div>
								{/if}
							</div>
						</div>
					{/if}

					<!-- Progress -->
					<div class="space-y-2 pt-2">
						<div class="text-xs text-muted-foreground">Progress</div>
						<div class="h-1.5 rounded-full bg-muted overflow-hidden">
							<div 
								class="h-full bg-datadog-purple transition-all duration-300"
								style="width: {((currentStep + 1) / steps.length) * 100}%"
							></div>
						</div>
						<div class="text-xs text-center text-muted-foreground">
							Step {currentStep + 1} of {steps.length}
						</div>
					</div>

					{#if !ingestionProduct || !indexedProduct}
						<p class="text-xs text-center text-amber-600 bg-amber-50 rounded-lg p-2">
							⚠️ Some products not found. Sync pricing data.
						</p>
					{/if}
				</div>
			</div>
		</div>
	</CardContent>
</Card>
