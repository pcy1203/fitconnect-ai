# ==================== Talent General Interview ====================
from config.settings import get_settings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Optional
from ai.interview.talent.models import (
    CandidateProfile,
    GeneralInterviewAnalysis,
    GeneralInterviewCardPart,
)
from ai.interview.talent.baseinterview import BaseInterview


# =====================================================================
# ==================== General Interview Questions ====================
# =====================================================================
GENERAL_QUESTIONS = [
    "최근 6개월 동안 가장 몰입했던 일은 무엇인가요? 왜 그 경험에 몰입했고, 어떤 결과를 얻었는지 말씀해 주세요.",
    "가장 성과를 냈다고 생각하는 프로젝트나 업무 경험을 소개해 주세요. 어떤 역할을 맡았고, 결과는 어땠나요?",
    "팀원들과 협업할 때 본인만의 강점은 무엇이라고 생각하시나요? 구체적인 사례와 함께 이야기 해주세요.",
    "일을 할 때 가장 중요하게 생각하는 가치는 무엇인가요? 해당 가치가 실제 행동으로 드러난 사례를 말씀해 주세요.",
    "앞으로 어떤 역량을 더 발전시키고 싶나요? 커리어에 대한 계획을 포함하여 말씀해 주세요."
]


# =================================================================
# ==================== General Interview Model ====================
# =================================================================
class GeneralInterview(BaseInterview):
    """구조화 면접"""

    def __init__(self, questions: Optional[List[str]] = None):
        super().__init__()
        self.questions = questions or GENERAL_QUESTIONS
        self.total_questions_num = len(self.questions)

    def get_next_question(self) -> Optional[str]:
        if self.current_question_num < self.total_questions_num:
            question = self.questions[self.current_question_num]
            self.current_question_num += 1
            return question
        return None
    
    def analyze_answer(self, answer):
        return super().analyze_answer(answer)


# ===================================================================
# ==================== General Interview Analysis ====================
# ===================================================================
def analyze_general_interview(questions_and_answers: List[dict]) -> GeneralInterviewAnalysis:
    """구조화 면접 답변 분석"""
    all_questions_and_answers = "\n\n".join([
        f"질문: {question_and_answer['question']}\n답변: {question_and_answer['answer']}"
        for question_and_answer in questions_and_answers
    ])
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 채용 전문가입니다.

        지원자의 구조화 면접 답변들을 분석하여, 직무 적합성 면접을 개인화하기 위한 핵심 정보를 추출하세요.

        **분석 목표:**
        1. 답변 전반에서 반복적으로 등장하는 주요 키워드
        2. 지원자가 중요하게 언급한 대표 경험과 성과
        3. 지원자의 핵심 역량과 행동적 강점
        4. 지원자의 직무 역량
        5. 지원자의 업무 방식과 협업 스타일, 성장 가능성
        6. 지원자의 기술 스택 (기술 직군에 한해) 혹은 활용 가능한 툴 (무관한 직무는 빈 값 가능)

        **분석 원칙:**
        - 사실 기반 평가 (프로필과 인터뷰 답변에 있는 내용만 사용)
        - 추정 및 과장 금지 (언급되지 않은 내용을 만들어내지 말 것)
        - 행동 기반 평가 (실제로 드러난 행동과 경험에 더 집중하여 분석)
        - 직무 유관 경험 우선 평가 (직무에서 필요로 하는 역량을 중심으로 분석, 직무와 무관하면 제외)
        - 종합적 해석과 구체적 서술 (명확한 키워드를 포함하여 정리)
        """),
        ("user", all_questions_and_answers),
        #TODO: 직군에 대한 데이터/설명 (업무 및 핵심 역량)
    ])
    settings = get_settings()
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY
    ).with_structured_output(GeneralInterviewAnalysis)
    return (prompt | llm).invoke({})



# ===================================================================
# 수정

def analyze_general_interview_for_card(
    candidate_profile: CandidateProfile,
    general_analysis: GeneralInterviewAnalysis,
    answers: list[dict]
) -> GeneralInterviewCardPart:
    """
    구조화 면접 결과를 프로필 카드용 파트로 변환

    Args:
        candidate_profile: 지원자 기본 프로필
        general_analysis: 구조화 면접 분석 결과
        answers: 원본 Q&A [{"question": str, "answer": str}, ...]

    Returns:
        GeneralInterviewCardPart
    """
    all_qa = "\n\n".join([
        f"질문: {a['question']}\n답변: {a['answer']}"
        for a in answers
    ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 HR 전문가입니다.
구조화 면접 결과를 분석하여 **주요 경험/경력**과 **핵심 일반 역량**을 추출하세요.

**추출 목표:**

1. **주요 경험/경력 (4개)**:
   - 구체적인 프로젝트나 업무 경험
   - 면접에서 강조한 경험 위주
   - 예: "마이크로서비스 아키텍처 설계 및 구축", "신규 결제 시스템 개발 리드"

2. **핵심 일반 역량 (4개)**:
   - Soft skills (리더십, 커뮤니케이션, 협업, 문제해결 등)
   - 각 역량의 수준: "높음", "보통", "낮음"
   - 면접에서 드러난 업무 스타일과 태도 기반
   - 예: {{"name": "협업 능력", "level": "높음"}}

**레벨 판단 기준:**
- **높음**: 구체적 사례와 함께 여러 번 강조, 명확한 성과 제시
- **보통**: 언급은 되었으나 깊이가 부족하거나 1-2회 언급
- **낮음**: 거의 언급 안됨 또는 매우 피상적

**주의:**
- 실제 면접 답변에 근거하여 작성
- 추측하지 말고 드러난 내용만 추출
- 구체적이고 명확하게 작성
"""),
        ("user", f"""
## 지원자 기본 정보
- 이름: {candidate_profile.basic.name if candidate_profile.basic else "지원자"}
- 직무: {candidate_profile.basic.tagline if candidate_profile.basic else "개발자"}
- 총 경력: {sum((exp.duration_years or 0) for exp in candidate_profile.experiences)}년

## 경력사항
{chr(10).join([f"- {exp.company_name} / {exp.title} ({exp.duration_years or 0}년)" for exp in candidate_profile.experiences]) if candidate_profile.experiences else "정보 없음"}

## 구조화 면접 분석 결과 (참고용)
- 주요 테마: {', '.join(general_analysis.key_themes)}
- 관심사: {', '.join(general_analysis.interests)}
- 업무 스타일: {', '.join(general_analysis.work_style_hints)}
- 강조한 경험: {', '.join(general_analysis.emphasized_experiences)}
- 기술 키워드: {', '.join(general_analysis.technical_keywords)}

## 구조화 면접 원본 답변
{all_qa}

위 정보를 바탕으로 **주요 경험/경력 4개**와 **핵심 일반 역량 4개**(레벨 포함)를 추출하세요.
""")
    ])

    settings = get_settings()
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY
    ).with_structured_output(GeneralInterviewCardPart)

    return (prompt | llm).invoke({})
