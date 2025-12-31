<script>
	import { Button } from '$lib/components/ui/button';
</script>

<div class="min-h-screen bg-background p-4 md:p-8">
	<div class="mx-auto max-w-4xl">
		<!-- Header with navigation -->
		<div class="mb-6 flex items-center gap-4">
			<Button variant="ghost" href="/" class="gap-2">
				<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M19 12H5M12 19l-7-7 7-7" />
				</svg>
				Back to PriceHound Datadog Pricing Calculator
			</Button>
		</div>

		<!-- Content -->
		<slot />

		<!-- Footer -->
		<footer class="mt-8 text-center text-xs text-muted-foreground">
			<p>
				PriceHound uses data sourced from
				<a href="https://www.datadoghq.com/pricing/list/" target="_blank" rel="noopener noreferrer" class="text-datadog-purple hover:underline">
					Datadog Pricing
				</a>
			</p>
		</footer>
	</div>
</div>

