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

        const { action, session_id, content, role, file_url, file_type } =
            await req.json();

        switch (action) {
            case "create_session": {
                const { data, error } = await supabase
                    .from("chat_sessions")
                    .insert({ user_id: user.id })
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
                    JSON.stringify({ session: data }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "send_message": {
                if (!session_id || !content) {
                    return new Response(
                        JSON.stringify({
                            error: "Missing session_id or content",
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

                const { data, error } = await supabase
                    .from("chat_messages")
                    .insert({
                        session_id,
                        user_id: user.id,
                        content,
                        role: role || "user",
                        file_url,
                        file_type,
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
                    JSON.stringify({ message: data }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "get_history": {
                if (!session_id) {
                    return new Response(
                        JSON.stringify({ error: "Missing session_id" }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                const { data, error } = await supabase
                    .from("chat_messages")
                    .select("*")
                    .eq("session_id", session_id)
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
                    JSON.stringify({ messages: data }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "list_chats": {
                const { data, error } = await supabase
                    .from("chat_sessions")
                    .select(
                        `
                        *,
                        chat_messages (
                            content,
                            created_at
                        )
                    `
                    )
                    .eq("user_id", user.id)
                    .order("updated_at", { ascending: false });

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

                // Add last message preview
                const sessionsWithPreview = data.map((session) => ({
                    ...session,
                    last_message:
                        session.chat_messages?.[
                            session.chat_messages.length - 1
                        ] || null,
                }));

                return new Response(
                    JSON.stringify({ sessions: sessionsWithPreview }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "delete_session": {
                if (!session_id) {
                    return new Response(
                        JSON.stringify({ error: "Missing session_id" }),
                        {
                            status: 400,
                            headers: {
                                ...getCorsHeaders(),
                                "Content-Type": "application/json",
                            },
                        }
                    );
                }

                const { error } = await supabase
                    .from("chat_sessions")
                    .delete()
                    .eq("id", session_id)
                    .eq("user_id", user.id);

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
                    JSON.stringify({ success: true }),
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
