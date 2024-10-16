from fastapi import FastAPI, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import get_db, init_db
from app.query import *
from LLM.langchain_doc import RAGSystem
from app.config import UPSTAGE_API_KEY

app = FastAPI()
rag_system = RAGSystem(api_key=UPSTAGE_API_KEY)
# Application startup
@app.on_event("startup")
def startup_event():
    init_db()  # Initialize the database

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/init-db")
def initialize_database():
    init_db(drop_and_create=True)
    return {"message": "Database initialized successfully"}

@app.post("/insertdata")
def insert_data(db: Session = Depends(get_db)):
    # Insert apt_info data first
    try:
        insert_apt_info(db, './data/apartment_data.csv')

        # Insert apt_review data
        review_dir = 'data/apt_review'
        for filename in os.listdir(review_dir):
            file_path = os.path.join(review_dir, filename)
            if os.path.isfile(file_path) and file_path.endswith('.csv'):
                insert_apt_reviews(db, file_path)
        
        # Insert apt_review_summary data
        review_sum_dir = 'data/apt_review_summ'
        for filename in os.listdir(review_sum_dir):
            file_path = os.path.join(review_sum_dir, filename)
            if os.path.isfile(file_path) and file_path.endswith('.csv'):
                insert_apt_review_summary(db, file_path)
        review_emo_dir = 'data/apt_review_emo'
        for filename in os.listdir(review_emo_dir):
            file_path = os.path.join(review_emo_dir, filename)
            if os.path.isfile(file_path) and file_path.endswith('.csv'):
                insert_apt_review_emo(db, file_path)
        # Insert apt_trade data
        insert_apt_trades(db)
        # Insert apt_descripion data
        insert_all_apt(db)
        return {"status": 200, "message": "Data insertion successful"}
    except Exception as e:
        return {"status": 400, "message": f"{e}"}
    
@app.get("/getdata/{apt_code}")
def get_data(apt_code: str, db: Session = Depends(get_db)):
    
    return get_apt_data(apt_code, db)

@app.get("/get/all-name-sq")
def get_all_names_and_sq(db: Session = Depends(get_db)):
    return get_all_name_sq(db)

@app.get("/get/all-name-code")
def get_all_names_and_code(page: int, size: int, search_str: str = None, db: Session = Depends(get_db)):
    return get_all_name_code(db=db, search_str=search_str, page=page, page_size=size)

@app.get("/get/name-price")
def get_all_names_and_prices(db: Session = Depends(get_db)):
    return get_region_apt_data(db)

@app.get("/get/review-summary/{apt_code}")
def get_apt_review_summary(apt_code: str, db: Session = Depends(get_db)):
    return get_review_summary(apt_code, db)

@app.get("/get/review-emotion/{apt_code}")
def get_apt_review_emotion(apt_code: str, db: Session = Depends(get_db)):
    return get_review_emotion(apt_code, db)

@app.get("/get/apt_info/{apt_code}")
def get_apt_code_info(apt_code: str, db: Session = Depends(get_db)):
    return get_apt_info(apt_code, db)

@app.post("/post/chatbot")
async def post_chat(apt_code: str, chat_input: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    APT_DESCRIPTION = get_one_apt_description(apt_code, db)
    print(f"""
            =================
            {APT_DESCRIPTION}
        """)
    if not APT_DESCRIPTION:
        APT_DESCRIPTION = db.scalar(select(AptCombSummary.description).filter(AptCombSummary.apt_code==apt_code))
    try:
        response = rag_system.get_response(input_text = chat_input, document = APT_DESCRIPTION, apt_code = apt_code)
        background_tasks.add_task(post_chat_bot, rag_system, apt_code, chat_input, db)
        return {"status": 200, "data": response}
    except Exception as e:
        return {"status": 400, "message": f"{e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)