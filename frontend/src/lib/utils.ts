import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export function formatCurrency(value: number): string {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		minimumFractionDigits: 2,
		maximumFractionDigits: 2
	}).format(value);
}

export function parsePrice(priceStr: string | null | undefined): number {
	if (!priceStr || priceStr === '-' || priceStr === '') return 0;
	const cleaned = priceStr.replace(/[^\d.]/g, '');
	return parseFloat(cleaned) || 0;
}

export function isPercentagePrice(priceStr: string | null | undefined): boolean {
	if (!priceStr) return false;
	return priceStr.includes('%');
}

export function parsePercentage(priceStr: string | null | undefined): number {
	if (!priceStr || !priceStr.includes('%')) return 0;
	const cleaned = priceStr.replace(/[^\d.]/g, '');
	return parseFloat(cleaned) || 0;
}

export function formatNumber(value: number): string {
	if (value >= 1_000_000_000) {
		return (value / 1_000_000_000).toFixed(1).replace(/\.0$/, '') + 'B';
	}
	if (value >= 1_000_000) {
		return (value / 1_000_000).toFixed(1).replace(/\.0$/, '') + 'M';
	}
	if (value >= 1_000) {
		return (value / 1_000).toFixed(1).replace(/\.0$/, '') + 'K';
	}
	return value.toLocaleString('en-US');
}

