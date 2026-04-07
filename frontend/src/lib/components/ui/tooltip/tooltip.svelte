<script lang="ts">
	import { Tooltip as TooltipPrimitive } from "bits-ui";

	type $$Props = TooltipPrimitive.Props;

	export let openDelay: $$Props["openDelay"] = 150;
	export let closeDelay: $$Props["closeDelay"] = 0;
</script>

<TooltipPrimitive.Root {openDelay} {closeDelay} {...$$restProps}>
	<slot />
</TooltipPrimitive.Root>
