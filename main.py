from fasthtml.common import *
import openai
from datetime import datetime
from litellm import completion

# Initialize FastHTML app
app, rt = fast_app()

# Add CSS styles for better UX
css = Style("""
/* Button styles */
button {
    background: #007bff;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease-in-out;
    position: relative;
    overflow: hidden;
}

button:hover:not(:disabled) {
    background: #0056b3;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

/* Disabled button styles */
button:disabled {
    background: #6c757d !important;
    cursor: not-allowed !important;
    opacity: 0.6 !important;
    transform: none !important;
    box-shadow: none !important;
}

/* Loading indicator styles */
.htmx-request button {
    background: #6c757d !important;
    cursor: not-allowed !important;
    opacity: 0.8 !important;
}

.htmx-request button::after {
    content: "";
    position: absolute;
    width: 16px;
    height: 16px;
    margin: auto;
    border: 2px solid transparent;
    border-top-color: #ffffff;
    border-radius: 50%;
    animation: spin 1s ease infinite;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
}

@keyframes spin {
    0% { transform: translate(-50%, -50%) rotate(0deg); }
    100% { transform: translate(-50%, -50%) rotate(360deg); }
}

/* Special styling for the green refine test button */
button[style*="background: #4CAF50"]:disabled {
    background: #6c757d !important;
}

/* Loading text for buttons */
.htmx-request .btn-text {
    opacity: 0;
}

/* Form styling improvements */
textarea, input, select {
    border: 2px solid #e1e5e9;
    border-radius: 0.375rem;
    padding: 0.5rem;
    transition: border-color 0.2s ease-in-out;
}

textarea:focus, input:focus, select:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
}

/* Results styling */
pre {
    border-radius: 0.375rem;
    border: 1px solid #e1e5e9;
}

/* Loading indicator styling */
.htmx-indicator {
    background: linear-gradient(90deg, #f0f8ff, #e6f3ff);
    border: 1px solid #007bff;
    border-radius: 0.5rem;
    animation: pulse 2s ease-in-out infinite;
}

.htmx-indicator span {
    font-weight: 500;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}
""")

# Store iterations in memory (you could use a simple JSON file for persistence)
iterations = []

# Available models
MODELS = [
    "openai/gpt-5-mini",
    "openai/gpt-5",
    "openai/gpt-4.1-mini",
    "openai/gpt-4.1",
    "anthropic/claude-sonnet-4-20250514",
]

def test_prompt(system_prompt, user_prompt, model):
    """Test the prompt against the selected model"""
    response = completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return response.choices[0].message.content

def refine_prompt(current_system, user_feedback, last_response, original_goal):
    """Use an LLM to suggest a refined system prompt"""
    refinement_prompt = f"""You are a prompt engineering assistant. 

Original Goal: {original_goal}

Current System Prompt:
{current_system}

The last response was:
{last_response[:500]}...  # Truncate if too long

User Feedback:
{user_feedback}

Generate an improved system prompt that addresses the feedback while maintaining the original goal.
Return ONLY the new system prompt, no explanation."""
    
    response = completion(
        model="openai/gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a helpful prompt engineering assistant."},
            {"role": "user", "content": refinement_prompt}
        ]
    )
    
    return response.choices[0].message.content

@rt("/")
def get():
    return Titled("Prompt Refinement Tool", css,
        Form(
            Fieldset(
                Label("System Prompt:", 
                    Textarea(name="system_prompt", rows=4, 
                            placeholder="You are a helpful assistant...",
                            style="width: 100%; font-family: monospace;")),
                
                Label("User Prompt:", 
                    Textarea(name="user_prompt", rows=3,
                            placeholder="Explain quantum computing...",
                            style="width: 100%; font-family: monospace;")),
                
                Label("Model:",
                    Select(*[Option(m, value=m) for m in MODELS], 
                          name="model")),
                
                Label("Original Goal (what you're trying to achieve):",
                    Input(name="goal", type="text", 
                         placeholder="Get clear, simple explanations with analogies",
                         style="width: 100%;")),
                
                Button(Span("Test Prompt", cls="btn-text"), 
                      type="submit", hx_disabled_elt="this", 
                      hx_indicator="#loading-test"),
            ),
            hx_post="/test",
            hx_target="#results",
            hx_swap="innerHTML"
        ),
        Div(Span("🤖 Testing your prompt..."), 
            id="loading-test", style="display: none; text-align: center; color: #007bff; padding: 1rem;"),
        Div(id="results"),
        Div(id="iterations")
    )

@rt("/test")
async def post(system_prompt: str, user_prompt: str, model: str, goal: str):
    """Test the current prompts"""
    try:
        response = test_prompt(system_prompt, user_prompt, model)
        
        # Store this iteration
        iteration = {
            "timestamp": datetime.now().isoformat(),
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "model": model,
            "response": response,
            "goal": goal
        }
        iterations.append(iteration)
        
        return Div(
            H3("Response:"),
            Pre(response, style="background: #f0f0f0; padding: 1em; white-space: pre-wrap;"),
            
            H3("Not quite right? Refine it:"),
            Form(
                Textarea(name="feedback", rows=3,
                        placeholder="Too technical, needs more examples, wrong focus...",
                        style="width: 100%;"),
                Hidden(name="current_system", value=system_prompt),
                Hidden(name="last_response", value=response),
                Hidden(name="user_prompt", value=user_prompt),
                Hidden(name="model", value=model),
                Hidden(name="goal", value=goal),
                Button(Span("🔄 Refine System Prompt", cls="btn-text"), 
                      type="submit", hx_disabled_elt="this",
                      hx_indicator="#loading-refine"),
                hx_post="/refine",
                hx_target="#refined",
                hx_swap="innerHTML"
            ),
            Div(Span("🧠 Refining your prompt..."),
                id="loading-refine", style="display: none; text-align: center; color: #007bff; padding: 1rem;"),
            Div(id="refined"),
            
            # Show iteration history
            H3(f"Iteration {len(iterations)}"),
            Details(
                Summary("View History"),
                *[Div(
                    Strong(f"Iteration {i+1}:"),
                    Pre(it["system_prompt"], style="background: #f9f9f9; padding: 0.5em;"),
                    style="margin: 0.5em 0;"
                ) for i, it in enumerate(iterations)]
            )
        )
    except Exception as e:
        return Div(
            P(f"Error: {str(e)}", style="color: red;"),
            P("Check your API key and model selection.")
        )

@rt("/refine")
async def post(feedback: str, current_system: str, last_response: str, 
               user_prompt: str, model: str, goal: str):
    """Refine the system prompt based on feedback"""
    try:
        refined = refine_prompt(current_system, feedback, last_response, goal)
        
        return Div(
            H4("Refined System Prompt:"),
            Pre(refined, style="background: #e8f5e9; padding: 1em; white-space: pre-wrap;"),
            
            Form(
                Hidden(name="system_prompt", value=refined),
                Hidden(name="user_prompt", value=user_prompt),
                Hidden(name="model", value=model),
                Hidden(name="goal", value=goal),
                Button(Span("✨ Test Refined Prompt", cls="btn-text"), 
                      type="submit", hx_disabled_elt="this",
                      style="background: #4CAF50;"),
                hx_post="/test",
                hx_target="#results",
                hx_swap="innerHTML"
            ),
            
            P(Em("Tip: Click 'Test Refined Prompt' to try the new version, or manually edit it in the form above."))
        )
    except Exception as e:
        return Div(P(f"Refinement error: {str(e)}", style="color: red;"))

serve()

