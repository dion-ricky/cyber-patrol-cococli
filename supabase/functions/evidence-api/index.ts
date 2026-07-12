import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseClient, getCorsHeaders } from "../_shared/supabase.ts";

serve(async (req) => {
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: getCorsHeaders() });
    }

    try {
        const authHeader = req.headers.get("Authorization");
        if (!authHeader) {
            return new Response(
                JSON.stringify({ error: "Not authenticated" }),
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
        const {
            data: { user },
            error: userError,
        } = await supabase.auth.getUser();

        if (userError || !user) {
            return new Response(
                JSON.stringify({
                    error: userError?.message || "Not authenticated",
                }),
                {
                    status: 401,
                    headers: {
                        ...getCorsHeaders(),
                        "Content-Type": "application/json",
                    },
                }
            );
        }

        const { action, scan_id, file_url, file_type, file_size, metadata } =
            await req.json();

        switch (action) {
            case "upload_evidence": {
                if (!scan_id || !file_url || !file_type) {
                    return new Response(
                        JSON.stringify({
                            error: "Missing scan_id, file_url, or file_type",
                        }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                // Verify scan belongs to user
                const { data: scan, error: scanError } = await supabase
                    .from("site_scans")
                    .select("id")
                    .eq("id", scan_id)
                    .eq("user_id", user.id)
                    .single();

                if (scanError || !scan) {
                    return new Response(
                        JSON.stringify({
                            error: "Scan not found or unauthorized",
                        }),
                        {
                            status: 404,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                const { data, error } = await supabase
                    .from("scan_evidence")
                    .insert({
                        scan_id,
                        file_url,
                        file_type,
                        file_size,
                        metadata,
                    })
                    .select()
                    .single();

                if (error) {
                    return new Response(
                        JSON.stringify({ error: error.message }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                return new Response(
                    JSON.stringify({ evidence: data }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "list_evidence": {
                if (!scan_id) {
                    return new Response(
                        JSON.stringify({ error: "Missing scan_id" }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                // Verify scan belongs to user
                const { data: scan, error: scanError } = await supabase
                    .from("site_scans")
                    .select("id")
                    .eq("id", scan_id)
                    .eq("user_id", user.id)
                    .single();

                if (scanError || !scan) {
                    return new Response(
                        JSON.stringify({
                            error: "Scan not found or unauthorized",
                        }),
                        {
                            status: 404,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                const { data, error } = await supabase
                    .from("scan_evidence")
                    .select("*")
                    .eq("scan_id", scan_id)
                    .order("created_at", { ascending: true });

                if (error) {
                    return new Response(
                        JSON.stringify({ error: error.message }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                return new Response(
                    JSON.stringify({ evidence: data }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "download_evidence": {
                const { evidence_id } = await req.json();

                if (!evidence_id) {
                    return new Response(
                        JSON.stringify({ error: "Missing evidence_id" }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                // Get evidence and verify ownership through scan
                const { data: evidence, error: evidenceError } =
                    await supabase
                        .from("scan_evidence")
                        .select(
                            `
                            *,
                            site_scans (
                                user_id
                            )
                        `
                        )
                        .eq("id", evidence_id)
                        .single();

                if (evidenceError || !evidence) {
                    return new Response(
                        JSON.stringify({ error: "Evidence not found" }),
                        {
                            status: 404,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                if (evidence.site_scans?.user_id !== user.id) {
                    return new Response(
                        JSON.stringify({ error: "Unauthorized" }),
                        {
                            status: 403,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                return new Response(
                    JSON.stringify({ evidence }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            default:
                return new Response(
                    JSON.stringify({ error: "Invalid action" }),
                    {
                        status: 400,
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
        }
    } catch (error) {
        return new Response(
            JSON.stringify({ error: error.message }),
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
