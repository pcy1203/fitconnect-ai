# ==================== Talent Base Interview ====================
from typing import List, Optional
from abc import ABC, abstractmethod

class BaseInterview(ABC):
    """면접 관리 클래스"""

    def __init__(self):
        self.questions_and_answers: List[dict] = []
        self.current_question_num: int = 0
        self.total_questions_num: int = 0

    @abstractmethod
    def get_next_question(self) -> Optional[str]:
        """다음 질문을 반환 (각 면접 유형별로 구현)"""
        pass

    @abstractmethod
    def analyze_answer(self, answer: str) -> dict:
        """답변 제출 및 분석 로직 (각 면접 유형별로 구현)"""
        pass

    def submit_answer(self, answer: str) -> dict:
        """답변 제출"""
        if self.current_question_num == 0:
            raise ValueError("인터뷰 시작 전입니다.")
        question = self.questions[self.current_question_num - 1]
        self.questions_and_answers.append({
            "question": question,
            "answer": answer
        })
        next_question = self.get_next_question()
        return {
            "submitted": True,
            "question_number": self.current_question_num,
            "total_questions": self.total_questions_num,
            "next_question": next_question
        }

    def is_finished(self) -> bool:
        """면접 종료 여부"""
        return self.current_question_num >= self.total_questions_num

    def get_questions_and_answers(self) -> List[dict]:
        """전체 답변 조회"""
        return self.questions_and_answers


    # def move_next(self):
    #     """다음 질문으로 이동"""
    #     self.current_question_num += 1


    # def get_history(self) -> List[dict]:
    #     """전체 Q&A 기록 조회"""
    #     return self.qa_history

    # def reset(self):
    #     """면접 상태 초기화"""
    #     self.current_question_num = 0
    #     self.current_question = None
    #     self.qa_history = []
    #     self.is_active = True
