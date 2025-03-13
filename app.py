import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from streamlit_extras.card import card
import random
import json
import os

# 페이지 설정
st.set_page_config(
    page_title="의학 용어 학습",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 20px;
        height: 3rem;
        background: linear-gradient(45deg, #4F46E5, #7C3AED);
        color: white;
        font-weight: bold;
    }
    .term-card {
        background: #f8f9fa;
        color: #000;  /* 글자색 검정으로 지정 */
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .stats-card {
        background: linear-gradient(45deg, #4F46E5, #7C3AED);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    .admin-card {
        background: #f1f5f9;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .calendar-day {
        background: #e2e8f0;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 2px;
    }
    .calendar-day-completed {
        background: linear-gradient(45deg, #4F46E5, #7C3AED);
        color: white;
    }
    .progress-container {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 기존 의학 용어 데이터베이스
nested_terms = {
    "기초 의학": {
        "해부학": [
            {"term": "Cerebrum", "definition": "대뇌"},
            {"term": "Medulla Oblongata", "definition": "연수"},
            {"term": "Cerebellum", "definition": "소뇌"},
            {"term": "Hypothalamus", "definition": "시상하부"},
            {"term": "Thalamus", "definition": "시상"},
            {"term": "Pons", "definition": "뇌교"},
            {"term": "Hippocampus", "definition": "해마"},
            {"term": "Amygdala", "definition": "편도체"},
            {"term": "Corpus Callosum", "definition": "뇌량"},
            {"term": "Brainstem", "definition": "뇌간"},
            # 추가 5개
            {"term": "Frontal Lobe", "definition": "전두엽"},
            {"term": "Parietal Lobe", "definition": "두정엽"},
            {"term": "Temporal Lobe", "definition": "측두엽"},
            {"term": "Occipital Lobe", "definition": "후두엽"},
            {"term": "Basal Ganglia", "definition": "기저핵"}
        ],
        "생리학": [
            {"term": "Homeostasis", "definition": "항상성"},
            {"term": "Metabolism", "definition": "대사"},
            {"term": "Osmosis", "definition": "삼투"},
            {"term": "Diffusion", "definition": "확산"},
            {"term": "Active Transport", "definition": "능동수송"},
            {"term": "Membrane Potential", "definition": "막전위"},
            {"term": "Action Potential", "definition": "활동전위"},
            {"term": "Synapse", "definition": "시냅스"},
            {"term": "Neurotransmitter", "definition": "신경전달물질"},
            {"term": "Receptor", "definition": "수용체"},
            # 추가 5개
            {"term": "Hormone", "definition": "호르몬"},
            {"term": "Enzyme", "definition": "효소"},
            {"term": "pH Balance", "definition": "산-염기 균형"},
            {"term": "Thermoregulation", "definition": "체온 조절"},
            {"term": "Blood Pressure Regulation", "definition": "혈압 조절"}
        ],
        "조직학": [
            {"term": "Epithelium", "definition": "상피조직"},
            {"term": "Connective Tissue", "definition": "결합조직"},
            {"term": "Muscle Tissue", "definition": "근육조직"},
            {"term": "Nervous Tissue", "definition": "신경조직"},
            {"term": "Adipose Tissue", "definition": "지방조직"},
            {"term": "Cartilage", "definition": "연골"},
            {"term": "Bone Tissue", "definition": "골조직"},
            {"term": "Blood", "definition": "혈액"},
            {"term": "Lymphatic Tissue", "definition": "림프조직"},
            {"term": "Mucous Membrane", "definition": "점막"},
            # 추가 5개
            {"term": "Tendon", "definition": "힘줄"},
            {"term": "Ligament", "definition": "인대"},
            {"term": "Elastic Tissue", "definition": "탄력성 조직"},
            {"term": "Reticular Tissue", "definition": "그물 조직"},
            {"term": "Serous Membrane", "definition": "장막"}
        ]
    },
    "임상 의학": {
        "순환기": [
            {"term": "Hypertension", "definition": "고혈압"},
            {"term": "Tachycardia", "definition": "빈맥"},
            {"term": "Bradycardia", "definition": "서맥"},
            {"term": "Arrhythmia", "definition": "부정맥"},
            {"term": "Myocardial Infarction", "definition": "심근경색"},
            {"term": "Angina Pectoris", "definition": "협심증"},
            {"term": "Heart Failure", "definition": "심부전"},
            {"term": "Atherosclerosis", "definition": "동맥경화증"},
            {"term": "Thrombosis", "definition": "혈전증"},
            {"term": "Embolism", "definition": "색전증"},
            # 추가 5개
            {"term": "Cardiac Output", "definition": "심박출량"},
            {"term": "Cardiomyopathy", "definition": "심근병증"},
            {"term": "Valvular Heart Disease", "definition": "심장판막질환"},
            {"term": "Peripheral Vascular Disease", "definition": "말초혈관질환"},
            {"term": "Stroke Volume", "definition": "일회박출량"}
        ],
        "호흡기": [
            {"term": "Dyspnea", "definition": "호흡곤란"},
            {"term": "Bronchitis", "definition": "기관지염"},
            {"term": "Pneumonia", "definition": "폐렴"},
            {"term": "Emphysema", "definition": "폐기종"},
            {"term": "Asthma", "definition": "천식"},
            {"term": "Tuberculosis", "definition": "결핵"},
            {"term": "Pleurisy", "definition": "흉막염"},
            {"term": "Pneumothorax", "definition": "기흉"},
            {"term": "Pulmonary Edema", "definition": "폐부종"},
            {"term": "Lung Cancer", "definition": "폐암"},
            # 추가 5개
            {"term": "Chronic Bronchitis", "definition": "만성 기관지염"},
            {"term": "Laryngitis", "definition": "후두염"},
            {"term": "Bronchiectasis", "definition": "기관지확장증"},
            {"term": "Pulmonary Fibrosis", "definition": "폐섬유화증"},
            {"term": "Respiratory Distress Syndrome", "definition": "호흡곤란 증후군"}
        ],
        "소화기": [
            {"term": "Gastritis", "definition": "위염"},
            {"term": "Hepatitis", "definition": "간염"},
            {"term": "Cholecystitis", "definition": "담낭염"},
            {"term": "Pancreatitis", "definition": "췌장염"},
            {"term": "Appendicitis", "definition": "충수염"},
            {"term": "Cirrhosis", "definition": "간경변"},
            {"term": "Peptic Ulcer", "definition": "소화성 궤양"},
            {"term": "Crohn Disease", "definition": "크론병"},
            {"term": "Ulcerative Colitis", "definition": "궤양성 대장염"},
            {"term": "Gallstone", "definition": "담석"},
            # 추가 5개
            {"term": "Gastroparesis", "definition": "위마비"},
            {"term": "Esophagitis", "definition": "식도염"},
            {"term": "Diverticulitis", "definition": "게실염"},
            {"term": "Gastroenteritis", "definition": "위장염"},
            {"term": "Hemorrhoids", "definition": "치질(치핵)"}
        ],
        "신경계": {
            "두뇌": [
                {"term": "Anencephaly", "definition": "무뇌증"},
                {"term": "Cerebral Palsy", "definition": "뇌성마비"},
                {"term": "Meningitis", "definition": "수막염"},
                {"term": "Brain Tumor", "definition": "뇌종양"},
                {"term": "Epilepsy", "definition": "간질"},
                {"term": "Encephalitis", "definition": "뇌염"},
                {"term": "Hydrocephalus", "definition": "수두증"},
                {"term": "Cerebral Hemorrhage", "definition": "뇌출혈"},
                {"term": "Multiple Sclerosis", "definition": "다발성 경화증"},
                {"term": "Brain Abscess", "definition": "뇌농양"},
                # 추가 5개
                {"term": "Parkinson's Disease", "definition": "파킨슨병"},
                {"term": "Alzheimer's Disease", "definition": "알츠하이머병"},
                {"term": "Subdural Hematoma", "definition": "경막하 혈종"},
                {"term": "Concussion", "definition": "뇌진탕"},
                {"term": "Transient Ischemic Attack", "definition": "일과성 허혈 발작"}
            ],
            "증상": [
                {"term": "Aphasia", "definition": "실어증"},
                {"term": "Apraxia", "definition": "실행증"},
                {"term": "Ataxia", "definition": "운동실조"},
                {"term": "Convulsion", "definition": "경련"},
                {"term": "Dizziness", "definition": "어지러움"},
                {"term": "Vertigo", "definition": "현기증"},
                {"term": "Coma", "definition": "혼수"},
                {"term": "Syncope", "definition": "실신"},
                {"term": "Neuralgia", "definition": "신경통"},
                {"term": "Paralysis", "definition": "마비"},
                # 추가 5개
                {"term": "Headache", "definition": "두통"},
                {"term": "Insomnia", "definition": "불면증"},
                {"term": "Neurogenic Shock", "definition": "신경인성 쇼크"},
                {"term": "Spasm", "definition": "근육 경련"},
                {"term": "Paresthesia", "definition": "감각 이상"}
            ]
        }
    },
    "이비인후과": {
        "귀": [
            {"term": "Otitis Media", "definition": "중이염"},
            {"term": "Tinnitus", "definition": "이명"},
            {"term": "Deafness", "definition": "난청"},
            {"term": "Labyrinthitis", "definition": "미로염"},
            {"term": "Acoustic Neuroma", "definition": "청신경종양"},
            {"term": "Otosclerosis", "definition": "이경화증"},
            {"term": "Vestibular Neuritis", "definition": "전정신경염"},
            {"term": "Meniere Disease", "definition": "메니에르병"},
            {"term": "Cochlear Implant", "definition": "인공와우"},
            {"term": "Presbycusis", "definition": "노인성난청"},
            # 추가 5개
            {"term": "Ear Barotrauma", "definition": "이압손상"},
            {"term": "Cholesteatoma", "definition": "진주종"},
            {"term": "Otorrhea", "definition": "이루(귀액)"},
            {"term": "Otalgia", "definition": "이통(귀 통증)"},
            {"term": "Perforated Eardrum", "definition": "고막 천공"}
        ],
        "코": [
            {"term": "Rhinitis", "definition": "비염"},
            {"term": "Sinusitis", "definition": "부비동염"},
            {"term": "Epistaxis", "definition": "비출혈"},
            {"term": "Nasal Polyp", "definition": "비강폴립"},
            {"term": "Deviated Septum", "definition": "비중격만곡증"},
            {"term": "Anosmia", "definition": "후각상실"},
            {"term": "Rhinorrhea", "definition": "콧물"},
            {"term": "Nasal Obstruction", "definition": "비강폐쇄"},
            {"term": "Allergic Rhinitis", "definition": "알레르기성 비염"},
            {"term": "Nasal Trauma", "definition": "비부외상"},
            # 추가 5개
            {"term": "Nasopharyngitis", "definition": "비인두염"},
            {"term": "Rhinosinusitis", "definition": "비부비동염"},
            {"term": "Hyposmia", "definition": "후각저하"},
            {"term": "Turbinate Hypertrophy", "definition": "코벌미비대"},
            {"term": "Foreign Body in Nose", "definition": "코 이물"}
        ]
    },
    "비뇨기과": {
        "신장": [
            {"term": "Nephritis", "definition": "신장염"},
            {"term": "Renal Failure", "definition": "신부전"},
            {"term": "Nephrotic Syndrome", "definition": "신증후군"},
            {"term": "Pyelonephritis", "definition": "신우신염"},
            {"term": "Hydronephrosis", "definition": "수신증"},
            {"term": "Renal Cyst", "definition": "신낭종"},
            {"term": "Glomerulonephritis", "definition": "사구체신염"},
            {"term": "Kidney Stone", "definition": "신장결석"},
            {"term": "Renal Cancer", "definition": "신장암"},
            {"term": "Polycystic Kidney", "definition": "다낭성신장"},
            # 추가 5개
            {"term": "Nephroblastoma", "definition": "신아세포종(윌름스 종양)"},
            {"term": "Renal Artery Stenosis", "definition": "신동맥협착증"},
            {"term": "Renal Colic", "definition": "신산통"},
            {"term": "Renal Hypertension", "definition": "신성고혈압"},
            {"term": "Renal Osteodystrophy", "definition": "신성골이영양증"}
        ],
        "방광": [
            {"term": "Cystitis", "definition": "방광염"},
            {"term": "Urinary Retention", "definition": "요저류"},
            {"term": "Incontinence", "definition": "요실금"},
            {"term": "Bladder Cancer", "definition": "방광암"},
            {"term": "Overactive Bladder", "definition": "과민성방광"},
            {"term": "Neurogenic Bladder", "definition": "신경인성방광"},
            {"term": "Urethritis", "definition": "요도염"},
            {"term": "Urinary Tract Infection", "definition": "요로감염"},
            {"term": "Bladder Stone", "definition": "방광결석"},
            {"term": "Interstitial Cystitis", "definition": "간질성방광염"},
            # 추가 5개
            {"term": "Bladder Neck Obstruction", "definition": "방광경부폐색"},
            {"term": "Bladder Fistula", "definition": "방광루"},
            {"term": "Bladder Diverticulum", "definition": "방광게실"},
            {"term": "Dysuria", "definition": "배뇨통"},
            {"term": "Benign Prostatic Hyperplasia", "definition": "양성 전립선 비대증(비뇨기과적 문제)"}
        ]
    }
}

# PDF에서 추출한 의학 용어 추가
pdf_terms = {
    "의학 약어": {
        "병원 약어": [
            {"term": "aa ana, of each", "definition": "각각"},
            {"term": "Abd abdominal", "definition": "복부"},
            {"term": "ABR absolute bed rest", "definition": "절대 안정"},
            {"term": "a.c before meals", "definition": "식전"},
            {"term": "a.h every hour", "definition": "매시간"},
            {"term": "amp ample", "definition": "앰플"},
            {"term": "amt amount", "definition": "양"},
            {"term": "AP anterior-posterior", "definition": "전후"},
            {"term": "aq aqua", "definition": "물"},
            {"term": "A&P auscultation&percussion", "definition": "청진과 타진"},
            {"term": "b.i.d twice a day", "definition": "하루 두 번"},
            {"term": "BUN/Cr blood urea nitrogen/creatinine", "definition": "혈중 요소 질소"},
            {"term": "Ca cancer", "definition": "암"},
            {"term": "Cath catheterization", "definition": "도뇨"},
            {"term": "cap capsule", "definition": "캡슐"},
            {"term": "C.C chief complain", "definition": "주 호소"},
            {"term": "CSR central supply room", "definition": "중앙공급실"},
            {"term": "D.C discontinue", "definition": "중단, 중지"},
            {"term": "D.O.A dead on arrival", "definition": "도착 시 사망함"},
            {"term": "Dx diagnosis", "definition": "진단"}
        ]
    },
    "소화기계": {
        "용어": [
            {"term": "abscess", "definition": "농양"},
            {"term": "absorption", "definition": "흡수"},
            {"term": "achalasia", "definition": "이완 불능, 식도 경련"},
            {"term": "adhesion", "definition": "유착, 접착"},
            {"term": "anal fistula", "definition": "치루, 항문 루"},
            {"term": "anal fissure", "definition": "항문 열상"},
            {"term": "anastomosis", "definition": "문합술"},
            {"term": "anorexia", "definition": "식욕부진"},
            {"term": "ascites", "definition": "복수"},
            {"term": "aphagia", "definition": "연하불능"},
            {"term": "aphthous stomatitis", "definition": "아프타성 구내염"},
            {"term": "appendicitis", "definition": "충수염"},
            {"term": "appendectomy", "definition": "충수절제술"},
            {"term": "bulimia", "definition": "식욕항진"},
            {"term": "colic pain", "definition": "산통"}
        ]
    },
    "호흡기계": {
        "용어": [
            {"term": "acute respiratory failure", "definition": "급성 호흡부전"},
            {"term": "aspiration", "definition": "흡인"},
            {"term": "asphyxia", "definition": "질식"},
            {"term": "asthma", "definition": "천식"},
            {"term": "atelectasis", "definition": "무기폐"},
            {"term": "barrel chest", "definition": "술통형 흉곽"},
            {"term": "bradypnea", "definition": "서호흡"},
            {"term": "bronchiectasis", "definition": "기관지 확장증"},
            {"term": "bronchospasm", "definition": "기관지경련"},
            {"term": "bronchitis", "definition": "기관지염"},
            {"term": "bronchodilator", "definition": "기관지 확장제"},
            {"term": "bronchopneumonia", "definition": "기관지 폐렴"},
            {"term": "bronchostenosis", "definition": "기관지협착증"},
            {"term": "crop", "definition": "후두염"},
            {"term": "cyanosis", "definition": "청색증"}
        ]
    },
    "순환기계": {
        "용어": [
            {"term": "arrhythmia", "definition": "부정맥"},
            {"term": "arteriopuncture", "definition": "동맥천자"},
            {"term": "arteriosclerosis", "definition": "동맥경화증"},
            {"term": "arteriosclerosis obliterans", "definition": "폐쇄성 동맥경화증"},
            {"term": "bradycardia", "definition": "서맥"},
            {"term": "cardiac arrest", "definition": "심박동 정지"},
            {"term": "cardiac catheterization", "definition": "심도자법"},
            {"term": "cardiac massage", "definition": "심장 마사지"},
            {"term": "cardiac output", "definition": "심박출량"},
            {"term": "cardiac tamponade", "definition": "심장압전"},
            {"term": "carditis", "definition": "심장염"},
            {"term": "cardiocentesis", "definition": "심장천자"},
            {"term": "cardiogenic shock", "definition": "심인성 쇽"},
            {"term": "cardioversion", "definition": "심장리듬전환술"},
            {"term": "cyanosis", "definition": "청색증"}
        ]
    },
    "혈액계": {
        "용어": [
            {"term": "albumin", "definition": "알부민"},
            {"term": "anemia", "definition": "빈혈"},
            {"term": "aplastic anemia", "definition": "재생 불량성 빈혈"},
            {"term": "basophils", "definition": "호염구"},
            {"term": "blood clotting", "definition": "혈액 응고"},
            {"term": "blood dyscasia", "definition": "혈액 이상"},
            {"term": "coagulation", "definition": "응고"},
            {"term": "collagen diseases", "definition": "교원병"},
            {"term": "cytopenia", "definition": "혈구감소증"},
            {"term": "ecchymosis", "definition": "반상 출혈"},
            {"term": "eosinophilia", "definition": "호산구 증가증"},
            {"term": "epistaxis", "definition": "비출혈"},
            {"term": "erythremia", "definition": "적혈병"},
            {"term": "erythrocyte", "definition": "적혈구"},
            {"term": "erythropenia", "definition": "적혈구 감소증"}
        ]
    },
    "신경계": {
        "용어": [
            {"term": "anencephaly", "definition": "무뇌증"},
            {"term": "anesthesia", "definition": "마취, 마비"},
            {"term": "aphasia", "definition": "실어증"},
            {"term": "apraxia", "definition": "실행증"},
            {"term": "asphyxia", "definition": "질식"},
            {"term": "asthenia", "definition": "무력증"},
            {"term": "ataxia", "definition": "운동실조"},
            {"term": "atrophy", "definition": "위축"},
            {"term": "aura", "definition": "전조"},
            {"term": "babinski reflex", "definition": "바빈스키 반사"}
        ]
    },
    "이비인후과": {
        "용어": [
            {"term": "laryngitis", "definition": "후두염"},
            {"term": "laryngospasm", "definition": "후두경련"},
            {"term": "laryngoscopy", "definition": "후두경 검사"},
            {"term": "laryngotomy", "definition": "후두절개술"},
            {"term": "Meniere's disease", "definition": "메니에르병, 알러지성미로수종"},
            {"term": "microtia", "definition": "소이증"}
        ]
    },
    "비뇨기계": {
        "용어": [
            {"term": "albuminuria", "definition": "알부민뇨"},
            {"term": "anuria", "definition": "무뇨"},
            {"term": "azotemia", "definition": "질소뇨"},
            {"term": "bacteriuria", "definition": "세균뇨"},
            {"term": "bladder", "definition": "방광"},
            {"term": "catheterization", "definition": "도뇨 삽입"},
            {"term": "cystitis", "definition": "방광염"}
        ]
    }
}

# 기존 용어와 PDF에서 추출한 용어 통합
for category, subcategories in pdf_terms.items():
    if category not in nested_terms:
        nested_terms[category] = {}
    
    for subcategory, terms in subcategories.items():
        if subcategory not in nested_terms[category]:
            nested_terms[category][subcategory] = []
        
        nested_terms[category][subcategory].extend(terms)

# 중첩된 딕셔너리를 단일 리스트로 변환
def flatten_terms(nested_dict):
    flat_list = []
    for val in nested_dict.values():
        if isinstance(val, dict):
            flat_list.extend(flatten_terms(val))
        elif isinstance(val, list):
            flat_list.extend(val)
    return flat_list

medical_terms = flatten_terms(nested_terms)

# 데이터 저장 함수
def save_data():
    data = {
        "completed_terms": [term["term"] for term in st.session_state.completed_terms],
        "monthly_completions": st.session_state.monthly_completions,
        "all_time_completed": [term["term"] for term in st.session_state.all_time_completed],
        "daily_terms": {k: [term["term"] for term in v] for k, v in st.session_state.daily_terms.items()},
        "student_progress": st.session_state.student_progress,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("medical_app_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 데이터 로드 함수
def load_data():
    if os.path.exists("medical_app_data.json"):
        with open("medical_app_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 용어 이름으로 실제 용어 객체 찾기
        term_dict = {term["term"]: term for term in medical_terms}
        
        st.session_state.completed_terms = [term_dict.get(term_name, {"term": term_name, "definition": "정의 없음"}) 
                                           for term_name in data.get("completed_terms", [])]
        
        st.session_state.monthly_completions = data.get("monthly_completions", 0)
        
        st.session_state.all_time_completed = [term_dict.get(term_name, {"term": term_name, "definition": "정의 없음"}) 
                                              for term_name in data.get("all_time_completed", [])]
        
        # 일일 용어 복원
        daily_terms = {}
        for date_key, term_names in data.get("daily_terms", {}).items():
            daily_terms[date_key] = [term_dict.get(term_name, {"term": term_name, "definition": "정의 없음"}) 
                                    for term_name in term_names]
        st.session_state.daily_terms = daily_terms
        
        # 학생 진도 데이터 로드
        st.session_state.student_progress = data.get("student_progress", {})

# 세션 상태 초기화
if "completed_terms" not in st.session_state:
    st.session_state.completed_terms = []
if "monthly_completions" not in st.session_state:
    st.session_state.monthly_completions = 0
if "all_time_completed" not in st.session_state:
    st.session_state.all_time_completed = []
# 날짜별로 뽑힌 6개 용어 저장용(딕셔너리: {날짜(str): [용어6개]})
if "daily_terms" not in st.session_state:
    st.session_state.daily_terms = {}
# 학생 진도 추적용 (딕셔너리: {학생ID: {날짜: 완료한 용어 수}})
if "student_progress" not in st.session_state:
    st.session_state.student_progress = {}
# 현재 로그인한 학생 ID
if "current_student" not in st.session_state:
    st.session_state.current_student = None
# 관리자 모드 여부
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# 데이터 로드
load_data()

# 사이드바 메뉴
with st.sidebar:
    # 로그인 섹션
    st.subheader("👤 로그인")
    
    # 간단한 로그인 기능
    student_id = st.text_input("학생 ID", key="login_id")
    login_password = st.text_input("비밀번호", type="password", key="login_password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("로그인"):
            if student_id and login_password:
                st.session_state.current_student = student_id
                # 학생 진도 데이터 초기화 (없는 경우)
                if student_id not in st.session_state.student_progress:
                    st.session_state.student_progress[student_id] = {}
                st.success(f"{student_id}님 환영합니다!")
                
                # 관리자 계정 확인 (실제로는 더 안전한 방식으로 구현해야 함)
                if student_id == "admin" and login_password == "admin123":
                    st.session_state.admin_mode = True
    
    with col2:
        if st.button("로그아웃"):
            st.session_state.current_student = None
            st.session_state.admin_mode = False
            st.info("로그아웃되었습니다.")
    
    st.divider()
    
    # 메뉴 옵션
    menu_options = {
        "오늘의 학습": "book",
        "통계": "graph-up",
        "상품 시스템": "gift"
    }
    
    # 관리자인 경우 관리자 대시보드 메뉴 추가
    if st.session_state.admin_mode:
        menu_options["관리자 대시보드"] = "gear"
    
    selected = option_menu(
        "학습 메뉴",
        list(menu_options.keys()),
        icons=list(menu_options.values()),
        menu_icon="cast",
        default_index=0,
    )

# 오늘의 학습 페이지
if selected == list(menu_options.keys())[0]:  # "오늘의 학습"
    st.title("🏥 오늘의 의학 용어")
    
    if not st.session_state.current_student:
        st.warning("학습을 시작하려면 로그인이 필요합니다.")
    else:
        # 날짜 선택
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_date = st.date_input("학습 날짜 선택", datetime.now())
        
        # 문자열 형태로 키를 사용(날짜별)
        date_key = selected_date.strftime("%Y-%m-%d")

        # date_key에 해당하는 6개 용어가 없다면 새로 뽑음
        if date_key not in st.session_state.daily_terms:
            # 남아있는 용어 중 6개 또는 전체에서 재추출
            remaining_terms = [term for term in medical_terms 
                            if term not in st.session_state.all_time_completed]
            if len(remaining_terms) < 6:
                sample_pool = medical_terms  # 전체 중에서 추출
            else:
                sample_pool = remaining_terms
            
            # 오늘의 6개 용어 고정
            st.session_state.daily_terms[date_key] = random.sample(sample_pool, 6)

        # 오늘의 용어 가져오기
        today_terms = st.session_state.daily_terms[date_key]

        # 전체 진행률 표시
        progress = len(st.session_state.all_time_completed) / len(medical_terms)
        st.progress(progress)
        st.write(
            f"전체 진행률: {progress*100:.1f}% "
            f"({len(st.session_state.all_time_completed)}/{len(medical_terms)})"
        )

        # 카드 표시 (영어+한글, 굵게)
        cols = st.columns(3)
        for idx, term in enumerate(today_terms):
            with cols[idx % 3]:
                card_key = f"term_card_{date_key}_{idx}"
                st.markdown(f"""
                <div class="term-card">
                    <p style="font-weight:bold; font-size:1.1rem;">{term['term']}</p>
                    <p style="font-weight:bold; font-size:1rem;">{term['definition']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 완료 버튼
                if st.button("완료", key=card_key):
                    if term not in st.session_state.completed_terms:
                        st.session_state.completed_terms.append(term)
                    if term not in st.session_state.all_time_completed:
                        st.session_state.all_time_completed.append(term)
                        st.session_state.monthly_completions += 1

                    # 학생 진도 업데이트
                    student_id = st.session_state.current_student
                    if student_id:
                        # student_id가 student_progress에 없는 경우 초기화
                        if student_id not in st.session_state.student_progress:
                            st.session_state.student_progress[student_id] = {}
                        # date_key가 해당 학생의 progress에 없는 경우 초기화
                        if date_key not in st.session_state.student_progress[student_id]:
                            st.session_state.student_progress[student_id][date_key] = 0
                        st.session_state.student_progress[student_id][date_key] += 1
                    
                    # 데이터 저장
                    save_data()

                    st.success("잘 하셨습니다! 🎉")
                    # 작은 풍선 하나만 표시
                    st.balloons()

# 통계 페이지
elif selected == list(menu_options.keys())[1]:  # "통계"
    st.title("📊 학습 통계")
    
    if not st.session_state.current_student:
        st.warning("통계를 확인하려면 로그인이 필요합니다.")
    else:
        student_id = st.session_state.current_student
        
        # 월간 완료 통계
        st.subheader("월간 완료 현황")
        monthly_data = pd.DataFrame({
            "완료 횟수": [st.session_state.monthly_completions],
            "목표": [30]
        })
        
        fig = go.Figure(data=[
            go.Bar(name="완료", y=monthly_data["완료 횟수"], marker_color="#4F46E5"),
            go.Bar(name="목표", y=monthly_data["목표"], marker_color="#7C3AED")
        ])
        
        fig.update_layout(
            barmode='group',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 전체 진행 현황
        st.subheader("전체 진행 현황")
        total_progress = len(st.session_state.all_time_completed)
        total_terms = len(medical_terms)
        st.metric(
            "학습한 용어 수",
            f"{total_progress}/{total_terms}",
            f"{(total_progress/total_terms*100):.1f}%"
        )
        
        # 학습 캘린더 표시
        st.subheader("학습 캘린더")
        
        # 현재 월의 날짜 생성
        today = datetime.now()
        first_day = datetime(today.year, today.month, 1)
        last_day = (datetime(today.year, today.month + 1, 1) - timedelta(days=1)).day
        
        # 학생의 학습 데이터 가져오기
        student_data = st.session_state.student_progress.get(student_id, {})
        
        # 캘린더 표시
        st.write("이번 달 학습 현황:")
        
        # 주 단위로 날짜 표시
        weeks = []
        current_week = []
        
        # 첫 주 시작 전 빈 칸 채우기
        first_weekday = first_day.weekday()
        for _ in range(first_weekday):
            current_week.append(None)
        
        # 날짜 채우기
        for day in range(1, last_day + 1):
            date_obj = datetime(today.year, today.month, day)
            date_str = date_obj.strftime("%Y-%m-%d")
            
            # 해당 날짜에 학습한 용어 수 확인
            completed_count = student_data.get(date_str, 0)
            
            current_week.append((day, completed_count))
            
            # 토요일이거나 마지막 날이면 주 마감
            if date_obj.weekday() == 6 or day == last_day:
                weeks.append(current_week)
                current_week = []
        
        # 마지막 주 빈 칸 채우기
        while len(current_week) < 7 and current_week:
            current_week.append(None)
        
        # 캘린더 렌더링
        cols = st.columns(7)
        for i, day_name in enumerate(["월", "화", "수", "목", "금", "토", "일"]):
            cols[i].markdown(f"<div style='text-align:center; font-weight:bold;'>{day_name}</div>", unsafe_allow_html=True)
        
        for week in weeks:
            cols = st.columns(7)
            for i, day_data in enumerate(week):
                if day_data is None:
                    cols[i].write("")
                else:
                    day, count = day_data
                    if count > 0:
                        cols[i].markdown(f"""
                        <div class='calendar-day calendar-day-completed' style='text-align:center;'>
                            <span>{day}</span>
                        </div>
                        <div style='text-align:center; font-size:0.8rem;'>{count}개</div>
                        """, unsafe_allow_html=True)
                    else:
                        cols[i].markdown(f"""
                        <div class='calendar-day' style='text-align:center;'>
                            <span>{day}</span>
                        </div>
                        """, unsafe_allow_html=True)

# 상품 시스템 페이지
elif selected == list(menu_options.keys())[2]:  # "상품 시스템"
    st.title("🎁 상품 시스템")
    
    if not st.session_state.current_student:
        st.warning("상품 시스템을 확인하려면 로그인이 필요합니다.")
    else:
        rewards = {
            10: "메모지 세트",
            20: "휴대용 수첩",
            30: "프리미엄 노트"
        }
        
        # 학생이 학습한 일수 계산 (student_progress에서 날짜 수 계산)
        student_id = st.session_state.current_student
        completed_days = 0
        if student_id in st.session_state.student_progress:
            # 학습 기록이 있는 날짜 수 계산
            completed_days = len(st.session_state.student_progress[student_id])
        
        for count, reward in rewards.items():
            # 학습한 일수를 기준으로 상품 획득 여부 판단
            achieved = completed_days >= count
            container_class = "stats-card" if achieved else "term-card"
            status_text = "획득 완료! 🎉" if achieved else "아직 획득하지 못했습니다"
            
            st.markdown(f"""
            <div class="{container_class}">
                <h3>{count}일 완료 - {reward}</h3>
                <p>{status_text}</p>
            </div>
            """, unsafe_allow_html=True)

        # 현재 달성 현황 (학습한 일수 기준)
        next_reward = next(
            (count for count in sorted(rewards.keys()) if count > completed_days),
            None
        )
        if next_reward:
            remaining = next_reward - completed_days
            st.info(f"다음 상품까지 {remaining}일 더 학습해야 합니다! 화이팅! 💪")

# 관리자 대시보드 페이지
elif selected == "관리자 대시보드" and st.session_state.admin_mode:
    st.title("👨‍💼 관리자 대시보드")
    
    # 전체 학생 진도 현황
    st.subheader("학생별 진도 현황")
    
    if not st.session_state.student_progress:
        st.info("아직 등록된 학생 데이터가 없습니다.")
    else:
        # 학생별 총 완료 용어 수 계산
        student_totals = {}
        for student_id, dates in st.session_state.student_progress.items():
            if student_id != "admin":  # 관리자 제외
                student_totals[student_id] = sum(dates.values())
        
        # 데이터프레임 생성
        student_df = pd.DataFrame({
            "학생 ID": list(student_totals.keys()),
            "완료한 용어 수": list(student_totals.values())
        })
        
        # 정렬
        student_df = student_df.sort_values("완료한 용어 수", ascending=False)
        
        # 표 표시
        st.dataframe(student_df, use_container_width=True)
        
        # 학생별 진도 그래프
        st.subheader("학생별 진도 그래프")
        
        fig = go.Figure()
        for student_id, total in student_totals.items():
            percentage = (total / len(medical_terms)) * 100
            fig.add_trace(go.Bar(
                x=[student_id],
                y=[percentage],
                name=student_id,
                text=[f"{percentage:.1f}%"],
                textposition="auto"
            ))
        
        fig.update_layout(
            title="학생별 전체 진도율 (%)",
            xaxis_title="학생 ID",
            yaxis_title="진도율 (%)",
            yaxis=dict(range=[0, 100]),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 일별 학습 현황
        st.subheader("일별 학습 현황")
        
        # 날짜 범위 선택
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작 날짜", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("종료 날짜", datetime.now())
        
        # 날짜 범위 내 데이터 추출
        date_range = [(start_date + timedelta(days=x)).strftime("%Y-%m-%d") 
                      for x in range((end_date - start_date).days + 1)]
        
        # 학생별 일일 데이터 수집
        daily_data = {student_id: [] for student_id in student_totals.keys()}
        for date_str in date_range:
            for student_id in student_totals.keys():
                count = st.session_state.student_progress.get(student_id, {}).get(date_str, 0)
                daily_data[student_id].append(count)
        
        # 그래프 생성
        fig = go.Figure()
        for student_id, counts in daily_data.items():
            fig.add_trace(go.Scatter(
                x=date_range,
                y=counts,
                mode='lines+markers',
                name=student_id
            ))
        
        fig.update_layout(
            title="일별 학습 용어 수",
            xaxis_title="날짜",
            yaxis_title="완료한 용어 수",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 전체 통계
        st.subheader("전체 통계")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 학생 수", len(student_totals))
        with col2:
            avg_terms = sum(student_totals.values()) / len(student_totals) if student_totals else 0
            st.metric("학생당 평균 완료 용어 수", f"{avg_terms:.1f}")
        with col3:
            active_students = sum(1 for total in student_totals.values() if total > 0)
            st.metric("활동 학생 수", active_students)
        
        # 데이터 내보내기
        st.subheader("데이터 내보내기")
        
        if st.button("CSV로 내보내기"):
            # 모든 학생의 모든 날짜 데이터 수집
            all_dates = set()
            for dates in st.session_state.student_progress.values():
                all_dates.update(dates.keys())
            
            all_dates = sorted(list(all_dates))
            
            # 데이터프레임 생성
            export_data = []
            for student_id in student_totals.keys():
                student_row = {"학생 ID": student_id}
                for date_str in all_dates:
                    count = st.session_state.student_progress.get(student_id, {}).get(date_str, 0)
                    student_row[date_str] = count
                export_data.append(student_row)
            
            export_df = pd.DataFrame(export_data)
            
            # CSV 파일로 저장
            export_df.to_csv("student_progress_export.csv", index=False, encoding="utf-8-sig")
            
            # 다운로드 링크 제공
            with open("student_progress_export.csv", "rb") as file:
                st.download_button(
                    label="CSV 파일 다운로드",
                    data=file,
                    file_name="student_progress_export.csv",
                    mime="text/csv"
                )

# 하단 정보
st.markdown("---")
st.markdown("Made with ❤️ for Medical Students")

# 모든 용어 학습 완료 시 초기화 버튼
if len(st.session_state.all_time_completed) == len(medical_terms):
    st.success("🎓 축하합니다! 모든 의학 용어를 학습하셨습니다!")
    if st.button("처음부터 다시 시작하기"):
        st.session_state.all_time_completed = []
        st.session_state.completed_terms = []
        st.session_state.monthly_completions = 0
        st.session_state.daily_terms = {}
        save_data()
        st.experimental_rerun()
