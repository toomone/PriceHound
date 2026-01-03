/**
 * Datadog RUM custom action tracking utilities.
 * 
 * These functions track user interactions as custom actions in Datadog RUM.
 * Actions are only sent if RUM has been initialized (browser only).
 */

import { browser } from '$app/environment';

// Type for the datadogRum module
interface DatadogRum {
	addAction: (name: string, context?: Record<string, unknown>) => void;
}

let rumInstance: DatadogRum | null = null;

/**
 * Initialize the RUM instance for tracking.
 * Called automatically when the module is first used.
 */
async function getRum(): Promise<DatadogRum | null> {
	if (!browser) return null;
	
	if (!rumInstance) {
		try {
			const { datadogRum } = await import('@datadog/browser-rum');
			rumInstance = datadogRum;
		} catch (e) {
			console.warn('Failed to load Datadog RUM:', e);
			return null;
		}
	}
	
	return rumInstance;
}

/**
 * Track when a user creates a shareable URL for a quote.
 */
export async function trackQuoteShared(context: {
	region: string;
	itemCount: number;
	protected: boolean;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('quote_shared', context);
}

/**
 * Track when a user imports a JSON file.
 */
export async function trackJsonImported(context: {
	region: string;
	itemCount: number;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('json_imported', context);
}

/**
 * Track when a user exports to JSON.
 */
export async function trackJsonExported(context: {
	region: string;
	itemCount: number;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('json_exported', context);
}

/**
 * Track when a user exports to CSV.
 */
export async function trackCsvExported(context: {
	region: string;
	itemCount: number;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('csv_exported', context);
}

/**
 * Track when a user prints/downloads PDF.
 */
export async function trackPdfDownloaded(context: {
	region: string;
	itemCount: number;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('pdf_downloaded', context);
}

/**
 * Track when a user opens a shared quote.
 */
export async function trackQuoteOpened(context: {
	region: string;
	quoteId: string;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('quote_opened', context);
}

/**
 * Track when pricing is synced from the UI.
 */
export async function trackPricingSync(context: {
	region: string;
}): Promise<void> {
	const rum = await getRum();
	rum?.addAction('pricing_sync', context);
}

