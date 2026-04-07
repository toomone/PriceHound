<script lang="ts">
	import { Tooltip as TooltipPrimitive } from "bits-ui";

	type $$Props = TooltipPrimitive.TriggerProps;
	type $$Slots = TooltipPrimitive.TriggerSlots;

	let className: $$Props["class"] = undefined;
	export { className as class };
	export let asChild: $$Props["asChild"] = undefined;
</script>

<TooltipPrimitive.Trigger {asChild} class={className} {...$$restProps} let:builder>
	<slot {builder} />
</TooltipPrimitive.Trigger>
