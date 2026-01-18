# src/client.py
import os
from openai import OpenAI
from .config import CONFIG
import logging

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

# Use the new model
MODEL_NAME = "z-ai/glm-4.5-air:free"

def call_llm(prompt: str) -> str:
    """Calls the LLM with the given prompt."""
    try:
        print(f"[DEBUG SDK] Sending prompt to LLM ({MODEL_NAME}): {prompt[:100]}...") # Log first 100 chars of prompt + model
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            timeout=30.0, # Optional timeout
        )

        # Check if choices is empty or if the first choice doesn't have the expected structure
        if not response.choices:
            print("[ERROR SDK] LLM response has no choices.")
            raise ValueError("LLM response has no choices.")
        
        first_choice = response.choices[0]
        if not hasattr(first_choice, 'message') or not hasattr(first_choice.message, 'content'):
             print(f"[ERROR SDK] LLM response choice is malformed. Choice: {first_choice}")
             raise ValueError(f"LLM response choice is malformed. Choice: {first_choice}")

        return first_choice.message.content
    except Exception as e:
        print(f"[EXCEPTION SDK] Error calling LLM: {e}")
        # Log the full traceback for better debugging if needed
        import traceback
        traceback.print_exc()
        raise e # Re-raise to be handled by caller/retry logic