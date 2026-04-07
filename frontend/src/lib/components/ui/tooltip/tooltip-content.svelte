<script lang="ts">
	import { Tooltip as TooltipPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";
	import { fly } from "svelte/transition";

	type $$Props = TooltipPrimitive.ContentProps;

	let className: $$Props["class"] = undefined;
	export let sideOffset: $$Props["sideOffset"] = 8;
	export { className as class };
</script>

<TooltipPrimitive.Content
	transition={fly}
	transitionConfig={{ y: 4, duration: 120 }}
	{sideOffset}
	class={cn(
		"z-50 max-w-xs rounded-md bg-foreground px-3 py-1.5 text-xs text-background shadow-md",
		className
	)}
	{...$$restProps}
>
	<TooltipPrimitive.Arrow class="fill-foreground" />
	<slot />
</TooltipPrimitive.Content>
