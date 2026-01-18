
# src/stripper.py
from .config import CONFIG
from .client import call_llm

def run_stripper_stage(input_text: str) -> str:
    """Runs the Stripper stage of the pipeline."""
    prompt_template = CONFIG.prompts.stripper
    prompt = prompt_template.format(input_text=input_text)
    response = call_llm(prompt)
    return response.strip() # Ensure leading/trailing whitespace is removed again