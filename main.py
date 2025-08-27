from fasthtml.common import *
import openai
from datetime import datetime
from litellm import completion

# Initialize FastHTML app
app, rt = fast_app()

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
    return Titled("Prompt Refinement Tool",
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
                
                Button("Test Prompt", type="submit", hx_disabled_elt="this"),
            ),
            hx_post="/test",
            hx_target="#results",
            hx_swap="innerHTML"
        ),
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
                Button("Refine System Prompt", type="submit", hx_disabled_elt="this"),
                hx_post="/refine",
                hx_target="#refined",
                hx_swap="innerHTML"
            ),
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
                Button("Test Refined Prompt", type="submit", 
                      style="background: #4CAF50; color: white; padding: 0.5em 1em;", hx_disabled_elt="this"),
                hx_post="/test",
                hx_target="#results",
                hx_swap="innerHTML"
            ),
            
            P(Em("Tip: Click 'Test Refined Prompt' to try the new version, or manually edit it in the form above."))
        )
    except Exception as e:
        return Div(P(f"Refinement error: {str(e)}", style="color: red;"))

serve()

