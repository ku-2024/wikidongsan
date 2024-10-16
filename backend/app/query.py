import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models import AptReview, AptTrade, AptInfo, AptReviewSummary, AptReviewEmotion, AptCombSummary
from fastapi import HTTPException
from typing import Optional
import os
from LLM.langchain_doc import RAGSystem
def insert_apt_info(session: Session, filename: str):
    info_df = pd.read_csv(filename, na_values=['nan', 'NaN', 'NAN', ''])
    info_df = info_df.where(pd.notnull(info_df), None)
    
    for index, row in info_df.iterrows():
        info = AptInfo(
            apt_code=row['apt_code'],
            apt_name=row['apt_name'] if pd.notnull(row['apt_name']) else None,
            total_households=row['total_households'] if pd.notnull(row['total_households']) else None,
            completion_date=row['completion_date'] if pd.notnull(row['completion_date']) else None,
            district=row['district'] if pd.notnull(row['district']) else None,
            total_buildings=int(row['total_buildings']) if pd.notnull(row['total_buildings']) else None,
            land_address=row['land_address'] if pd.notnull(row['land_address']) else None,
            road_address=row['road_address'] if pd.notnull(row['road_address']) else None,
            latitude=str(row['latitude']) if pd.notnull(row['latitude']) else None,
            longitude=str(row['longitude']) if pd.notnull(row['longitude']) else None,
            construction_company=row['construction_company'] if pd.notnull(row['construction_company']) else None,
            heating_type=row['heating_type'] if pd.notnull(row['heating_type']) else None,
            max_floor=int(row['max_floor']) if pd.notnull(row['max_floor']) else None,
            min_floor=int(row['min_floor']) if pd.notnull(row['min_floor']) else None,
            parking_per_household=str(row['parking_per_household']) if pd.notnull(row['parking_per_household']) else None,
            area_list=row['area_list'] if pd.notnull(row['area_list']) else None,
        )
        session.add(info)
    session.commit()

def insert_apt_reviews(session: Session, filename: str):
    review_df = pd.read_csv(filename)
    for _, row in review_df.iterrows():
        review = AptReview(
            apt_code=row['apt_code'],
            category=row['category'],
            review=row['Review'].replace("\n", " ")
        )
        session.add(review)
    session.commit()

def insert_apt_review_summary(session: Session, filename: str):
    review_df = pd.read_csv(filename)
    for _, row in review_df.iterrows():
        review = AptReviewSummary(
            apt_code=row['apt_code'],
            # create_date=pd.Timestamp.now().strftime('%Y-%m-%d'),
            category=row['category'], 
            review=row['review'].replace("\n", " ")
        )
        session.add(review)
    session.commit()

def insert_apt_review_emo(session: Session, filename: str):
    review_df = pd.read_csv(filename)
    for _, row in review_df.iterrows():
        review = AptReviewEmotion(
            apt_code=row['apt_code'],
            emotion=row['emotion'],
            category=row['category'], 
            review=row['review'].replace("\n", " ")
        )
        session.add(review)
    session.commit()

def insert_apt_trades(session: Session):
    trade_df = pd.read_csv('data/apt_trade/Apt_transaction_result.csv')
    for _, row in trade_df.iterrows():
        trade = AptTrade(
            apt_code=row['apt_code'],
            apt_sq=row['apt_sq'],
            avg_price=row['avg_price'],
            top_avg_price=row['top_avg_price'],
            bottom_avg_price=row['bottom_avg_price'],
            recent_avg=row['recent_avg'],
            recent_top=row['recent_top'],
            recent_bottom=row['recent_bottom'],
            trade_trend=row['trade_trend'],
            price_trend=row['price_trend']
        )
        session.add(trade)
    session.commit()

def get_apt_data(apt_code: str, db: Session):
    apt_name = db.execute(
        select(AptInfo.apt_name).filter(AptInfo.apt_code == apt_code)
    ).scalar_one_or_none()

    if apt_name is None:
        return {'status': 200, 'data': {'apt_code': apt_code, 'apt_name': None, 'reviews': [], 'trades': []}}

    reviews = db.execute(
        select(AptReview.category, AptReview.review)
        .filter(AptReview.apt_code == apt_code)
        .order_by(AptReview.category)
    )
    reviews = reviews.mappings().all()
    review_list = [{'category': review['category'], 'review': review['review']} for review in reviews]

    result = db.execute(
        select(AptTrade.apt_sq, AptTrade.top_avg_price, AptTrade.bottom_avg_price, AptTrade.avg_price)
        .filter(AptTrade.apt_code == apt_code)
        .order_by(AptTrade.apt_sq)
    )
    trades = result.mappings().all()
    trade_list = [
        {
            'apt_sq': trade['apt_sq'],
            'avg_price': trade['avg_price'],
            'top_avg_price': trade['top_avg_price'],
            'bottom_avg_price': trade['bottom_avg_price'],
        }
        for trade in trades
    ]

    return {
        'status': 200,
        'data': {
            'apt_code': apt_code,
            'apt_name': apt_name,
            'reviews': review_list,
            'trades': trade_list
        }
    }

def get_all_name_sq(db: Session):
    result = db.execute(
        select(AptInfo.apt_name, AptInfo.apt_code, AptTrade.apt_sq)
        .join(AptTrade, AptInfo.apt_code == AptTrade.apt_code)
    )
    results = result.mappings().all()
    data = [{'apt_code': row['apt_code'], 'apt_name': row['apt_name'], 'apt_sq': f"{row['apt_sq']}㎡"} for row in results]
    return {'status': 200, 'data': data}

def get_all_name_code(db: Session, search_str: Optional[str] = None, page: int = 1, page_size: int = 10):
    if page < 1:
        return {'status': 400, 'message': "Page number must be greater than 0"}
    
    offset = (page - 1) * page_size
    base_query = select(AptInfo)

    if search_str:
        base_query = base_query.filter(AptInfo.apt_name.contains(search_str))
    
    total_query = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(total_query) or 0
    total_pages = (total + page_size - 1) // page_size if total else 0

    query = (
        base_query.with_only_columns(
            AptInfo.apt_name, AptInfo.apt_code, AptInfo.latitude, AptInfo.longitude, AptInfo.land_address, AptInfo.road_address
        )
        .offset(offset)
        .limit(page_size)
    )
    
    result = db.execute(query)
    results = result.mappings().all()
    data = [
        {
            'apt_name': r['apt_name'],
            'apt_code': r['apt_code'],
            'latitude': r['latitude'],
            'longitude': r['longitude'],
            'land_address': r['land_address'],
            'road_address': r['road_address']
        } for r in results
    ]
    
    return {
        'status': 200,
        'data': data,
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages
    }

def get_region_apt_data(db: Session):
    result = db.execute(
        select(
            AptInfo.apt_name, AptInfo.apt_code, AptTrade.avg_price, AptTrade.top_avg_price, AptTrade.bottom_avg_price, AptTrade.apt_sq
        ).join(AptTrade, AptInfo.apt_code == AptTrade.apt_code)
    )
    results = result.mappings().all()
    data = [
        {
            'apt_name': row['apt_name'],
            'apt_code': row['apt_code'],
            'apt_sq': row['apt_sq'],
            'avg_price': row['avg_price']
        } for row in results
    ]
    return {'status': 200, 'data': data}

def get_review_summary(apt_code: str, db: Session):
    apt_name = db.execute(
        select(AptInfo.apt_name).filter(AptInfo.apt_code == apt_code)
    ).scalar_one_or_none()

    if apt_name is None:
        return {'status': 200, 'data': {'apt_code': apt_code, 'apt_name': None, 'reviews': []}}

    result = db.execute(
        select(AptReviewSummary.category, AptReviewSummary.review)
        .filter(AptReviewSummary.apt_code == apt_code)
        .order_by(AptReviewSummary.category)
    )
    
    results = result.mappings().all()
    data = [{'category': row['category'], 'review': row['review']} for row in results]
    return {
        'status': 200,
        'data': {
            'apt_name': apt_name,
            'apt_code': apt_code,
            'reviews': data
        }
    }


def get_review_emotion(apt_code: str, db: Session):
    apt_name = db.execute(
        select(AptInfo.apt_name).filter(AptInfo.apt_code == apt_code)
    ).scalar_one_or_none()

    if apt_name is None:
        return {'status': 200, 'data': {'apt_code': apt_code, 'apt_name': None, 'reviews': []}}

    result = db.execute(
        select(AptReviewEmotion.category, AptReviewEmotion.emotion, AptReviewEmotion.review)
        .filter(AptReviewEmotion.apt_code == apt_code)
        .order_by(AptReviewEmotion.category)
    )
    
    results = result.mappings().all()
    data = [{'category': row['category'], 'emotion': row['emotion'], 'review': row['review']} for row in results]
    return {
        'status': 200,
        'data': {
            'apt_name': apt_name,
            'apt_code': apt_code,
            'reviews': data
        }
    }


def get_apt_info(apt_code: str, db: Session):
    result = db.execute(
        select(AptInfo.apt_name, 
               AptInfo.apt_code, 
               AptInfo.land_address,
               AptInfo.total_households, 
               AptInfo.completion_date, 
               AptInfo.construction_company,
               AptInfo.heating_type, 
               AptInfo.area_list).filter(AptInfo.apt_code==apt_code))
    results = result.mappings().all()
    data = [{'apt_code': row['apt_code'], 
             'apt_name': row['apt_name'], 
             'land_address': row['land_address'], 
             'total_households': f"{row['total_households']}", 
             'completion_date': f"{row['completion_date']}", 
             'construction_company': f"{row['construction_company']}", 
             'heating_type': f"{row['heating_type']}", 
             'area_list': f"{row['area_list']}"} for row in results]
    return {'status': 200, 'data': data}

def get_apt_all_data(apt_code: str, db: Session):
    # AptInfo 조회
    apt_info_query = select(AptInfo).filter(AptInfo.apt_code == apt_code)
    apt_info = db.execute(apt_info_query).scalar_one_or_none()

    # AptTrade 조회
    apt_trade_query = select(AptTrade).filter(AptTrade.apt_code == apt_code).order_by(AptTrade.apt_sq)
    apt_trades = db.execute(apt_trade_query).scalars().all()

    # AptReviewSummary 조회
    apt_review_summary_query = select(AptReviewSummary).filter(AptReviewSummary.apt_code == apt_code)
    apt_review_summaries = db.execute(apt_review_summary_query).scalars().all()

    # AptReviewEmotion 조회
    apt_review_emotion_query = select(AptReviewEmotion).filter(AptReviewEmotion.apt_code == apt_code)
    apt_review_emotions = db.execute(apt_review_emotion_query).scalars().all()

    return apt_info, apt_trades, apt_review_summaries, apt_review_emotions

def generate_apt_description(apt_info, apt_trades, apt_review_summaries, apt_review_emotions):
    cat_num_to_name = {
        "1": "환경", "2": "커뮤니티", "3": "동별 특징", "4": "상권", "5": "교통",
        "6": "학군", "7": "소음", "8": "주차", "9": "기타"
    }

    description = f"""
아파트명: {apt_info.apt_name}
위치: {apt_info.district} {apt_info.land_address} (도로명: {apt_info.road_address})
좌표: {apt_info.latitude}, {apt_info.longitude}
규모: 총 {apt_info.total_households}세대, {apt_info.total_buildings}개 동
입주일: {apt_info.completion_date}
건설사: {apt_info.construction_company}
난방: {apt_info.heating_type}
층수: {apt_info.min_floor}층 ~ {apt_info.max_floor}층
주차: 세대당 {apt_info.parking_per_household}대
제공 평형: {apt_info.area_list}
{generate_trade_info(apt_trades)}
{generate_review_summary(apt_review_summaries, cat_num_to_name)}
{generate_emotion_analysis(apt_review_emotions, cat_num_to_name)}
"""
    return description.strip()

def generate_trade_info(apt_trades):
    if not apt_trades:
        pass
    
    trade_info = []
    for trade in apt_trades:
        trade_info.append(f"{trade.apt_sq}평형: 평균 {trade.avg_price}, 최고 {trade.top_avg_price}, 최저 {trade.bottom_avg_price}")
        trade_info.append(f"  최근: 평균 {trade.recent_avg}, 최고 {trade.recent_top}, 최저 {trade.recent_bottom}")
        trade_info.append(f"  동향: 거래 {trade.trade_trend}, 가격 {trade.price_trend}")
    return "\n".join(trade_info)

def generate_review_summary(summaries, cat_map):
    if not summaries:
        pass
    
    return "\n".join(f"{cat_map.get(s.category, '기타')}: {s.review}" for s in summaries)

def generate_emotion_analysis(emotions, cat_map):
    if not emotions:
        pass
    
    return "\n".join(f"{cat_map.get(e.category, '기타')}: {e.emotion} - {e.review}" for e in emotions)

def post_chat_bot(rag_system: RAGSystem, apt_code: str, chat_input: str, db: Session):
    apt_description = db.scalar(select(AptCombSummary.description).filter(AptCombSummary.apt_code==apt_code))

    if apt_description is None:
        return {'status': 404, 'data': f"Apartment not found: {apt_code}"}
    try:
        rag_response = rag_system.get_response(chat_input, apt_description, apt_code)
        
        return {
            'status': 200,
            'data': rag_response
        }
    except Exception as e:
        print(f"Error in RAG system: {e}")
        return {
            'status': 500,
            'data': f"An error occurred while processing your request: {str(e)}"
        }

def create_apt_comb_summary(apt_code: str, descriptions: str, db: Session):
    new_summary = AptCombSummary(
        apt_code=apt_code,
        description=descriptions
    )
    db.add(new_summary)
    db.commit()
    return new_summary


def process_apt_data(apt_code: str, db: Session):
    # 데이터 조회
    apt_info, apt_trades, apt_review_summaries, apt_review_emotions = get_apt_all_data(apt_code, db)
    
    if not apt_info:
        return None  # 해당 apt_code에 대한 정보가 없는 경우
    
    # 설명 생성
    descriptions = generate_apt_description(apt_info, apt_trades, apt_review_summaries, apt_review_emotions)
    
    # AptCombSummary에 저장
    summary = create_apt_comb_summary(apt_code, descriptions, db)
    
    return summary


def insert_all_apt(db: Session):
    apt_codes = db.execute(select(AptInfo.apt_code)).scalars().all()
    print(f"총 {len(apt_codes)}개의 아파트 정보를 처리합니다.")
    for apt in apt_codes:
        try:
            process_apt_data(apt, db)
        except Exception as e:
            print(f"Apt_code {apt} INSERT FAIL:{str(e)}")
            return {'status': 400}
    return {'status': 200}
    


def get_one_apt_description(apt_code:str, db: Session):
    # description = db.scalar(select(AptCombSummary.description).filter(AptCombSummary.apt_code==apt_code))
    try:
        file_path = os.path.join("data", "rag", f"{apt_code}.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            add_description = file.read()
        description = add_description.replace("\n", "\n\n")
        # description+=add_description
    except:
        return ""
    return description

