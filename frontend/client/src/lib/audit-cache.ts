/**
 * Sistema de Cache para Laudos de Auditoria
 * Otimiza performance com caching inteligente
 * Design: Privacy-first, localStorage-based
 */

const CACHE_PREFIX = 'auditx_audit_';
const CACHE_EXPIRY_HOURS = 24;

export interface CachedAudit {
    id: string;
    data: any;
    timestamp: number;
    expiresAt: number;
}

class AuditCache {
    /**
     * Armazenar laudo em cache
     */
    static setAudit(auditId: string, data: any): void {
        try {
            const now = Date.now();
            const expiresAt = now + CACHE_EXPIRY_HOURS * 3600 * 1000;

            const cached: CachedAudit = {
                id: auditId,
                data,
                timestamp: now,
                expiresAt,
            };

            localStorage.setItem(
                `${CACHE_PREFIX}${auditId}`,
                JSON.stringify(cached)
            );
        } catch (error) {
            console.error('Cache set error:', error);
        }
    }

    /**
     * Recuperar laudo do cache
     */
    static getAudit(auditId: string): any | null {
        try {
            const cached = localStorage.getItem(`${CACHE_PREFIX}${auditId}`);
            if (!cached) return null;

            const parsed: CachedAudit = JSON.parse(cached);

            // Verificar se expirou
            if (Date.now() > parsed.expiresAt) {
                localStorage.removeItem(`${CACHE_PREFIX}${auditId}`);
                return null;
            }

            return parsed.data;
        } catch (error) {
            console.error('Cache get error:', error);
            return null;
        }
    }

    /**
     * Limpar cache de um laudo
     */
    static clearAudit(auditId: string): void {
        try {
            localStorage.removeItem(`${CACHE_PREFIX}${auditId}`);
        } catch (error) {
            console.error('Cache clear error:', error);
        }
    }

    /**
     * Limpar todo o cache
     */
    static clearAll(): void {
        try {
            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(CACHE_PREFIX)) {
                    localStorage.removeItem(key);
                }
            });
        } catch (error) {
            console.error('Cache clear all error:', error);
        }
    }

    /**
     * Obter informações de cache
     */
    static getCacheInfo(): { count: number; size: number } {
        try {
            let count = 0;
            let size = 0;

            const keys = Object.keys(localStorage);
            keys.forEach(key => {
                if (key.startsWith(CACHE_PREFIX)) {
                    count++;
                    const item = localStorage.getItem(key);
                    if (item) {
                        size += item.length;
                    }
                }
            });

            return { count, size };
        } catch (error) {
            console.error('Cache info error:', error);
            return { count: 0, size: 0 };
        }
    }

    /**
     * Limpar cache expirado
     */
    static cleanExpired(): number {
        try {
            let cleaned = 0;
            const now = Date.now();
            const keys = Object.keys(localStorage);

            keys.forEach(key => {
                if (key.startsWith(CACHE_PREFIX)) {
                    try {
                        const cached = localStorage.getItem(key);
                        if (cached) {
                            const parsed: CachedAudit = JSON.parse(cached);
                            if (now > parsed.expiresAt) {
                                localStorage.removeItem(key);
                                cleaned++;
                            }
                        }
                    } catch (error) {
                        console.error('Error cleaning cache:', error);
                    }
                }
            });

            return cleaned;
        } catch (error) {
            console.error('Cache clean error:', error);
            return 0;
        }
    }
}

/**
 * Otimizações de Performance
 */
export class PerformanceOptimizer {
    /**
     * Lazy load imagens
     */
    static setupLazyLoading(): void {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target as HTMLImageElement;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.removeAttribute('data-src');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
    }

    /**
     * Prefetch recursos críticos
     */
    static prefetchResources(urls: string[]): void {
        urls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
        });
    }

    /**
     * Preload recursos críticos
     */
    static preloadResources(urls: string[]): void {
        urls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = url;
            link.as = 'script';
            document.head.appendChild(link);
        });
    }

    /**
     * Medir performance
     */
    static measurePerformance(): PerformanceMetrics {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        const paint = performance.getEntriesByType('paint');

        return {
            dns: navigation?.domainLookupEnd - navigation?.domainLookupStart || 0,
            tcp: navigation?.connectEnd - navigation?.connectStart || 0,
            ttfb: navigation?.responseStart - navigation?.requestStart || 0,
            download: navigation?.responseEnd - navigation?.responseStart || 0,
            domInteractive: navigation?.domInteractive - navigation?.fetchStart || 0,
            domComplete: navigation?.domComplete - navigation?.fetchStart || 0,
            loadComplete: navigation?.loadEventEnd - navigation?.fetchStart || 0,
            fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
            lcp: 0, // Requer PerformanceObserver
        };
    }

    /**
     * Reportar Web Vitals
     */
    static reportWebVitals(callback: (metrics: WebVitals) => void): void {
        // Cumulative Layout Shift
        let cls = 0;
        const clsObserver = new PerformanceObserver(list => {
            for (const entry of list.getEntries()) {
                if (!(entry as any).hadRecentInput) {
                    cls += (entry as any).value;
                }
            }
        });

        try {
            clsObserver.observe({ type: 'layout-shift', buffered: true });
        } catch (e) {
            console.error('CLS observer error:', e);
        }

        // Largest Contentful Paint
        let lcp = 0;
        const lcpObserver = new PerformanceObserver(list => {
            const entries = list.getEntries();
            const lastEntry = entries[entries.length - 1] as any;
            lcp = lastEntry.renderTime || lastEntry.loadTime;
        });

        try {
            lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        } catch (e) {
            console.error('LCP observer error:', e);
        }

        // First Input Delay
        let fid = 0;
        const fidObserver = new PerformanceObserver(list => {
            const entries = list.getEntries();
            const firstEntry = entries[0];
            fid = (firstEntry as any).processingEnd - (firstEntry as any).startTime;
        });

        try {
            fidObserver.observe({ type: 'first-input', buffered: true });
        } catch (e) {
            console.error('FID observer error:', e);
        }

        // Reportar após 3 segundos
        setTimeout(() => {
            callback({
                cls,
                lcp,
                fid,
            });

            clsObserver.disconnect();
            lcpObserver.disconnect();
            fidObserver.disconnect();
        }, 3000);
    }
}

export interface PerformanceMetrics {
    dns: number;
    tcp: number;
    ttfb: number;
    download: number;
    domInteractive: number;
    domComplete: number;
    loadComplete: number;
    fcp: number;
    lcp: number;
}

export interface WebVitals {
    cls: number; // Cumulative Layout Shift
    lcp: number; // Largest Contentful Paint
    fid: number; // First Input Delay
}

export default AuditCache;
