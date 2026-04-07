<script lang="ts">
	import { PieChart } from 'layerchart';
	import { formatCurrency, parsePrice, isPercentagePrice } from '$lib/utils';
	import type { Product } from '$lib/api';

	interface QuantityLine {
		id: string;
		label: string;
		quantity: number;
	}

	interface LineItem {
		id: string;
		product: Product | null;
		quantity: number;
		negotiatedPrice?: number | null;
		isAllotment?: boolean;
		quantityBreakdown?: QuantityLine[];
	}

	export let lines: LineItem[] = [];
	export let billingType: 'annually' | 'monthly' | 'on_demand' = 'annually';

	// Color palette for categories
	const categoryColors: Record<string, string> = {
		'APM': 'hsl(262, 83%, 58%)', // Purple (Datadog purple)
		'Log Management': 'hsl(142, 76%, 36%)', // Green
		'Infrastructure': 'hsl(217, 91%, 60%)', // Blue
		'RUM & Session Replay': 'hsl(25, 95%, 53%)', // Orange
		'Synthetics': 'hsl(340, 82%, 52%)', // Pink
		'Database Monitoring': 'hsl(47, 96%, 53%)', // Yellow
		'Network Monitoring': 'hsl(199, 89%, 48%)', // Cyan
		'Security': 'hsl(0, 72%, 51%)', // Red
		'CI/CD': 'hsl(271, 91%, 65%)', // Violet
		'Serverless': 'hsl(160, 84%, 39%)', // Teal
	};

	// Default color for unknown categories
	const defaultColors = [
		'hsl(215, 20%, 65%)',
		'hsl(215, 20%, 55%)',
		'hsl(215, 20%, 45%)',
		'hsl(215, 20%, 35%)',
	];

	function getCategoryColor(category: string, index: number): string {
		return categoryColors[category] || defaultColors[index % defaultColors.length];
	}

	function getPriceField(product: Product): string {
		switch (billingType) {
			case 'annually': return product.billed_annually;
			case 'monthly': return product.billed_month_to_month;
			case 'on_demand': return product.on_demand;
		}
	}

	// Calculate costs grouped by category
	$: categoryData = (() => {
		const categories: Record<string, { cost: number; products: string[] }> = {};
		
		for (const line of lines) {
			if (!line.product || line.isAllotment) continue;
			
			const category = line.product.category || 'Other';
			const priceStr = getPriceField(line.product);
			
			// Skip percentage-based pricing for now
			if (isPercentagePrice(priceStr)) continue;
			
			const price = parsePrice(priceStr);
			const lineCost = price * line.quantity;
			
			if (!categories[category]) {
				categories[category] = { cost: 0, products: [] };
			}
			categories[category].cost += lineCost;
			if (!categories[category].products.includes(line.product.product)) {
				categories[category].products.push(line.product.product);
			}
		}
		
		return categories;
	})();

	// Convert to chart data format
	$: chartData = (() => {
		const data = Object.entries(categoryData)
			.filter(([_, v]) => v.cost > 0)
			.map(([category, data], index) => ({
				category,
				cost: data.cost * 12, // Annual cost
				products: data.products,
				color: getCategoryColor(category, index),
			}))
			.sort((a, b) => b.cost - a.cost);
		
		return data;
	})();

	// Calculate total for percentages
	$: totalCost = chartData.reduce((sum, d) => sum + d.cost, 0);

	// Create a unique key based on the data to force re-render
	$: chartKey = chartData.map(d => `${d.category}:${d.cost}`).join('|');

	// Legend items
	$: legendItems = chartData.map(d => ({
		name: d.category,
		color: d.color,
		percentage: totalCost > 0 ? (d.cost / totalCost) * 100 : 0,
		value: formatCurrency(d.cost),
	}));

	// Label-based breakdown chart
	const labelColors = [
		'hsl(262, 83%, 58%)',
		'hsl(217, 91%, 60%)',
		'hsl(142, 76%, 36%)',
		'hsl(25, 95%, 53%)',
		'hsl(340, 82%, 52%)',
		'hsl(47, 96%, 53%)',
		'hsl(199, 89%, 48%)',
		'hsl(0, 72%, 51%)',
		'hsl(271, 91%, 65%)',
		'hsl(160, 84%, 39%)',
	];

	$: hasBreakdownLines = lines.some(l => l.quantityBreakdown && l.quantityBreakdown.length > 0);

	$: labelData = (() => {
		if (!hasBreakdownLines) return [];
		const labels: Record<string, number> = {};

		for (const line of lines) {
			if (!line.product || line.isAllotment || !line.quantityBreakdown?.length) continue;

			const priceStr = getPriceField(line.product);
			if (isPercentagePrice(priceStr)) continue;

			const unitPrice = line.negotiatedPrice != null && line.negotiatedPrice > 0 && billingType === 'annually'
				? line.negotiatedPrice
				: parsePrice(priceStr);

			for (const bl of line.quantityBreakdown) {
				const lbl = bl.label || 'unlabeled';
				labels[lbl] = (labels[lbl] || 0) + unitPrice * bl.quantity;
			}
		}

		return Object.entries(labels)
			.filter(([_, cost]) => cost > 0)
			.map(([label, cost], i) => ({
				label,
				cost: cost * 12,
				color: labelColors[i % labelColors.length],
			}))
			.sort((a, b) => b.cost - a.cost);
	})();

	$: labelTotalCost = labelData.reduce((s, d) => s + d.cost, 0);
	$: labelChartKey = labelData.map(d => `${d.label}:${d.cost}`).join('|');
	$: labelLegendItems = labelData.map(d => ({
		name: d.label,
		color: d.color,
		percentage: labelTotalCost > 0 ? (d.cost / labelTotalCost) * 100 : 0,
		value: formatCurrency(d.cost),
	}));
</script>

{#if chartData.length > 0}
	<div
		class="grid {hasBreakdownLines && labelData.length > 0
			? 'grid-cols-1 md:grid-cols-2 gap-4 md:gap-5'
			: 'grid-cols-1'}"
	>
		<!-- Cost by Category -->
		<div class="min-w-0">
			<div class="flex flex-col sm:flex-row items-center gap-3 sm:gap-4">
				<div class="w-[148px] h-[148px] sm:w-[160px] sm:h-[160px] shrink-0 relative">
					{#key chartKey}
						<PieChart
							data={chartData}
							key="category"
							value="cost"
							c="color"
							innerRadius={0.6}
							legend={false}
						/>
					{/key}
					<div class="absolute inset-0 flex items-center justify-center pointer-events-none">
						<div class="text-center px-1">
							<div class="text-sm sm:text-base font-bold leading-tight">{formatCurrency(totalCost)}</div>
							<div class="text-[10px] sm:text-xs text-muted-foreground">/year</div>
						</div>
					</div>
				</div>
				<div class="flex-1 min-w-0 w-full">
					<div class="flex flex-col gap-1.5 text-sm">
						{#each legendItems as item}
							<div class="flex items-center gap-2">
								<div class="h-3 w-3 rounded-sm shrink-0" style="background-color: {item.color}"></div>
								<span class="text-muted-foreground">{item.name}</span>
								<span class="font-medium">{item.percentage.toFixed(1)}%</span>
								<span class="text-muted-foreground text-xs">({item.value})</span>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</div>

		<!-- Cost by Volume Label -->
		{#if hasBreakdownLines && labelData.length > 0}
			<div class="min-w-0 pt-2 border-t border-border/60 md:pt-0 md:border-t-0">
				<h4 class="text-xs font-semibold text-foreground mb-2 md:mb-3 tracking-wide uppercase">
					By volume label
				</h4>
				<div class="flex flex-col sm:flex-row items-center gap-3 sm:gap-4">
					<div class="w-[148px] h-[148px] sm:w-[160px] sm:h-[160px] shrink-0 relative">
						{#key labelChartKey}
							<PieChart
								data={labelData}
								key="label"
								value="cost"
								c="color"
								innerRadius={0.6}
								legend={false}
							/>
						{/key}
						<div class="absolute inset-0 flex items-center justify-center pointer-events-none">
							<div class="text-center px-1">
								<div class="text-sm sm:text-base font-bold leading-tight">{formatCurrency(labelTotalCost)}</div>
								<div class="text-[10px] sm:text-xs text-muted-foreground">/year</div>
							</div>
						</div>
					</div>
					<div class="flex-1 min-w-0 w-full">
						<div class="flex flex-col gap-1.5 text-sm">
							{#each labelLegendItems as item}
								<div class="flex items-center gap-2">
									<div class="h-3 w-3 rounded-sm shrink-0" style="background-color: {item.color}"></div>
									<span class="text-muted-foreground">{item.name}</span>
									<span class="font-medium">{item.percentage.toFixed(1)}%</span>
									<span class="text-muted-foreground text-xs">({item.value})</span>
								</div>
							{/each}
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{:else}
	<div class="text-center text-muted-foreground py-5 text-sm">
		Add products to see cost distribution
	</div>
{/if}

<style>
	/* Override layerchart styles to fit within container */
	:global(.chart-container) {
		width: 100%;
		height: 100%;
	}
</style>
