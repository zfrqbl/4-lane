# streamlit_app.py
import streamlit as st
import os
import time # Import time for cooldown calculation
from dotenv import load_dotenv # Import load_dotenv explicitly
import re # Import re for parsing judge verdict

# --- Import necessary functions and classes ---
from src.config import CONFIG
from src.rate_limiter import GlobalRateLimiter
from src.models import PipelineState # Import PipelineState
from src.validators import validate_input_specification # Import validator
from src.architect import run_architect_stage
from src.stripper import run_stripper_stage
from src.worker import run_worker_stage
from src.judge import run_judge_stage # Import the missing function

# --- Import tenacity decorators ---
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
# ----------------------------------
# ---------------------------------------------


# load the .env file at the start of the script
load_dotenv()

# Check immediately if the API key is available in the environment
ENV_API_KEY_PRESENT = bool(os.getenv("OPENROUTER_API_KEY"))

if not ENV_API_KEY_PRESENT:
    # If the key is not in .env, show an error in the main UI and stop execution
    st.error("OpenRouter API Key not found. Please configure it in the '.env' file in the project root directory.")
    st.stop() # Stop execution if the key is not found

# At this point, we know the key is in the environment, so api_key_set is True
st.session_state.api_key_set = True

# Initialize other session state variables only if the key is present
if 'pipeline_state' not in st.session_state:
    st.session_state.pipeline_state = PipelineState(specification="")
if 'last_run_time' not in st.session_state:
    st.session_state.last_run_time = 0

# Rate Limiter Instance
rate_limiter = GlobalRateLimiter(cooldown_period=CONFIG.system.global_cooldown)

# --- Main App UI ---
st.title("_LANE_PRO_: AI-Powered Project Generator")

specification = st.text_area(
    "Enter your project specification:",
    value=st.session_state.pipeline_state.specification,
    height=200,
    max_chars=CONFIG.system.input_char_limit
)

col1, col2 = st.columns([1, 1])
with col1:
    # The run button should now be enabled as the key is confirmed to be present
    run_button = st.button("Run Pipeline", disabled=not st.session_state.api_key_set)
with col2:
    reset_button = st.button("Reset")

if reset_button:
    st.session_state.pipeline_state = PipelineState(specification="")
    st.session_state.last_run_time = 0
    st.rerun()

if run_button:
    # Validate input first
    is_valid, error_msg = validate_input_specification(specification)
    if not is_valid:
        st.error(error_msg)
    else:
        # Update spec in session state
        st.session_state.pipeline_state.specification = specification
        current_time = time.time()

        # Check cooldown
        elapsed_since_last_run = current_time - st.session_state.last_run_time
        if elapsed_since_last_run < CONFIG.system.global_cooldown:
            st.warning(f"Please wait. Cooldown active. Next run possible in {CONFIG.system.global_cooldown - int(elapsed_since_last_run)} seconds.")
        else:
            # Reset state for new run
            st.session_state.pipeline_state = PipelineState(specification=specification)
            # Inform the rate limiter about the call
            rate_limiter.wait_if_needed()
            st.session_state.last_run_time = time.time()

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Define the retry decorator - Now properly imported
            @retry(stop=stop_after_attempt(CONFIG.system.max_retries), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
            def safe_llm_call(func, *args):
                return func(*args)

            try:
                # Stage 1: Architect
                status_text.text("Running Architect Stage...")
                raw_tasks_json = safe_llm_call(run_architect_stage, specification)
                st.session_state.pipeline_state.plan = raw_tasks_json # Store raw output
                progress_bar.progress(25)

                # Check for error from Architect (now checking for JSON error format)
                if '"error"' in raw_tasks_json.lower() and 'vague' in raw_tasks_json.lower():
                     st.session_state.pipeline_state.error_occurred = True
                     st.session_state.pipeline_state.error_message = raw_tasks_json
                     st.session_state.pipeline_state.final_output = raw_tasks_json
                     st.success("Pipeline completed with an early error from the Architect stage.")
                     st.write("**Final Output:**")
                     st.code(st.session_state.pipeline_state.final_output, language="json") # Changed language to json
                     st.stop()

                # Stage 2: Strip Plan (Tasks JSON) - This stage might not be strictly necessary anymore
                # if the Architect is already asked to return clean JSON, but keeping for consistency.
                status_text.text("Running Stripper Stage (Task List)...")
                tasks_json = safe_llm_call(run_stripper_stage, raw_tasks_json)
                st.session_state.pipeline_state.stripped_plan = tasks_json
                progress_bar.progress(50)

                # Stage 3: Worker - Pass the JSON task list and text
                status_text.text("Running Worker Stage...")
                implementation_result = safe_llm_call(run_worker_stage, tasks_json) # Pass the JSON object
                st.session_state.pipeline_state.implementation_result = implementation_result
                progress_bar.progress(75)

                # Stage 4: Judge
                status_text.text("Running Judge Stage...")
                judge_verdict_raw = safe_llm_call(run_judge_stage, specification, implementation_result)
                st.session_state.pipeline_state.judge_verdict = judge_verdict_raw
                progress_bar.progress(90)

                # --- Parse Judge Verdict ---
                score_match = re.search(r'Score \(out of 10\):\s*(\d+)', judge_verdict_raw)
                discrepancy_match = re.search(r'Discrepancy:\s*(.*?)(?:\n|$)', judge_verdict_raw, re.DOTALL)

                score = score_match.group(1) if score_match else "N/A"
                discrepancy = discrepancy_match.group(1).strip() if discrepancy_match else "N/A"

                # Determine final output based on judge's verdict (optional, can store raw verdict)
                st.session_state.pipeline_state.final_output = judge_verdict_raw

                progress_bar.progress(100)
                status_text.text("Pipeline Complete!")
                st.success("Pipeline finished successfully!")

                # --- Display Concise Output Based on New Requirement ---
                st.subheader("Job Summary:")
                
                # 1. Display Score
                col_score = st.columns([1])[0] # Single column for score
                col_score.metric(label="Score", value=f"{score}/10")

                # 2. Display Worker's Output
                st.write("**Worker's Output:**")
                st.code(implementation_result, language="text") # Or whatever language is appropriate

                # 3. Display Judge's Analysis/Response (Full Verdict)
                st.write("**Judge's Analysis:**")
                st.code(judge_verdict_raw, language="text")

                # 4. Display Discrepancy (<50 words)
                st.write(f"**Discrepancy (<50 words):** {discrepancy}")


            except Exception as e:
                print(f"[STREAMLIT OUTER EXCEPT] Final error caught: {e}")
                print(f"[STREAMLIT OUTER EXCEPT] Type: {type(e)}")
                import traceback
                traceback.print_exc()
                st.error(f"An error occurred during the pipeline execution after {CONFIG.system.max_retries} attempts: {str(e)}")
                st.session_state.pipeline_state.error_occurred = True
                st.session_state.pipeline_state.error_message = str(e)

