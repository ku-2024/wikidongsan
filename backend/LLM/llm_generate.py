import os
import pandas as pd
from dotenv import load_dotenv
from langchain_upstage import ChatUpstage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()
upstage_api_key = os.getenv("UPSTAGE_API_KEY")

assert "UPSTAGE_API_KEY" in os.environ, "Please set the UPSTAGE_API_KEY environment variable"

llm = ChatUpstage(model="solar-1-mini-chat")


# label 설명 dictionary
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
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '환경(단지, 조경)', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.

        Reviews:\n{Review_ref1}

        Summary: '조경이 아주 훌륭하고, 10년차가 넘어 나무가 무성해져 숲이나 공원으로 느껴져 출퇴근할때 기분이 좋습니다. 조경과 하늘가람 근린공원과, 온조마루 근린공원이 연결되어 있어 조경이 왠만한 공원 보다 좋습니다. 특히 보기 드문 평지 아파트에 중앙 통로가 있는 단지 모양이라 유모차를 끌고 산책하거나, 자전거 타기 좋습니다. 또 중통의 좋은 점은 밤 늦게 걸어도 무섭지 않다는 장점을 가지고 있습니다. 성내천 한강 그리고 올림픽공원과 매우 인접하여 다양한 산책 코스를 즐길 수 있습니다. 조금만 더 걸으면 롯데타워 지나서 석촌호수에서 운동할 수 있습니다. '
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '커뮤니티', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref2}
'

        Summary: '1단지 2단지 모두 헬스장, GX강의실이 존재합니다. 2단지 커뮤니티의 경우 210동과 211동 사이에 위치해 있으며, 골프연습장의 경우 1단지에만 존재합니다. 세대수에 비해 골프 연습할 수 있는 곳이 부족하여 기다리는 경우가 많습니다. 아이들 교육을 위한 아이두레터는 유아, 초등, 성인 클래스가 다양하게 존재하며, 성인들을 위한 수업인 성인영어회화, 오카리나 등 다양한 프로그램이 존재합니다. 피트니스 센터는 한달 이용요금이 3만원이고, 관리비에 고지되어 나옵니다.'
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '동별 특징', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref3}

        Summary: '33평 C타입의 경우 4베이에 남동 남서향이라 채광좋고 겨울에 엄청 따뜻합니다. 부엌 다용도실도 바닥까지 내려오는 큰 창문이라 생선고기 냄새나는 것들은 간편하게 처리가능하고, 빨래도 잘 마릅니다. 또한 햇빛이 잘 들고 통풍도 잘 됩니다. 26평형의 경우에도 광폭 발코니에 확장까지해서 요즘 신축 아파트 30평의 느낌이나고, 마찬가지로 32평 같은 경우에도 신축 40평대 느낌이 날 정도로 넓습니다. 성내천 라인의 1호 4호 중층 이상의 작은방 2개는 모두 한강뷰 나옵니다. 213동 1호라인인데 해가 거의 안들고 외풍이 심해 추운 단점이 있습니다. 3단지 고층 거실에서는 롯데타워 뷰가 나오고, 1단지 B타입중에는 한강뷰 나오는 타입도 있습니다.  3단지의 일부 매물은 올림픽 파크뷰와 롯데타워뷰가 보입니다. '
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '주변 상권', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref4}
'

        Summary: '바로 앞에 롯데타워가 있어서 장보러가거나 쇼핑하러가기 좋으며, 주변 신축아파트가 많아 상가 이용, 바로 앞에 아산 병원 인프라를 이용할 수 있습니다. 조금만 더 걸으면 송리단길이 위치해있습니다. 파크리오 바로 앞에 잠실4동 동사무소가 있어 편리하며 A상가에 롯데슈퍼, B상가에 GS슈퍼가 있어 도보로 이용하고 있고, 좀 많이 사려면 홈플러스, 롯데몰마트를 이용합니다. 방이 유흥가에서 멀어 애들 키우기 좋습니다. '
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '교통', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref5}

        Summary: '대치동까지 자차로 20분 걸립니다. 또한 올림픽 대로가 바로 앞에 있어 교통이 편하고, 모든동에서 지하로 10분 이내에 지하철역에 갈 수 있습니다. 2호선 8호선이 메인으로 이용할 수 있으며 소마 미술관쪽으로 가로질러가면 9호선이 있어서 편한 호선을 골라탈 수 있으며, 아파트에 3개의 버스정류장이 있습니다. 잠실나루역 3번출구(장미아파트쪽)에서 80미터거리(도보1분)에 택시들이 많이 있습니다. 잠실역에 가까워 늘 교통량이 많아 출퇴근시간대에는 많이 막히는 단점을 가지고 있습니다.'
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '학군', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref6}

        Summary: '단지내 초등학교가 잠실초와 잠현초 2개 있어 영유아, 초등학생 양육환경이 매우 우수합니다. 상가에 하구언이 많아 초등학생까지는 좋으나, 중학생때부터는 애매합니다. 이후 학원의 경우 대치동으로 많이 다니며 대치동으로 픽업 다닐 경우 20분정도의 시간이 소요됩니다. 남아의 경우 학군이 괜찮으나, 여아의 경우 중학교와 고등학교가 애매합니다. 여아들은 잠실중 – 한대부고(자사고) 다니며 특히 한대부고는 통학버스가 다닙니다. '
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '소음', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref7}

        Summary: '1단지 옆으로 2호선 지상철이 다녀 소음이 발생합니다. 특히 2호선의 경우 지하철 주기가 짧아 예민할 경우 조금 스트레스를 받을 수 있습니다. 지상철에 인접한 105동의 3호 4호 라인의 경우 창문 열면 잘 들립니다. 그러나 거실문 닫으면 하나도 안들립니다. 1호 2호라인은 전혀 안들리고, 고층으로 올라갈 경우 잘 안들립니다. 1단지 2단지 바깥쪽을 제외하고는 거슬리는 수준은 아닙니다. 층간소음때문에 싸우는 경우가 많으며, 특히 화장실의 경우 윗집의 물내리는 소리가 다 들립니다. 벽식 구조에다 슬래브도 얇아서 층간 소음이 다른 아파트보다 잘 들리는 편입니다.'
        """
    ),
    (
        "user",
        """
        [Instruction]
        You are a helpful assistant that summarizes and provides comprehensive insights based on user reviews about various aspects of an apartment complex. The reviews are categorized into topics such as environment, community, or transportation. Your task is to summarize these reviews to provide clear and concise information related to the topic of '{label_description}'.

        [Context]
        Summarize the reviews below in a detailed and comprehensive manner, focusing on key points related to '주차', using a professional and neutral tone to aggregate the opinions, highlighting important features and general sentiments expressed in the reviews in more than 9 sentences to ensure all perspectives and nuances are adequately captured. Do not make a newline or line break.
        Reviews:\n{Review_ref8}

        Summary: '저녁에는 조명이 어두워 각 동이 어디에 있는지 찾기가 힘듭니다. 1단지 2단지 3단지의 건설사가 달라서 지하주차장이 모두 연결되어있지 않습니다. 15년차가 넘은 준 신축 아파트이지만, 전기차 충전구역이 있고 추가적으로 한동당 2개정도의 컨센트 형식의 충전기가 있지만, 일반 차량이 주차하면 충전을 조금 힘들 수 있습니다. 세대당 1.4대 정도로 연식 대비 주차장은 넓고 좋습니다. 특히 동 근처 지하 1~2층에 항상 주차 가능하고, 주차장에서 엘리베이터가 자동으로 호출됩니다.'
        """
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


# 상위 디렉토리의 모든 하위 폴더를 탐색
for complex_name in os.listdir(base_input_dir):
    complex_input_dir = os.path.join(base_input_dir, complex_name)  # 하위 폴더 경로 설정
    complex_output_dir = os.path.join(base_output_dir, complex_name)  # 하위 폴더에 맞는 출력 경로 설정
    
    # 하위 폴더가 실제 폴더인지 확인 (파일이 아닌 폴더만 탐색)
    if not os.path.isdir(complex_input_dir):
        continue
    
    # 출력 폴더 생성
    os.makedirs(complex_output_dir, exist_ok=True)

    # 하위 폴더 내 CSV 파일들을 탐색하여 처리
    for label_file in os.listdir(complex_input_dir):
        # 파일이 Label_Group_ 패턴에 맞는지 확인
        if label_file.startswith(f"{complex_name}_Label_Group_") and label_file.endswith(".csv"):
            label_path = os.path.join(complex_input_dir, label_file)
            try:
                # CSV 파일 읽기
                data = pd.read_csv(label_path, sep=',', quotechar='"', error_bad_lines=False)

                # 파일 이름에서 라벨 번호 추출
                label = label_file.split("_")[-1].split(".")[0]
                label_description = label_descriptions.get(label, "기타")  # label 설명 가져오기

                # "Review" 열의 모든 텍스트를 결합
                combined_text = " ".join(data["Review"].astype(str).tolist())

                # 템플릿, LLM, 파서를 사용하여 체인 생성
                chain = few_shot_prompt_template | llm | StrOutputParser()

                # 체인을 사용하여 요약 생성하고 결과 저장
                summary = chain.invoke({
                    "label": label,
                    "combined_text": combined_text,
                    "label_description": label_description,
                    "temperature": 0.7,  # 낮추면 robust, 높이면 창의력이라 생각하면 됨
                    "top_p": 0.7         # temp로 만든 확률을 어디까지 고려할지
                })

                # 요약 결과를 출력 디렉토리에 저장
                output_file = f"{complex_output_dir}/Label_Summary_{label}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(summary)

                print(f"Label {label}번에 대한 요약이 {output_file}에 저장되었습니다.")

            except Exception as e:
                print(f"파일 {label_file} 처리 중 오류 발생: {e}")



            except Exception as e:
                print(f"파일 {label_file} 처리 중 오류 발생: {e}")

