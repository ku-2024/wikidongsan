import os
import pandas as pd
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from vllm import LLM, SamplingParams
load_dotenv()
upstage_api_key = os.getenv("UPSTAGE_API_KEY")

assert "UPSTAGE_API_KEY" in os.environ, "Please set the UPSTAGE_API_KEY environment variable"

# Label 설명 dictionary
label_descriptions = {
    "1": "환경(단지, 조경)",
    "2": "커뮤니티",
    "3": "동별 특징",
    "4": "주변 상권",
    "5": "교통",
    "6": "학군",
    "7": "소음",
    "8": "주차",
    "9": "복합적"
}

# 상위 입력 디렉토리 설정
base_input_dir = "./processed_data"
base_output_dir = "./summary"

# few-shot prompt 템플릿 설정
few_shot_prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert in analyzing and summarizing user reviews related to apartment living environments. Take a step-by-step approach to analyze the reviews. Start by identifying and prioritizing information related specifically to residential comments. Then, carefully categorize the remaining content by relevant topics. For each category, extract the key points and provide a concise summary that highlights the most important aspects. All summaries must be provided in Korean."
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '{label_description}', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.

        Reviews:\n{combined_text}
        
        Summary:
        """
    )
])

def summarize_with_solar(combined_text, label, label_description):
    """Solar-1-Mini 모델을 사용한 요약 생성 함수"""
    llm = ChatUpstage(model="solar-1-mini-chat")
    chain = few_shot_prompt_template | llm | StrOutputParser()
    summary = chain.invoke({
        "label": label,
        "combined_text": combined_text,
        "label_description": label_description,
        "temperature": 0.25,
        "top_p": 0.85
    })
    return summary
def summarize_with_huggingface(model_name, combined_text, label_description):
    """Hugging Face 모델을 사용한 요약 생성 함수"""
    
    # 모델과 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # 대화형 요약을 위한 프롬프트 구성
    prompt = (f"You are an expert summarizer for Korean apartment reviews.\n"
              f"Summarize the following text in korean focusing on '{label_description}':\n"
              f"{combined_text}")

    # 파이프라인을 사용하여 요약 생성
    summarizer = pipeline("text-generation", model=model, tokenizer=tokenizer)
    
    # 텍스트 생성
    outputs = summarizer(prompt, max_length=1000, do_sample=True, temperature=0.25, top_p=0.85)
    
    # 결과 반환
    return outputs[0]['generated_text']

def summarize_with_vllm(model_name, combined_text, label_description):
    """vLLM을 사용한 요약 생성 함수 (LLama 또는 Gemma 모델 사용)"""
    llm = LLM(model=model_name)
    sampling_params = SamplingParams(temperature=0.25, top_p=0.85)
    
    conversation = [
        {"role": "system", "content": "You are an expert summarizer for Korean apartment reviews."},
        {"role": "user", "content": f"Summarize the following text in korean focusing on '{label_description}': {combined_text}"}
    ]
    
    outputs = llm.chat(conversation, sampling_params=sampling_params)
    return outputs[0].outputs[0].text

# 모델 선택을 위한 함수
def choose_model_and_summarize(combined_text, label, label_description, model_type):
    if model_type == "solar-1-mini":
        return summarize_with_solar(combined_text, label, label_description)
    elif model_type == "llama3.1":
        return summarize_with_huggingface("meta-llama/Meta-Llama-3.1-8B-Instruct", combined_text, label_description)
    elif model_type == "gemma2":
        return summarize_with_huggingface("google/gemma-2-9b-it", combined_text, label_description)
    else:
        raise ValueError("지원하지 않는 모델 타입입니다.")

# 상위 디렉토리의 모든 하위 폴더를 탐색
for complex_name in os.listdir(base_input_dir):
    complex_input_dir = os.path.join(base_input_dir, complex_name)  # 하위 폴더 경로 설정
    complex_output_dir = os.path.join(base_output_dir, complex_name)  # 하위 폴더에 맞는 출력 경로 설정
    
    if not os.path.isdir(complex_input_dir):
        continue
    
    # 출력 폴더 생성
    os.makedirs(complex_output_dir, exist_ok=True)

    # 하위 폴더 내 CSV 파일들을 탐색하여 처리
    for label_file in os.listdir(complex_input_dir):
        if label_file.startswith(f"{complex_name}_Label_Group_") and label_file.endswith(".csv"):
            label_path = os.path.join(complex_input_dir, label_file)
            try:
                data = pd.read_csv(label_path, sep=',', quotechar='"', error_bad_lines=False)

                label = label_file.split("_")[-1].split(".")[0]
                label_description = label_descriptions.get(label, "기타")

                combined_text = " ".join(data["Review"].astype(str).tolist())

                # 모델 선택 및 요약
                model_type = "llama3.1"  # llama, gemma, 또는 solar-1-mini로 설정 가능
                summary = choose_model_and_summarize(combined_text, label, label_description, model_type)

                # 요약 결과를 출력 디렉토리에 저장
                output_file = f"{complex_output_dir}/Label_Summary_{label}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(summary)

                print(f"Label {label}번에 대한 요약이 {output_file}에 저장되었습니다.")

            except Exception as e:
                print(f"파일 {label_file} 처리 중 오류 발생: {e}")
