import json
import os

class Quiz:
    """개별 퀴즈를 표현하는 클래스"""
    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices  # 4개의 리스트
        self.answer = answer    # 정답 번호 (1~4)

    def to_dict(self):
        """JSON 저장을 위해 딕셔너리 형태로 변환"""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer
        }


class QuizGame:
    """게임 전체를 관리하는 클래스"""
    def __init__(self, filename="state.json"):
        self.filename = filename
        self.quizzes = []
        self.best_score = 0
        self.load_data()

    def load_data(self):
        """state.json 파일에서 퀴즈 데이터와 최고 점수를 불러옴
            즉, 프로그램을 껐다 켜도 유지되도록 게임의 슬롯1 Save 데이터인 셈이다!(데이터 영속성)"""
        # 파일이 없으면 기본 퀴즈 데이터 생성
        if not os.path.exists(self.filename):   # 파일이 없다면?
            self.init_default_quizzes()         # 기본 퀴즈를 만들고
            self.save_data()                    # state.json 파일로 저장해라!
            print("📂 기본 퀴즈 데이터로 시작합니다.")
            return

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.best_score = data.get("best_score", 0)
                raw_quizzes = data.get("quizzes", [])
                
                self.quizzes = []
                for q in raw_quizzes:
                    self.quizzes.append(Quiz(q["question"], q["choices"], q["answer"]))
            
            print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_score}점)")
        except (json.JSONDecodeError, Exception) as e:
            print("⚠️ 데이터 파일이 손상되었거나 읽을 수 없습니다. 기본 데이터로 복구합니다.")
            self.init_default_quizzes()
            self.save_data()

    def save_data(self):
        """현재 퀴즈 목록과 최고 점수를 state.json에 저장"""
        try:
            data = {
                "best_score": self.best_score,
                "quizzes": [q.to_dict() for q in self.quizzes]
            }
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ 데이터 저장 중 오류가 발생했습니다: {e}")

    def init_default_quizzes(self):
        """기본 퀴즈 5개 이상 생성"""
        self.quizzes = [
            Quiz("Python의 창시자는?", ["Guido van Rossum", "Linus Torvalds", "Bjarne Stroustrup", "James Gosling"], 1),
            Quiz("다음 중 기본 자료형(Primitive/Built-in type)이 아닌 것은?", ["int", "str", "array", "bool"], 3),
            Quiz("Git에서 원격 저장소의 내용을 가져와 병합하는 명령어는?", ["git push", "git pull", "git commit", "git init"], 2),
            Quiz("파이썬에서 함수를 정의할 때 사용하는 키워드는?", ["func", "define", "def", "function"], 3),
            Quiz("데이터를 키-값(Key-Value) 형태로 저장하는 파이썬 자료구조는?", ["list", "tuple", "dict", "set"], 3)
        ]

    def get_validated_input(self, prompt, min_val, max_val):
        """숫자 입력 및 예외 처리를 공통으로 수행하는 헬퍼 메서드"""
        while True:
            try:
                user_input = input(prompt).strip()
                if not user_input:
                    print("⚠️ 빈 입력입니다. 다시 입력해주세요.")
                    continue
                
                value = int(user_input)
                if min_val <= value <= max_val:
                    return value
                else:
                    print(f"⚠️ 잘못된 입력입니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.")
            except ValueError:
                print(f"⚠️ 숫자 형식으로 입력해주세요.")
            except (KeyboardInterrupt, EOFError):
                print("\n\n🚪 프로그램을 안전하게 종료합니다.")
                self.save_data()
                exit(0)

    def play_quiz(self):
        """퀴즈 풀기 기능"""
        if not self.quizzes:
            print("\n❌ 등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해주세요!")
            return

        print(f"\n📝 퀴즈를 시작합니다! (총 {len(self.quizzes)}문제)")
        score = 0

        for i, q in enumerate(self.quizzes, 1):
            print("-" * 40)
            print(f"[문제 {i}] {q.question}")
            for idx, choice in enumerate(q.choices, 1):
                print(f"{idx}. {choice}")

            ans = self.get_validated_input("정답 입력 (1-4): ", 1, 4)

            if ans == q.answer:
                print("✅ 정답입니다!")
                score += 1
            else:
                print(f"❌ 틀렸습니다! 정답은 {q.answer}번입니다.")

        # 점수 계산 및 최고 점수 갱신 (100점 만점 환산 또는 맞은 개수 기준)
        # 여기서는 맞은 개수를 점수로 사용하거나 백분율로 계산 가능 (미션 예시 기준 맞은 개수 혹은 점수)
        calculated_score = int((score / len(self.quizzes)) * 100)
        print("=" * 40)
        print(f"🏆 결과: {len(self.quizzes)}문제 중 {score}문제 정답! ({calculated_score}점)")

        if calculated_score > self.best_score:
            self.best_score = calculated_score
            print("🎉 새로운 최고 점수입니다!")
            self.save_data()
        print("=" * 40)

    def add_quiz(self):
        """새로운 퀴즈 추가 기능"""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        try:
            question = input("문제를 입력하세요: ").strip()
            if not question:
                print("⚠️ 빈 문항은 등록할 수 없습니다.")
                return

            choices = []
            for i in range(1, 5):
                choice = input(f"선택지 {i}: ").strip()
                choices.append(choice)

            answer = self.get_validated_input("정답 번호 (1-4): ", 1, 4)

            new_quiz = Quiz(question, choices, answer)
            self.quizzes.append(new_quiz)
            self.save_data()
            print("✅ 퀴즈가 성공적으로 추가되었습니다!")
        except (KeyboardInterrupt, EOFError):
            print("\n⚠️ 입력을 취소합니다.")

    def show_quiz_list(self):
        """등록된 퀴즈 목록 확인"""
        if not self.quizzes:
            print("\n📋 등록된 퀴즈가 없습니다.")
            return

        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print("-" * 40)
        for i, q in enumerate(self.quizzes, 1):
            print(f"[{i}] {q.question}")
            for idx, choice in enumerate(q.choices, 1):
                print(f"    {idx}. {choice}")
        print("-" * 40)

    def show_score(self):
        """최고 점수 확인"""
        print("\n" + "=" * 40)
        print(f"🏆 최고 점수: {self.best_score}점")
        print("=" * 40)

    def run(self):
        """메인 실행 루프"""
        while True:
            print("\n" + "=" * 40)
            print("            🎯 나만의 퀴즈 게임 🎯")
            print("=" * 40)
            print("1. 퀴즈 풀기")
            print("2. 퀴즈 추가")
            print("3. 퀴즈 목록")
            print("4. 점수 확인")
            print("5. 종료")
            print("=" * 40)

            choice = self.get_validated_input("선택: ", 1, 5)

            if choice == 1:
                self.play_quiz()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_quiz_list()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                print("\n👋 프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
                break


if __name__ == "__main__":
    game = QuizGame()
    game.run()