# LANE_PRO: AI-Powered Multi-Stage Task Executor

<!-- shields / badges -->
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-%5E1.30.0-informational)
![OpenAI](https://img.shields.io/badge/OpenAI_SDK-%5E1.5.0-green)
![Pydantic](https://img.shields.io/badge/pydantic-%5E2.0-blueviolet)
![Pyyaml](https://img.shields.io/badge/pyyaml-%5E6.0-yellow)
![Tenacity](https://img.shields.io/badge/tenacity-%5E8.2-orange)
![Rich](https://img.shields.io/badge/rich-%5E13.0-lightgrey)
![Requests](https://img.shields.io/badge/requests-%5E2.31-red)

<!-- short description -->
A Streamlit-based application implementing a stateless, multi-stage AI pipeline (Architect → Stripper → Worker → Judge) for robust task execution and evaluation, inspired by the concept of prompt drift mitigation.

## Table of Contents
- [Features](#features)
- [Core Idea & Concepts](#core-idea--concepts)
  - [Statelessness](#statelessness)
  - [Evaluation & The Judge](#evaluation--the-judge)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Model Selection & Provider](#model-selection--provider)
- [License](#license)
- [Credits](#credits)

## Features

* **Multi-Stage AI Pipeline:** Decomposes complex tasks into distinct phases (Architect, Stripper, Worker, Judge) for improved robustness.
* **Statelessness:** Each stage operates independently, consuming input and producing output without maintaining internal state across calls.
* **Prompt Drift Mitigation:** Uses the Judge stage to evaluate the Worker's output against original specifications, identifying deviations.
* **Concise Evaluation:** Provides a clear score, worker output, judge analysis, and a brief discrepancy report.
* **Synchronous Execution:** Processes tasks sequentially within a single user session.
* **Rate Limiting:** Enforces configurable cooldown periods between LLM calls to manage API usage.
* **Configurable via YAML:** Easily modify prompts, system parameters, and paths through `config/core.yaml`.

## Core Idea & Concepts

The core idea behind `LANE_PRO` is inspired by the challenge of **prompt drift** in large language models (LLMs). When complex instructions are passed through a single prompt or multiple chained calls, the model's interpretation can subtly shift, leading to inaccurate or unexpected results. This project implements a multi-lane workflow to mitigate this risk.

### Statelessness

Each component (Architect, Stripper, Worker, Judge) in the pipeline is designed to be **stateless**. This means that the execution of a stage depends solely on its inputs and the predefined prompt/configuration, not on any data stored from previous runs or other stages' internal workings. This design promotes modularity, simplifies debugging, and makes the system easier to reason about. The `PipelineState` object in the Streamlit app holds the data flowing through the stages for that specific run but is not persisted or shared between separate invocations of the entire pipeline.

### Evaluation & The Judge

The **Judge** stage plays a critical role in ensuring the quality and adherence of the final output. After the Worker stage executes the tasks derived from the Architect's plan (refined by the Stripper), the Judge receives both the original user specification and the Worker's output. It then evaluates the output against the initial request, assigning a score (out of 10) and providing a textual analysis that includes an "Expected Answer" and a "Discrepancy" report. This formal evaluation loop helps identify instances where the Worker may have deviated from the intended outcome, effectively acting as a check against prompt drift or misinterpretation in earlier stages.

## How It Works

1.  **User Input:** A user provides a project specification (e.g., "extract name and email from 'my name is q...'") in the Streamlit UI.
2.  **Architect Stage:** An LLM analyzes the specification and breaks it down into a structured JSON object containing the main text and a list of discrete tasks (e.g., "extract name", "extract email").
3.  **Stripper Stage:** Another LLM call cleans and standardizes the output from the Architect stage, ensuring the task list is in the correct format.
4.  **Worker Stage:** An LLM executes the tasks defined in the JSON object on the provided text, generating the final result.
5.  **Judge Stage:** An LLM compares the Worker's output against the original specification, evaluating its correctness.
6.  **Frontend Display:** The Streamlit app presents the Judge's score, the Worker's output, the Judge's analysis, and the discrepancy report in a concise format.

## Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/your-username/lane-pro.git
    cd lane-pro
    ```

2.  **Set up Virtual Environment (using `uv`):**
    ```bash
    # Install uv if you haven't already
    pip install uv

    # Create and activate virtual environment, install dependencies
    uv venv
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    uv pip install streamlit openai pydantic pyyaml tenacity rich python-dotenv tiktoken requests
    ```

3.  **Configure API Key:**
    *   Obtain an API key from [OpenRouter](https://openrouter.ai/keys).
    *   Create a file named `.env` in the root of the project directory (`lane-pro/.env`).
    *   Add your key to the file:
        ```ini
        OPENROUTER_API_KEY=your_openrouter_api_key_here
        ```

## Usage

1.  Activate your virtual environment (if not already active):
    ```bash
    source .venv/bin/activate # On Windows: .venv\Scripts\activate
    ```
2.  Run the Streamlit application:
    ```bash
    streamlit run streamlit_app.py
    ```
3.  Open your web browser and navigate to the URL displayed in the terminal (usually `http://localhost:8501`).
4.  Enter your project specification in the text area.
5.  Click the "Run Pipeline" button.
6.  View the concise results (Score, Worker Output, Judge Analysis, Discrepancy) in the UI.

## Configuration

*   **System Settings & Prompts:** Edit `config/core.yaml` to adjust parameters like global cooldown, retry attempts, input limits, and most importantly, the prompts used by each stage (Architect, Stripper, Worker, Judge).

## Model Selection & Provider

*   **Provider:** This system uses [OpenRouter](https://openrouter.ai/) to access a variety of Large Language Models (LLMs) through a unified API. An OpenRouter API key is required (see Installation).
*   **Changing the Model:** To use a different model supported by OpenRouter:
    1.  Navigate to the `src` directory.
    2.  Open the `client.py` file.
    3.  Locate the `MODEL_NAME` constant (e.g., `MODEL_NAME = "z-ai/glm-4.5-air:free"`).
    4.  Change the string value assigned to `MODEL_NAME` to the ID of the desired model available on OpenRouter (e.g., `"openai/gpt-4o-mini:free"` or `"anthropic/claude-3-haiku:beta"`).
    5.  Save the file. The application will use the newly specified model on the next run.

## License

This project is licensed under the [MIT License](LICENSE). See the `LICENSE` file for details. You are free to use, modify, and distribute this software.

## Credits

*   **Concept Inspiration:** The idea for this multi-lane workflow was inspired by a post on Reddit's r/PromptEngineering. Credit goes to user [FirefighterFine9544](https://www.reddit.com/u/FirefighterFine9544) for the original post: ["Prompt drift forced me into a multi-lane workflow — curious if this is already a thing"](https://www.reddit.com/r/PromptEngineering/comments/1q6049k/prompt_drift_forced_me_into_a_multilane_workflow/).
*   **Author:** Developed by [Zafar Iqbal (zfrqbl)](https://github.com/zfrqbl). <!-- Replace with your actual GitHub profile link if you have one -->
