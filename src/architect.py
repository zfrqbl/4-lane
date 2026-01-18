# src/architect.py
from .config import CONFIG
from .client import call_llm

def run_architect_stage(specification: str) -> str:
    """Runs the Architect stage of the pipeline."""
    prompt_template = CONFIG.prompts.architect
    prompt = prompt_template.format(specification=specification)
    response = call_llm(prompt)
    return response
