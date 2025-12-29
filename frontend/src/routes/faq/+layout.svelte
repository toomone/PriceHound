<script>
	import { Card, CardContent } from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
</script>

<div class="min-h-screen bg-background p-4 md:p-8">
	<div class="mx-auto max-w-3xl">
		<!-- Header with navigation -->
		<div class="mb-6 flex items-center gap-4">
			<Button variant="ghost" href="/" class="gap-2">
				<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M19 12H5M12 19l-7-7 7-7" />
				</svg>
				Back to Calculator
			</Button>
		</div>

		<!-- FAQ Content Card -->
		<Card class="border-border">
			<CardContent class="faq-content p-6 md:p-8">
				<slot />
			</CardContent>
		</Card>

		<!-- Footer -->
		<footer class="mt-8 text-center text-xs text-muted-foreground">
			<p>
				PriceHound Datadog Pricing Calculator uses data sourced from
				<a href="https://www.datadoghq.com/pricing/list/" target="_blank" rel="noopener noreferrer" class="text-datadog-purple hover:underline">
					Datadog Pricing
				</a>
			</p>
		</footer>
	</div>
</div>

<style>
	.faq-content :global(h1) {
		font-size: 1.875rem;
		font-weight: 700;
		margin-bottom: 1.5rem;
		color: hsl(var(--foreground));
	}

	.faq-content :global(h2) {
		font-size: 1.25rem;
		font-weight: 600;
		margin-top: 2rem;
		margin-bottom: 0.75rem;
		color: hsl(var(--foreground));
	}

	.faq-content :global(p) {
		margin-bottom: 1rem;
		line-height: 1.7;
		color: hsl(var(--muted-foreground));
	}

	.faq-content :global(ul) {
		list-style-type: disc;
		padding-left: 1.5rem;
		margin-bottom: 1rem;
	}

	.faq-content :global(li) {
		margin-bottom: 0.5rem;
		line-height: 1.6;
		color: hsl(var(--muted-foreground));
	}

	.faq-content :global(strong) {
		color: hsl(var(--foreground));
		font-weight: 600;
	}

	.faq-content :global(a) {
		color: hsl(var(--datadog-purple));
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.faq-content :global(a:hover) {
		opacity: 0.8;
	}
</style>

