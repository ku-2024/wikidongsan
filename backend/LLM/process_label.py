import os
import json
import csv
from langchain_core.prompts import ChatPromptTemplate
from langchain_upstage import ChatUpstage
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI

# Set Upstage LLM
upstage_api_key = os.getenv("UPSTAGE_API_KEY")

assert "UPSTAGE_API_KEY" in os.environ, "Please set the UPSTAGE_API_KEY environment variable"
client = OpenAI(
        base_url="https://api.upstage.ai/v1/solar"
    )
llm = ChatUpstage(model="solar-1-mini-chat")
# Set answer label
label_ans = ['1', '2', '3', '4', '5', '6', '7','8']

# Read Data
with open('./Gracium_2024.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    reviews = data["review"]

# Define Prompt
def get_prompt(review):
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You have to give the category number of the review sentence. Give me only the number. 1. Environment 2. Community 3. Neighborhood Characteristics 4. Surrounding Amenities 5. Transportation 6. School District 7. Noise 8. Parking 9. Others. Label it as ‘9’ if it is not entirely clear-cut or if it is related to price."),
            ("human", "The satisfaction level for building 209210 is excellent. The bus stop to Suseo Station is just a 5-minute walk, the recycling area is nearby, and there is a playground. We plan to live here long-term and raise our child because once the Wirye-Sinsa Line opens, there will be a direct route to Seoul, making it practically a station area"),
            ("ai", "3"),
            ("human", review),
        ]
    )
    return chat_prompt

# Get Preprocessed Review
pre_review=[]
for i,review in enumerate(reviews):
    # 전처리 수행
    if "?" in review:
        continue
    if "작성자" in review:
        continue
    if "블락" in review:
        continue
    if len(review)<10:
        continue
        
    # Set Translate Model
    stream = llm.chat.completions.create(
        model="solar-1-mini-translate-koen",
        messages=[
        {
            "role": "user",
            "content": "역과 바로 연결되고, 주차공간도 넉넉하고 어린이집 바로옆 초등학교 등등 모든게 장점입니다."
        },
        {
            "role": "assistant",
            "content": "It is directly connected to the station, has plenty of parking space, and is right next to a kindergarten and an elementary school. Everything about it is an advantage."
        },
        {
            "role": "user",
            "content": review
        }
        ],
        stream=True,
    )
    
    en_review = ''
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            en_review += chunk.choices[0].delta.content
    if en_review in pre_review:
        continue
    
    chat_prompt = get_prompt(en_review)
    chain = chat_prompt | llm | StrOutputParser()
    ans = chain.invoke({})
    print(review)
    print(en_review)
    print('['+ans+']')
    if ans in label_ans:
        pre_review.append([i+1, review, ans])

with open('./Gracium_label.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)

    writer.writerow(['Index', 'Review', 'Label'])

    writer.writerows(pre_review)

print("\n*** CSV File Done ***")
