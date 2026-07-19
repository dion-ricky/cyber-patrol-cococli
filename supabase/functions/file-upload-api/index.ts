import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseClient, getCorsHeaders } from "../_shared/supabase.ts";

const ALLOWED_FILE_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "text/plain",
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

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

        const { action, file_name, file_type, file_size, session_id } =
            await req.json();

        switch (action) {
            case "upload_chat_file": {
                if (!file_name || !file_type || !session_id) {
                    return new Response(
                        JSON.stringify({
                            error: "Missing file_name, file_type, or session_id",
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

                // Validate file type
                if (!ALLOWED_FILE_TYPES.includes(file_type)) {
                    return new Response(
                        JSON.stringify({
                            error: "File type not allowed",
                            allowed_types: ALLOWED_FILE_TYPES,
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

                // Validate file size
                if (file_size > MAX_FILE_SIZE) {
                    return new Response(
                        JSON.stringify({
                            error: "File size exceeds limit",
                            max_size: MAX_FILE_SIZE,
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

                // Verify session belongs to user
                const { data: session, error: sessionError } = await supabase
                    .from("chat_sessions")
                    .select("id")
                    .eq("id", session_id)
                    .eq("user_id", user.id)
                    .single();

                if (sessionError || !session) {
                    return new Response(
                        JSON.stringify({
                            error: "Session not found or unauthorized",
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

                // Generate upload URL
                const filePath = `${user.id}/${session_id}/${Date.now()}_${file_name}`;
                const { data, error } = await supabase.storage
                    .from("chat-uploads")
                    .createSignedUploadUrl(filePath);

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
                    JSON.stringify({
                        upload_url: data.signedUrl,
                        file_path: filePath,
                    }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "get_upload_url": {
                if (!file_name || !file_type) {
                    return new Response(
                        JSON.stringify({
                            error: "Missing file_name or file_type",
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

                // Validate file type
                if (!ALLOWED_FILE_TYPES.includes(file_type)) {
                    return new Response(
                        JSON.stringify({
                            error: "File type not allowed",
                            allowed_types: ALLOWED_FILE_TYPES,
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

                const filePath = `${user.id}/${Date.now()}_${file_name}`;
                const { data, error } = await supabase.storage
                    .from("chat-uploads")
                    .createSignedUploadUrl(filePath);

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
                    JSON.stringify({
                        upload_url: data.signedUrl,
                        file_path: filePath,
                    }),
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
