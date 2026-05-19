completion = await client.chat.completions.create(
    # ── Required ──────────────────────────────────────────────────────────
    model="gpt-4o-mini",        # any model string: gpt-4o, gpt-4.1, gpt-4.1-mini
    messages=[...],             # list of {role, content} dicts

    # ── Tools ─────────────────────────────────────────────────────────────
    tools=TOOLS,                # list of tool definitions
    tool_choice="auto",         # "auto"     → model decides
                                # "none"     → never call tools, always respond
                                # "required" → MUST call a tool, never respond directly
                                # {"type": "function", "function": {"name": "web_search"}}
                                #            → force a specific tool

    # ── Sampling ──────────────────────────────────────────────────────────
    temperature=0.2,            # 0.0 - 2.0
                                # 0.0 = deterministic, same answer every time
                                # 0.7 = balanced, default
                                # 1.5+ = very creative, unpredictable
    
    top_p=0.9,                  # 0.0 - 1.0, alternative to temperature
                                # don't use both at the same time
    
    n=1,                        # how many completions to generate
                                # n=3 returns 3 different responses to same prompt
    
    seed=42,                    # attempt deterministic output
                                # same seed + same input = same output (mostly)

    # ── Length control ────────────────────────────────────────────────────
    max_tokens=1000,            # hard cap on response length
                                # always set this in production
    
    max_completion_tokens=1000, # newer alias for max_tokens

    # ── Stop sequences ────────────────────────────────────────────────────
    stop=["###", "END"],        # stop generating when hitting these strings
                                # useful for structured output parsing

    # ── Output format ─────────────────────────────────────────────────────
    response_format={
        "type": "text"          # default, plain text response
    },
    response_format={
        "type": "json_object"   # forces valid JSON output, used in 08-code-review
    },
    response_format={
        "type": "json_schema",  # strict JSON schema enforcement (newer models)
        "json_schema": {
            "name": "my_schema",
            "schema": { ... }   # full JSON schema definition
        }
    },

    # ── Streaming ─────────────────────────────────────────────────────────
    stream=True,                # True  → SSE streaming, used in 02-streaming
                                # False → wait for full response (default)
    
    stream_options={
        "include_usage": True   # include token usage stats in stream
    },

    # ── Penalties ─────────────────────────────────────────────────────────
    frequency_penalty=0.0,      # -2.0 to 2.0
                                # positive = penalise repeated tokens
                                # useful to reduce repetitive responses
    
    presence_penalty=0.0,       # -2.0 to 2.0
                                # positive = penalise tokens already used
                                # encourages talking about new topics

    # ── Logging ───────────────────────────────────────────────────────────
    user="user-123",            # end user identifier for abuse monitoring
                                # OpenAI logs this for their safety systems

    # ── Timeout ───────────────────────────────────────────────────────────
    timeout=30.0,               # seconds before request times out
                                # always set in production
)

-------------------------------------------------------------------
temperature      # every request
max_tokens       # every production request  
stream           # feature 02
response_format  # feature 08 code review
tools + tool_choice  # feature 03, 07
seed             # when you need reproducible output for testing
timeout          # production only
--------------------------------------------------------------------
python -m venv venv        # create it (once)
venv\Scripts\activate      # activate it (every new terminal session)
pip install -r requirements.txt  # install deps into it