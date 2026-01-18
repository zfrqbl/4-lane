# src/judge.py
from .config import CONFIG
from .client import call_llm

def run_judge_stage(specification: str, result: str) -> str:
    """Runs the Judge stage of the pipeline."""
    prompt_template = CONFIG.prompts.judge # This gets the string from YAML
    # The .format call below should correctly substitute {specification} and {result}
    # because they are the only unescaped placeholders in the YAML string.
    prompt = prompt_template.format(specification=specification, result=result)
    response = call_llm(prompt)
    return response