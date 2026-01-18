# src/worker.py
from .config import CONFIG
from .client import call_llm

def run_worker_stage(task_list_and_text: str) -> str: # Renamed parameter for clarity
    """Runs the Worker stage of the pipeline."""
    prompt_template = CONFIG.prompts.worker
    prompt = prompt_template.format(task_list_and_text=task_list_and_text) # Updated key
    response = call_llm(prompt)
    return response