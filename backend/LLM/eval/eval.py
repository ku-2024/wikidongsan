from rouge import Rouge
from nltk.translate import meteor_score
import sacrebleu
from bert_score import score as bertscore
import os
import nltk
import logging

# NLTK 데이터 다운로드 (필요한 경우)
nltk.download('wordnet')
nltk.download('punkt')

# 로그 설정 (로그 파일에 저장)
logging.basicConfig(filename="evaluation_log.txt", level=logging.INFO, 
                    format="%(asctime)s - %(message)s")


def read_file(filepath):
    """파일을 읽고 내용을 반환"""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def rouge_l_score(summary, reference):
    """ROUGE-L 스코어 계산"""
    rouge = Rouge()
    scores = rouge.get_scores(summary, reference, avg=True)
    return scores['rouge-l']['f']  # ROUGE-L의 F1 스코어만 반환


def bleu_score(summary, reference):
    """BLEU 스코어 계산 (sacrebleu 사용)"""
    return sacrebleu.corpus_bleu([summary], [[reference]]).score


def meteor_score_fn(summary, reference):
    """METEOR 스코어 계산"""
    return meteor_score.single_meteor_score(reference, summary)


def bert_score_fn(summary, reference):
    """BERTScore 계산 (다국어 모델 사용)"""
    P, R, F1 = bertscore([summary], [reference], lang="ko")  # 한국어로 설정
    return F1.mean().item()  # F1 스코어만 반환


def evaluate_summary(generated_summary_path, reference_summary):
    """단일 요약 결과를 평가"""
    generated_summary = read_file(generated_summary_path)
    
    # ROUGE-L, BLEU, BERTScore, METEOR 스코어 계산
    rouge_l_f1 = rouge_l_score(generated_summary, reference_summary)
    bleu = bleu_score(generated_summary, reference_summary)
    meteor = meteor_score_fn(generated_summary, reference_summary)
    bert_f1 = bert_score_fn(generated_summary, reference_summary)
    
    return {"rouge-l_f1": rouge_l_f1, "bleu": bleu, "meteor": meteor, "bert_f1": bert_f1}


def log_evaluation_results(model_name, evaluation_results):
    """평가 결과를 로그 파일에 저장 (F1 값만 로그)"""
    logging.info(f"Model: {model_name}")
    
    # ROUGE-L F1
    logging.info(f"ROUGE-L F1: {evaluation_results['rouge-l_f1']:.4f}")
    
    # BLEU
    logging.info(f"BLEU: {evaluation_results['bleu']:.4f}")
    
    # METEOR
    logging.info(f"METEOR: {evaluation_results['meteor']:.4f}")
    
    # BERTScore F1
    logging.info(f"BERTScore F1: {evaluation_results['bert_f1']:.4f}")
    
    logging.info("-" * 80)


# 경로 설정
reference_summary_dir = "./summary/HelioCity/Sum_Hel/"
reference_summary_paths = [
    os.path.join(reference_summary_dir, f"Label_Summary_{i}_HT.txt") for i in range(1, 9)
]

model_summary_dir = "./summary/HelioCity/Sum_Hel/"
model_names = ["base", "gemma", "Llama3", ""]  # 모델별 이름 정의

# 모델별 점수 누적 변수 초기화
cumulative_scores_by_model = {
    "base": {"rouge-l_f1": 0, "bleu": 0, "meteor": 0, "bert_f1": 0, "count": 0},
    "gemma": {"rouge-l_f1": 0, "bleu": 0, "meteor": 0, "bert_f1": 0, "count": 0},
    "Llama3": {"rouge-l_f1": 0, "bleu": 0, "meteor": 0, "bert_f1": 0, "count": 0},
    "solar_ours": {"rouge-l_f1": 0, "bleu": 0, "meteor": 0, "bert_f1": 0, "count": 0},
}

model_summary_paths = [
    [os.path.join(model_summary_dir, f"Label_Summary_{i}_{model}.txt") if model else os.path.join(model_summary_dir, f"Label_Summary_{i}.txt")
     for model in model_names]
    for i in range(1, 9)
]

# 각 참조 요약 및 모델 요약 파일 평가
for i, reference_summary_path in enumerate(reference_summary_paths):
    # 기준이 되는 참조 요약 읽기
    reference_summary = read_file(reference_summary_path)
    
    # 모델별 요약 파일 평가
    for model_idx, generated_summary_path in enumerate(model_summary_paths[i]):
        model_name = model_names[model_idx] if model_names[model_idx] else "solar_ours"
        evaluation_results = evaluate_summary(generated_summary_path, reference_summary)
        
        # 점수 누적
        cumulative_scores_by_model[model_name]["rouge-l_f1"] += evaluation_results["rouge-l_f1"]
        cumulative_scores_by_model[model_name]["bleu"] += evaluation_results["bleu"]
        cumulative_scores_by_model[model_name]["meteor"] += evaluation_results["meteor"]
        cumulative_scores_by_model[model_name]["bert_f1"] += evaluation_results["bert_f1"]
        cumulative_scores_by_model[model_name]["count"] += 1
        
        # 로그 저장
        log_evaluation_results(model_name, evaluation_results)

# 모델별 평균 계산 및 출력
for model_name, scores in cumulative_scores_by_model.items():
    if scores["count"] > 0:
        print(f"{model_name} 모델 평균 평가 점수:")
        print(f"ROUGE-L F1 평균: {scores['rouge-l_f1'] / scores['count']:.4f}")
        print(f"BLEU 평균: {scores['bleu'] / scores['count']:.4f}")
        print(f"METEOR 평균: {scores['meteor'] / scores['count']:.4f}")
        print(f"BERTScore F1 평균: {scores['bert_f1'] / scores['count']:.4f}")
        print("-" * 80)
