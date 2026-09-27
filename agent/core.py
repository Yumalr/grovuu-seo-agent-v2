"""Core agent logic: tool definitions, function calling, and chat loop.

Uses the google.genai SDK for Gemini function calling.
Handles the function calling lifecycle so the Streamlit app
only needs to call process_chat_message() and display the result.
"""

import json
from google import genai
from google.genai import types
from mcp_tools.inspect_page import inspect_page as _inspect_page


# ---------------------------------------------------------------------------
# Tool declarations for Gemini function calling
# ---------------------------------------------------------------------------

INSPECT_PAGE_DECLARATION = types.FunctionDeclaration(
    name="inspect_page",
    description=(
        "Fetch one public webpage and return observed server-HTML SEO evidence. "
        "Returns: HTTP status, canonical, robots directives, title + character count, "
        "meta description + character count, heading hierarchy (H1-H6), "
        "internal and external links with anchors, images (alt, width, height, "
        "loading, fetchpriority), Open Graph tags, JSON-LD schema types, "
        "language, viewport, and server-HTML word count. "
        "ALWAYS use this tool when the user provides a URL to audit, inspect, "
        "or analyse. "
        "This tool does NOT verify: JavaScript-rendered content, Core Web Vitals, "
        "Search Console, GA4, rankings, or SERP competitor data."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "url": types.Schema(
                type=types.Type.STRING,
                description="The full public URL to inspect (must start with http:// or https://)",
            )
        },
        required=["url"],
    ),
)

TOOL_DECLARATIONS = [types.Tool(function_declarations=[INSPECT_PAGE_DECLARATION])]


# Map tool names → Python callables
TOOL_FUNCTIONS = {
    "inspect_page": _inspect_page,
}


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def execute_tool_call(function_call) -> dict:
    """Execute a single Gemini function call. Returns the tool result dict."""
    name = function_call.name
    args = dict(function_call.args) if function_call.args else {}

    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return {"error": f"Unknown tool: {name}"}

    try:
        return func(**args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


# ---------------------------------------------------------------------------
# Chat processing (called from Streamlit)
# ---------------------------------------------------------------------------

MAX_TOOL_ITERATIONS = 5


def process_chat_message(
    user_message: str,
    client,
    model_name: str,
    history: list,
    system_prompt: str,
    on_tool_start=None,
    on_tool_end=None,
):
    """Send a user message, handling function calls in a loop.

    Args:
        user_message: The user's input text.
        client: A google.genai.Client instance.
        model_name: Model identifier string.
        history: List of previous messages (Content objects or dicts).
        system_prompt: System instruction text.
        on_tool_start: Optional callback(tool_name, args) before execution.
        on_tool_end: Optional callback(tool_name, result) after execution.

    Returns:
        tuple: (response_text: str, tool_results: dict, updated_history: list)
    """
    # Build the config
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=TOOL_DECLARATIONS,
    )

    # Add user message to history
    history = list(history)  # shallow copy
    history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))

    # Send to Gemini
    response = client.models.generate_content(
        model=model_name,
        contents=history,
        config=config,
    )

    all_tool_results = {}

    for _iteration in range(MAX_TOOL_ITERATIONS):
        # Check for function calls
        function_calls = []
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call and part.function_call.name:
                    function_calls.append(part)

        if not function_calls:
            break

        # Add the model's response (with function calls) to history
        history.append(response.candidates[0].content)

        # Execute each function call with callbacks
        function_response_parts = []
        for fc_part in function_calls:
            fc = fc_part.function_call
            args = dict(fc.args) if fc.args else {}

            if on_tool_start:
                on_tool_start(fc.name, args)

            result = execute_tool_call(fc)
            all_tool_results[fc.name] = result

            if on_tool_end:
                on_tool_end(fc.name, result)

            function_response_parts.append(
                types.Part.from_function_response(
                    name=fc.name,
                    response={"result": json.dumps(result, default=str)},
                )
            )

        # Add function responses to history
        history.append(types.Content(role="user", parts=function_response_parts))

        # Send back to Gemini
        response = client.models.generate_content(
            model=model_name,
            contents=history,
            config=config,
        )

    # Add final response to history
    if response.candidates and response.candidates[0].content:
        history.append(response.candidates[0].content)

    # Extract text
    try:
        text = response.text
    except Exception:
        text = "Analysis complete but I could not generate a text summary."

    return text, all_tool_results, history
