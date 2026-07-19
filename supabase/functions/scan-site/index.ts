import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseClient, getCorsHeaders } from "../_shared/supabase.ts";

interface ScanRequest {
    scan_id: string;
    url: string;
}

serve(async (req) => {
    // Handle CORS preflight
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: getCorsHeaders() });
    }

    try {
        const authHeader = req.headers.get("Authorization");
        if (!authHeader) {
            return new Response(
                JSON.stringify({ error: "Missing authorization header" }),
                {
                    status: 401,
                    headers: {
                        ...getCorsHeaders(),
                        "Content-Type": "application/json",
                    },
                }
            );
        }

        const supabase = getSupabaseClient(authHeader);
        const { scan_id, url }: ScanRequest = await req.json();

        // Validate input
        if (!scan_id || !url) {
            return new Response(
                JSON.stringify({ error: "Missing scan_id or url" }),
                {
                    status: 400,
                    headers: {
                        ...getCorsHeaders(),
                        "Content-Type": "application/json",
                    },
                }
            );
        }

        // Update scan status to processing
        const { error: updateError } = await supabase
            .from("site_scans")
            .update({
                status: "processing",
                started_at: new Date().toISOString(),
            })
            .eq("id", scan_id);

        if (updateError) {
            throw updateError;
        }

        // TODO: Implement actual scanning logic
        // This is where you would:
        // 1. Fetch the website content
        // 2. Analyze for gambling, scam, or illegal lending indicators
        // 3. Capture screenshots and videos
        // 4. Store evidence in Supabase Storage

        // For now, simulate scanning with a placeholder
        const scanResult = await performScan(url);

        // Update scan with results
        const { error: resultError } = await supabase
            .from("site_scans")
            .update({
                status: "completed",
                risk_score: scanResult.risk_score,
                categories: scanResult.categories,
                completed_at: new Date().toISOString(),
            })
            .eq("id", scan_id);

        if (resultError) {
            throw resultError;
        }

        return new Response(
            JSON.stringify({
                success: true,
                scan_id,
                risk_score: scanResult.risk_score,
                categories: scanResult.categories,
            }),
            {
                headers: {
                    ...getCorsHeaders(),
                    "Content-Type": "application/json",
                },
            }
        );
    } catch (error) {
        console.error("Scan error:", error);

        // Update scan status to failed
        const scanId = (await req.json()).scan_id;
        if (scanId) {
            const supabase = getSupabaseClient(
                req.headers.get("Authorization") ?? ""
            );
            await supabase
                .from("site_scans")
                .update({
                    status: "failed",
                    error_message: error.message,
                })
                .eq("id", scanId);
        }

        return new Response(
            JSON.stringify({ error: "Scan failed", details: error.message }),
            {
                status: 500,
                headers: {
                    ...getCorsHeaders(),
                    "Content-Type": "application/json",
                },
            }
        );
    }
});

async function performScan(url: string) {
    // Placeholder scanning logic
    // In production, this would:
    // 1. Use a headless browser to fetch page content
    // 2. Analyze text for keywords related to gambling, scams, illegal lending
    // 3. Check domain age, SSL certificate, etc.
    // 4. Capture screenshots using Puppeteer or similar

    const categories: string[] = [];
    let risk_score = 0;

    // Simple keyword-based detection (placeholder)
    const gamblingKeywords = [
        "casino",
        "bet",
        "gambling",
        "slots",
        "poker",
        "jackpot",
    ];
    const scamKeywords = [
        "guaranteed",
        "winner",
        "claim prize",
        "limited time",
        "act now",
    ];
    const illegalLendingKeywords = [
        "quick loan",
        "no collateral",
        "instant approval",
        "high interest",
        "bnpl",
    ];

    try {
        const response = await fetch(url);
        const html = await response.text();
        const lowerHtml = html.toLowerCase();

        // Check for gambling indicators
        if (gamblingKeywords.some((k) => lowerHtml.includes(k))) {
            categories.push("gambling");
            risk_score += 40;
        }

        // Check for scam indicators
        if (scamKeywords.some((k) => lowerHtml.includes(k))) {
            categories.push("scam");
            risk_score += 30;
        }

        // Check for illegal lending indicators
        if (illegalLendingKeywords.some((k) => lowerHtml.includes(k))) {
            categories.push("illegal_lending");
            risk_score += 30;
        }
    } catch (e) {
        console.error("Error fetching URL:", e);
    }

    return {
        risk_score: Math.min(risk_score, 100),
        categories,
    };
}
