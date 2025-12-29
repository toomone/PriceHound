<script lang="ts">
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";

	type $$Props = TabsPrimitive.RootProps;

	let className: $$Props["class"] = undefined;
	export let value: $$Props["value"] = undefined;
	export { className as class };
</script>

<TabsPrimitive.Root bind:value class={cn("", className)} {...$$restProps}>
	<slot />
</TabsPrimitive.Root>

