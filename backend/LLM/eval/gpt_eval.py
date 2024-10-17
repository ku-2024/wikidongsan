import openai
import os
import pandas as pd
import logging
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    filename="evaluation_results.log",  # 로그 파일 이름
    level=logging.INFO,                 # 로그 레벨 설정 (INFO 이상 로그 기록)
    format="%(asctime)s - %(levelname)s - %(message)s"  # 로그 출력 형식
)

# Initialize OpenAI client with API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Prompt template for evaluation
EVALUATION_PROMPT_TEMPLATE = """
You will be given one summary written for an article. Your task is to rate the summary on one metric.
Please make sure you read and understand these instructions very carefully. 
Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

{criteria}

Evaluation Steps:

{steps}

Example:

Source Text:

{document}

Summary:

{summary}

Evaluation Form (scores ONLY):

- {metric_name}
"""

# Evaluation criteria and steps
evaluation_metrics = {
    "Consistency": ("""
Consistency(1-5) - the factual alignment between the summary and the summarized source. 
A factually consistent summary contains only statements that are entailed by the source document. 
Annotators were also asked to penalize summaries which contained hallucinated facts.
""", """
1. Read the article carefully and identify the main facts and details it presents.
2. Read the summary and compare it to the article. Check if the summary contains any factual errors that are not supported by the article.
3. Assign a score for consistency based on the Evaluation Criteria.
""")
}

# Function to read file contents
def read_file(filepath):
    """Reads file content and returns it."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# Function to get evaluation score from OpenAI's GPT model, with retry logic for rate limits
def get_geval_score(criteria, steps, document, summary, metric_name):
    prompt = EVALUATION_PROMPT_TEMPLATE.format(
        criteria=criteria,
        steps=steps,
        metric_name=metric_name,
        document=document,
        summary=summary
    )

    while True:
        try:
            # Correct API call using openai.ChatCompletion.create
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Use the correct model
                messages=[{"role": "user", "content": prompt}],
                temperature=2,
                max_tokens=5,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response['choices'][0]['message']['content'].strip()  # Adjust for chat-based response format

        except openai.error.RateLimitError as e:
            logging.warning(f"Rate limit error: {e}. Retrying after delay...")
            # Extract retry time if available, otherwise use a default delay
            retry_after = getattr(e, 'retry_after', 2)  # 기본 2초 대기
            time.sleep(retry_after)  # 대기 후 재시도
        except Exception as e:
            logging.error(f"Error during API call: {e}")
            return None

# Set paths for source documents and summaries
source_document_dir = "./LLM/processed_data/HelioCity/1/"
summary_dir = "./LLM/summary/HelioCity/Sum_Hel/"
source_document_paths = [
    os.path.join(source_document_dir, f"HelioCity_Label_Group_{i}_reviews_only.txt") for i in range(1, 9)
]
summary_paths = [
    [os.path.join(summary_dir, f"Label_Summary_{i}_{model}.txt") if model else os.path.join(summary_dir, f"Label_Summary_{i}.txt")
     for model in ["base", "gemma", "Llama3", ""]] 
    for i in range(1, 9)
]

# Perform evaluations and log the results
for i, source_document_path in enumerate(source_document_paths):
    source_document = read_file(source_document_path)  # Read source document

    # Evaluate each summary for the given source document
    for model_idx, summary_path in enumerate(summary_paths[i]):
        summary_name = ["base", "gemma", "Llama3", "default"][model_idx]  # Model name
        summary = read_file(summary_path)  # Read summary

        # Perform evaluations for each metric
        for eval_type, (criteria, steps) in evaluation_metrics.items():
            score = get_geval_score(criteria, steps, source_document, summary, eval_type)
            if score is not None:
                # Log the result
                logging.info(f"Evaluation: {eval_type}, Model: {summary_name}, Score: {score}")
