<script lang="ts">
	import { cn } from '$lib/utils';

	let className: string | undefined = undefined;
	export { className as class };
</script>

<div class={cn('p-4 pt-0', className)} {...$$restProps}>
	<slot />
</div>

