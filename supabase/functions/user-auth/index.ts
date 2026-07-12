import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseClient, getCorsHeaders } from "../_shared/supabase.ts";

serve(async (req) => {
    if (req.method === "OPTIONS") {
        return new Response("ok", { headers: getCorsHeaders() });
    }

    try {
        const { action, email, password, full_name } = await req.json();
        const supabase = getSupabaseClient();

        switch (action) {
            case "register": {
                const { data, error } = await supabase.auth.signUp({
                    email,
                    password,
                    options: {
                        data: { full_name },
                    },
                });

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
                        user: data.user,
                        session: data.session,
                    }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "login": {
                const { data, error } =
                    await supabase.auth.signInWithPassword({
                        email,
                        password,
                    });

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
                        user: data.user,
                        session: data.session,
                    }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "logout": {
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

                const supabaseWithAuth = getSupabaseClient(authHeader);
                const { error } = await supabaseWithAuth.auth.signOut();

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

            case "refresh": {
                const { refresh_token } = await req.json();
                const { data, error } =
                    await supabase.auth.refreshSession({
                        refresh_token,
                    });

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
                        session: data.session,
                    }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "get_profile": {
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

                const supabaseWithAuth = getSupabaseClient(authHeader);
                const {
                    data: { user },
                    error: userError,
                } = await supabaseWithAuth.auth.getUser();

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

                const { data: profile, error: profileError } =
                    await supabaseWithAuth
                        .from("profiles")
                        .select("*")
                        .eq("id", user.id)
                        .single();

                if (profileError) {
                    return new Response(
                        JSON.stringify({ error: profileError.message }),
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
                    JSON.stringify({ profile }),
                    {
                        headers: {
                            ...getCorsHeaders(),
                            "Content-Type": "application/json",
                        },
                    }
                );
            }

            case "update_profile": {
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

                const supabaseWithAuth = getSupabaseClient(authHeader);
                const {
                    data: { user },
                    error: userError,
                } = await supabaseWithAuth.auth.getUser();

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

                const { full_name, avatar_url } = await req.json();
                const { data: profile, error: profileError } =
                    await supabaseWithAuth
                        .from("profiles")
                        .update({ full_name, avatar_url })
                        .eq("id", user.id)
                        .select()
                        .single();

                if (profileError) {
                    return new Response(
                        JSON.stringify({ error: profileError.message }),
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
                    JSON.stringify({ profile }),
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
