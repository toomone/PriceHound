<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { slide } from 'svelte/transition';
	import ProductSearch from './ProductSearch.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { formatCurrency, parsePrice, formatNumber, isPercentagePrice, parsePercentage } from '$lib/utils';
	import type { Product, Allotment, QuantityBreakdownLine } from '$lib/api';

	interface AllotmentItem {
		product: Product | null;
		includedQuantity: number;
		allotmentInfo: Allotment | null;
	}

	interface QuantityLineLocal {
		id: string;
		label: string;
		quantity: number;
	}

	export let products: Product[] = [];
	export let selectedProduct: Product | null = null;
	export let quantity: number = 1;
	export let index: number = 0;
	export let showAnnual: boolean = true;
	export let showMonthly: boolean = true;
	export let showOnDemand: boolean = true;
	export let isAllotment: boolean = false;
	export let includedQuantity: number = 0;
	export let allotmentInfo: Allotment | null = null;
	export let totalAllottedForProduct: number = 0;
	export let lineAllotments: AllotmentItem[] = [];
	export let hideCategory: boolean = false;
	export let isGrouped: boolean = false;
	export let searchId: string | undefined = undefined;
	export let negotiatedPrice: number | null = null;
	export let quantityBreakdown: QuantityLineLocal[] = [];
	export let showBreakdown: boolean = false;
	
	let showNegotiatedInput = negotiatedPrice !== null && negotiatedPrice > 0;
	$: if (negotiatedPrice === null || negotiatedPrice === undefined) showNegotiatedInput = false;

	$: hasBreakdown = quantityBreakdown.length > 0;
	$: breakdownSum = quantityBreakdown.reduce((s, bl) => s + bl.quantity, 0);

	const dispatch = createEventDispatcher<{
		update: { product: Product | null; quantity: number; negotiatedPrice?: number | null };
		remove: void;
		updateBreakdown: { breakdown: QuantityLineLocal[] };
	}>();

	function initBreakdown() {
		const initial: QuantityLineLocal[] = [{ id: crypto.randomUUID(), label: 'base', quantity }];
		dispatch('updateBreakdown', { breakdown: initial });
	}

	function addBreakdownLine() {
		const updated = [...quantityBreakdown, { id: crypto.randomUUID(), label: '', quantity: 0 }];
		dispatch('updateBreakdown', { breakdown: updated });
	}

	function removeBreakdownLine(lineId: string) {
		const updated = quantityBreakdown.filter(bl => bl.id !== lineId);
		if (updated.length === 0) {
			dispatch('updateBreakdown', { breakdown: [] });
		} else {
			dispatch('updateBreakdown', { breakdown: updated });
		}
	}

	function handleBreakdownChange() {
		dispatch('updateBreakdown', { breakdown: quantityBreakdown });
	}

	// Check if this product uses percentage-based pricing
	$: isPercentageBased = selectedProduct ? isPercentagePrice(selectedProduct.billed_annually) : false;

	// Calculate all 3 prices (or percentages)
	$: annualPrice = selectedProduct ? parsePrice(selectedProduct.billed_annually) : 0;
	$: monthlyPrice = selectedProduct ? parsePrice(selectedProduct.billed_month_to_month) : 0;
	$: onDemandPrice = selectedProduct ? parsePrice(selectedProduct.on_demand) : 0;

	// For percentage-based pricing, get the percentage values
	$: annualPercent = selectedProduct ? parsePercentage(selectedProduct.billed_annually) : 0;
	$: monthlyPercent = selectedProduct ? parsePercentage(selectedProduct.billed_month_to_month) : 0;
	$: onDemandPercent = selectedProduct ? parsePercentage(selectedProduct.on_demand) : 0;

	// Negotiated price handling (annual only)
	$: hasNegotiatedPrice = negotiatedPrice !== null && negotiatedPrice > 0;
	$: effectiveAnnualPrice = hasNegotiatedPrice ? negotiatedPrice! : annualPrice;

	// For allotments, only charge for quantity exceeding the included amount
	$: chargeableQuantity = isAllotment ? Math.max(0, quantity - includedQuantity) : quantity;

	// Calculate totals for all 3 (only for chargeable quantity)
	// For percentage items, the "total" shown is just the percentage - actual calculation done in summary
	// For annual, use negotiated price if available
	$: annualTotal = isPercentageBased ? annualPercent : effectiveAnnualPrice * chargeableQuantity;
	$: monthlyTotal = isPercentageBased ? monthlyPercent : monthlyPrice * chargeableQuantity;
	$: onDemandTotal = isPercentageBased ? onDemandPercent : onDemandPrice * chargeableQuantity;

	$: visibleColumns = [showAnnual, showMonthly, showOnDemand].filter(Boolean).length;

	function handleProductSelect(event: CustomEvent<Product>) {
		selectedProduct = event.detail;
		// Reset negotiated price when product changes
		negotiatedPrice = null;
		showNegotiatedInput = false;
		dispatch('update', { product: selectedProduct, quantity, negotiatedPrice: null });
	}

	function handleQuantityChange() {
		dispatch('update', { product: selectedProduct, quantity, negotiatedPrice });
	}
	
	function handleNegotiatedPriceChange() {
		dispatch('update', { product: selectedProduct, quantity, negotiatedPrice });
	}
	
	function toggleNegotiatedPrice() {
		showNegotiatedInput = !showNegotiatedInput;
		if (!showNegotiatedInput) {
			negotiatedPrice = null;
			dispatch('update', { product: selectedProduct, quantity, negotiatedPrice: null });
		}
	}

	function handleRemove() {
		dispatch('remove');
	}
</script>

{#if isAllotment}
	<!-- Compact Allotment Line (read-only) -->
	<div
		class="relative rounded-lg border border-datadog-green/20 bg-datadog-green/5 px-4 py-2 ml-8"
		style="animation: slideIn 0.3s ease-out {index * 0.05}s both;"
	>
		<div class="absolute -left-6 top-1/2 -translate-y-1/2 text-datadog-green/50">
			<svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M9 18l6-6-6-6" />
			</svg>
		</div>

		<div class="flex items-center gap-4">
			<!-- Product Name -->
			<div class="flex-1 min-w-0 flex items-center gap-2">
				<span class="text-sm text-muted-foreground truncate">
					{selectedProduct?.product || 'Unknown product'}
				</span>
				<Badge variant="outline" class="text-[9px] px-1.5 py-0 bg-datadog-green/10 text-datadog-green border-datadog-green/30 shrink-0">
					Allotment
				</Badge>
			</div>

			<!-- Included Quantity -->
			<div class="text-xs text-muted-foreground shrink-0">
				{formatNumber(includedQuantity)} {allotmentInfo?.allotted_unit || 'units'}
			</div>
		</div>
	</div>
{:else}
	<!-- Regular Product Line -->
	<div
		class="group relative p-4 transition-all {isGrouped ? 'bg-transparent hover:bg-muted/30' : 'rounded-xl border border-border/50 bg-card/50 hover:border-foreground/20 hover:bg-card/80'}"
		style="animation: slideIn 0.3s ease-out {index * 0.05}s both;"
	>
		<!-- Category Label (hidden when grouped) -->
		{#if selectedProduct?.category && !hideCategory}
			<div class="absolute -top-3 left-4 z-10">
				<span class="inline-flex items-center px-2.5 py-1 rounded text-[11px] font-medium bg-zinc-200 dark:bg-zinc-700 text-foreground/80 border border-foreground/20 shadow-sm whitespace-nowrap">
					{selectedProduct.category}
				</span>
			</div>
		{/if}

		<div class="flex flex-col gap-4 lg:flex-row lg:items-start">
			<!-- Product Search -->
			<div class="flex-1 min-w-0">
				<div class="mb-1.5 h-4"></div>
				<ProductSearch {products} {selectedProduct} id={searchId} on:select={handleProductSelect} />
				{#if selectedProduct}
					<div class="mt-2 flex items-center gap-2 flex-wrap">
						<span class="inline-flex items-center px-2 py-0.5 rounded-sm text-xs text-muted-foreground bg-zinc-100 dark:bg-zinc-800">
							{selectedProduct.billing_unit}
						</span>
						<!-- Negotiated price toggle (small switch) -->
						{#if !isPercentageBased}
							<button
								type="button"
								class="w-4 h-4 rounded-sm border transition-all flex items-center justify-center {showNegotiatedInput ? 'bg-amber-500 border-amber-500' : 'border-muted-foreground/30 hover:border-amber-400 hover:bg-amber-50 dark:hover:bg-amber-950'}"
								title="Set negotiated price (annual billing only)"
								on:click={toggleNegotiatedPrice}
							>
								{#if showNegotiatedInput}
									<svg class="w-2.5 h-2.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
										<path d="M5 13l4 4L19 7" />
									</svg>
								{/if}
							</button>
						{/if}
						<!-- Negotiated price input (when enabled) -->
						{#if showNegotiatedInput && !isPercentageBased}
							<div class="flex items-center gap-1">
								<span class="text-xs text-amber-600 dark:text-amber-400">$</span>
								<input
									type="number"
									step="0.01"
									min="0"
									bind:value={negotiatedPrice}
									placeholder={annualPrice.toFixed(2)}
									class="w-20 h-6 px-1.5 text-xs rounded border border-amber-300 dark:border-amber-600 bg-amber-50 dark:bg-amber-950 text-amber-800 dark:text-amber-200 focus:ring-1 focus:ring-amber-500 focus:outline-none"
									on:change={handleNegotiatedPriceChange}
								/>
								<span class="text-[10px] text-amber-600/70 dark:text-amber-400/70">/unit</span>
							</div>
						{/if}
						<!-- Detail volume breakdown button -->
						{#if !hasBreakdown && !isAllotment}
							<button
								type="button"
								class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] text-muted-foreground/60 hover:text-datadog-purple hover:bg-datadog-purple/5 border border-transparent hover:border-datadog-purple/20 transition-all"
								title="Break down quantity by env, team, etc."
								on:click={initBreakdown}
							>
								<svg class="h-2.5 w-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" /></svg>
								detail volume
							</button>
						{/if}
					</div>
				{/if}
			</div>

			<!-- Quantity -->
			<div class="w-24 shrink-0">
				<div class="mb-1.5 h-4"></div>
				{#if hasBreakdown}
					<div
						class="flex h-10 w-full items-center justify-center rounded-lg border border-dashed border-input bg-muted/30 px-3 py-2 text-sm text-center font-mono text-muted-foreground"
						title="Sum of {quantityBreakdown.length} breakdown lines"
					>
						{breakdownSum}
					</div>
				{:else}
					<input
						type="number"
						min="1"
						bind:value={quantity}
						on:change={handleQuantityChange}
						class="flex h-10 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-center font-mono ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200"
					/>
				{/if}
				{#if totalAllottedForProduct > 0}
					<div class="mt-1 text-[10px] text-center text-datadog-green">
						+ {formatNumber(totalAllottedForProduct)} included
					</div>
				{/if}
			</div>

			<!-- Price Columns -->
			<div class="flex gap-2" style="width: {visibleColumns * 110}px;">
				{#if showAnnual}
					<div class="flex-1 text-center min-w-[100px]">
						<span class="mb-1.5 block text-xs font-medium {hasNegotiatedPrice ? 'text-amber-600 dark:text-amber-400' : 'text-datadog-green'}">
							{hasNegotiatedPrice ? 'Negotiated' : 'Annually'}
						</span>
						<div class="rounded-lg {hasNegotiatedPrice ? 'bg-amber-500/10 border-amber-500/20' : 'bg-datadog-green/10 border-datadog-green/20'} border px-2 py-2">
							<div class="font-mono text-sm font-semibold {hasNegotiatedPrice ? 'text-amber-600 dark:text-amber-400' : 'text-datadog-green'} truncate">
								{#if !selectedProduct}
									-
								{:else if isPercentageBased}
									{annualPercent}%
								{:else}
									{formatCurrency(annualTotal)}<span class="text-[10px] font-normal opacity-60">/mo</span>
								{/if}
							</div>
							{#if selectedProduct && !isPercentageBased && effectiveAnnualPrice > 0}
								<div class="font-mono text-[10px] {hasNegotiatedPrice ? 'text-amber-600/60 dark:text-amber-400/60' : 'text-datadog-green/60'} mt-0.5">
									{formatCurrency(effectiveAnnualPrice)}/unit
									{#if hasNegotiatedPrice}
										<span class="line-through opacity-50 ml-1">{formatCurrency(annualPrice)}</span>
									{/if}
								</div>
							{:else if selectedProduct && isPercentageBased}
								<div class="font-mono text-[10px] text-datadog-green/60 mt-0.5">
									of total
								</div>
							{/if}
						</div>
					</div>
				{/if}

				{#if showMonthly}
					<div class="flex-1 text-center min-w-[100px]">
						<span class="mb-1.5 block text-xs font-medium text-datadog-blue">Monthly</span>
						<div class="rounded-lg bg-datadog-blue/10 border border-datadog-blue/20 px-2 py-2">
							<div class="font-mono text-sm font-semibold text-datadog-blue truncate">
								{#if !selectedProduct}
									-
								{:else if isPercentageBased}
									{monthlyPercent}%
								{:else}
									{formatCurrency(monthlyTotal)}<span class="text-[10px] font-normal opacity-60">/mo</span>
								{/if}
							</div>
							{#if selectedProduct && !isPercentageBased && monthlyPrice > 0}
								<div class="font-mono text-[10px] text-datadog-blue/60 mt-0.5">
									{formatCurrency(monthlyPrice)}/unit
								</div>
							{:else if selectedProduct && isPercentageBased}
								<div class="font-mono text-[10px] text-datadog-blue/60 mt-0.5">
									of total
								</div>
							{/if}
						</div>
					</div>
				{/if}

				{#if showOnDemand}
					<div class="flex-1 text-center min-w-[100px]">
						<span class="mb-1.5 block text-xs font-medium text-datadog-orange">On-Demand</span>
						<div class="rounded-lg bg-datadog-orange/10 border border-datadog-orange/20 px-2 py-2">
							<div class="font-mono text-sm font-semibold text-datadog-orange truncate">
								{#if !selectedProduct}
									-
								{:else if isPercentageBased}
									{onDemandPercent}%
								{:else}
									{formatCurrency(onDemandTotal)}<span class="text-[10px] font-normal opacity-60">/mo</span>
								{/if}
							</div>
							{#if selectedProduct && !isPercentageBased && onDemandPrice > 0}
								<div class="font-mono text-[10px] text-datadog-orange/60 mt-0.5">
									{formatCurrency(onDemandPrice)}/unit
								</div>
							{:else if selectedProduct && isPercentageBased}
								<div class="font-mono text-[10px] text-datadog-orange/60 mt-0.5">
									of total
								</div>
							{/if}
						</div>
					</div>
				{/if}
			</div>

			<!-- Remove Button -->
			<div class="absolute -right-2 -top-2 lg:relative lg:right-auto lg:top-auto lg:self-center lg:ml-2">
				<div class="mb-1.5 h-4 hidden lg:block"></div>
				<Button
					variant="ghost"
					size="icon"
					class="h-8 w-8 rounded-full text-muted-foreground/40 transition-all hover:bg-destructive hover:text-white group-hover:bg-destructive/10 group-hover:text-destructive"
					on:click={handleRemove}
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6" />
					</svg>
				</Button>
			</div>
		</div>

		<!-- Quantity Breakdown -->
		{#if hasBreakdown && showBreakdown}
			<div class="mt-3 pt-3 border-t border-border/30" transition:slide={{ duration: 150 }}>
				<div class="space-y-1 pl-4">
					{#each quantityBreakdown as bl (bl.id)}
						<div class="flex items-center group/bl">
							<div class="flex-1 min-w-0 flex items-center gap-2">
								<span class="w-1 h-1 rounded-full bg-datadog-purple/40 shrink-0"></span>
								<input
									type="text"
									bind:value={bl.label}
									on:change={handleBreakdownChange}
									on:input={() => { bl.label = bl.label.replace(/[<>"'`;]/g, ''); }}
									placeholder="env, team..."
									maxlength="50"
									class="h-6 w-40 border-0 border-b border-border/50 bg-transparent px-0.5 text-xs placeholder:text-muted-foreground/40 focus:outline-none focus:border-datadog-purple"
								/>
								<button
									type="button"
									class="h-4 w-4 shrink-0 flex items-center justify-center rounded text-muted-foreground/20 hover:text-destructive hover:bg-destructive/10 opacity-0 group-hover/bl:opacity-100 transition-all"
									title="Remove this breakdown line"
									on:click={() => removeBreakdownLine(bl.id)}
								>
									<svg class="h-2.5 w-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
								</button>
							</div>
							<div class="w-24 shrink-0">
								<input
									type="number"
									min="0"
									bind:value={bl.quantity}
									on:change={handleBreakdownChange}
									class="h-6 w-full border-0 border-b border-border/50 bg-transparent px-1 text-xs text-center font-mono focus:outline-none focus:border-datadog-purple"
								/>
							</div>
						</div>
					{/each}
					<div class="flex items-center pl-3">
						<button
							type="button"
							class="flex items-center gap-1 text-[10px] text-muted-foreground/50 hover:text-datadog-purple transition-colors"
							on:click={addBreakdownLine}
						>
							<svg class="h-2.5 w-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14" /></svg>
							Add line
						</button>
					</div>
				</div>
			</div>
		{/if}

		<!-- Included Allotments (inside product card) -->
		{#if lineAllotments.length > 0}
			<div class="mt-3 pt-3 border-t border-border/30">
				<div class="flex items-center gap-2 mb-1.5">
					<svg class="w-3.5 h-3.5 text-muted-foreground/70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
					</svg>
					<span class="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-wide">Included Allotments</span>
				</div>
				<ul class="space-y-0.5 pl-5">
					{#each lineAllotments as allotment}
						<li class="flex items-center gap-2 text-xs text-muted-foreground">
							<span class="w-1 h-1 rounded-full bg-muted-foreground/40"></span>
							<span><strong>{allotment.product?.product || 'Unknown'}</strong>: {formatNumber(allotment.includedQuantity || 0)} {allotment.allotmentInfo?.allotted_unit || 'units'}</span>
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	</div>
{/if}

<style>
	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}
</style>
