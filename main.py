import json
from anthropic import Anthropic

class DebateBot:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
        self.messages = []
        self.load_data()

        # 속성 초기화
        self.about_debate = """
        1. 가치논제는 옳은지 그른지, 바람직한지 아닌지, 좋은지 나쁜지 등 가치판단이 쟁점이 되는 논제입니다. 승패를 가를 때에는 논제를 더 잘 이해하고, 적절한 근거를 잘 제시했는지를 평가하게 됩니다.
        2. 반론/반박의 전략은 두 가지가 있습니다. 1)직접적/공격적으로 주장을 하는 방법은 상대방이 주장하고 제시한 내용들을 모두 반박하는 것입니다. 이런 방법을 취하기 위해서는 주장을 '잘' 들을 수 있어야 하고, 주장에 대해 '적절하게' 반박할 수 있어야 합니다. 2)방어적으로 주장을 하는 방법은 부정측의 입장을 토대로 주장을 세우고 시작하는 것입니다.
        3. 토론에서 이기기 위해 가장 중요한 것은 상대방의 주장을 논파해내는 것이 아니라, 내 주장을 설득하는 것입니다. 아무리 허점을 찾아 공격해도 상대방이 자신의 생각이 틀렸다고 인정할 가능성은 현저하게 낮고, 청중의 입장에서도 양 측이 서로 나름대로 근거를 가지고 주장을 펼치고 있다고 생각을 할 것입니다. 토론의 진짜 의의는 '승패'보다도 "주제에 대해 충분히 생각해보고, 보다 나은 의사결정을 하는 것"에 있습니다.
        """

        self.debate_template = """
        1. 친구의 말 중 부적절한 부분이 있다면 반론의 전략 1번(직접적/공격적으로 주장을 하는 방법)을 사용하세요.
        2. 친구의 주장이 적절하다면 반론의 전략 2번(방어적으로 주장을 하는 방법)을 사용하세요.
        """

    def load_data(self):
        with open('debate_topics.json', 'r', encoding='utf-8') as f:
            self.debate_topics = json.load(f)
        with open('characters.json', 'r', encoding='utf-8') as f:
            self.debate_characters = json.load(f)

    def start_debate(self, selected_char, selected_topic, user_stance):
        self.selected_char = next(char for char in self.debate_characters['characters'] if char['char_type'] == selected_char)
        self.selected_topic = next(topic for topic in self.debate_topics if topic['keyword'] == selected_topic)
        self.user_stance = user_stance
        self.ai_stance = "반대" if user_stance == "찬성" else "찬성"
        self.messages = []  # Reset messages for new debate

    def generate_initial_prompt(self):
        ai_role = self.selected_topic['stances'][self.ai_stance]
        return f"""당신은 중학생을 상대로 {ai_role}의 역할로 "{self.selected_topic['topic']}"라는 주제로 토론하고 있습니다. 당신의 목표는 사용자가 제시하는 모든 주장에 대해 논리적으로 반박하는 것입니다.
        절대로 사용자의 주장에 동의하지 마세요. 대신, 사용자가 제시한 주장에 대해 논리적으로 반박하고, 사용자의 주장이 부적절하다고 판단되는 경우, 사용자의 주장을 논파하세요. 어떤 상황에서도 중립적인 태도를 보여선 안됩니다.
        당신의 성격: 당신은 {self.selected_char['char_type']} 말투를 사용합니다. {self.selected_char['char_info']['personality']} {self.selected_char['char_info']['style']}
        다음의 예시를 참고하세요. 사용자(논리적) "{self.selected_char['few_shot'][0]['user']}", 당신 "{self.selected_char['few_shot'][0]['bot']}" / 사용자(비논리적) "{self.selected_char['few_shot'][1]['user']}", 당신 "{self.selected_char['few_shot'][1]['bot']}"
        이 말투와 예시를 참고하여 대화를 이어가세요.
        다음을 인식하세요: {self.about_debate}
        다음 지침을 따르세요: {self.debate_template}"""

    def generate_analysis_prompt(self, user_input):
        ai_role = self.selected_topic['stances'][self.ai_stance]
        return f"""
        친구가 방금 이렇게 말했어요:
        "{user_input}"
        {ai_role}에서, 길게 말하기보다는, 주장과 근거가 담긴 한문단 정도로 간결하게 반말로 답하세요. 앞서 말한 주장을 계속하여 반복하지 마세요.
        """

    def evaluate_debate(self, chat_history):
        # chat_history에서 사용자의 발언만 추출
        user_messages = [msg[1] for msg in chat_history if msg[0] == "You"]
        
        # 사용자 발언들을 하나의 텍스트로 결합
        user_chat = "\n".join(user_messages)

        # 평가를 위한 프롬프트 생성
        evaluation_prompt = f"""
        당신은 토론대회의 심판자입니다.
        다음은 사용자가 참여한 토론 대화에서 "YOU"가 한 발언들입니다:
        {user_chat}

        이 발언들에 대해 다음 기준에 따라 평가해 주세요:
        1. 주제의 일관성 : 발언들이 주제에 부합하고 일관성이 있는가?
        2. 논리적 연결성 : 발언들의 흐름과 논리적 연결성이 잘 유지되었는가?
        3. 반박의 적절성 : 상대방의 주장을 이해하고 적절히 반박하였는가?
        4. 근거의 타당성 : 주장에 대한 근거가 충분히 타당하고 논리적인가?
        5. 언어 선택의 적절성 : 발언 과정에서 적절한 언어가 사용되었는가?

        각 항목을 20점 만점으로 평가하고, 점수와 함께 간단한 코멘트와 개선을 위한 구체적인 조언을 제시해 주세요.
        개선 방안에서는 "YOU"가 실제로 말한 문장을 제시하고, 어떻게 바꾸면 더 나은 점수를 받을 수 있는지 구체적으로 설명해 주세요.
        마지막에는 총점(100점 만점)을 제시해 주세요.

        "반드시 아래의 json형식으로 반환해 주세요."
        {{
            "주제의 일관성": {{"점수": 점수, "코멘트": "코멘트", "개선방안": "개선을 위한 조언"}},
            "논리적 연결성": {{"점수": 점수, "코멘트": "코멘트", "개선방안": "개선을 위한 조언"}},
            "반박의 적절성": {{"점수": 점수, "코멘트": "코멘트", "개선방안": "개선을 위한 조언"}},
            "근거의 타당성": {{"점수": 점수, "코멘트": "코멘트", "개선방안": "개선을 위한 조언"}},
            "언어 선택의 적절성": {{"점수": 점수, "코멘트": "코멘트", "개선방안": "개선을 위한 조언"}},
            "총점": 0-100
        }}
        """

        # API 요청 보내기 (예제)
        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": evaluation_prompt}]
        )

        # 응답에서 텍스트 추출 및 JSON 파싱
        response_text = response.content[0].text

        try:
            evaluation_result = json.loads(response_text)
            return evaluation_result
        except json.JSONDecodeError:
            return {
                "주제의 일관성": {"점수": 0, "코멘트": "JSON 파싱 실패", "개선방안": "JSON 형식을 확인해 주세요."},
                "논리적 연결성": {"점수": 0, "코멘트": "JSON 파싱 실패", "개선방안": "JSON 형식을 확인해 주세요."},
                "반박의 적절성": {"점수": 0, "코멘트": "JSON 파싱 실패", "개선방안": "JSON 형식을 확인해 주세요."},
                "근거의 타당성": {"점수": 0, "코멘트": "JSON 파싱 실패", "개선방안": "JSON 형식을 확인해 주세요."},
                "언어 선택의 적절성": {"점수": 0, "코멘트": "JSON 파싱 실패", "개선방안": "JSON 형식을 확인해 주세요."},
                "총점": 0
            }



    def chat(self, user_input):
        analysis_prompt = self.generate_analysis_prompt(user_input)
        self.messages.append({"role": "user", "content": analysis_prompt})

        chat_messages = [msg for msg in self.messages if msg["role"] != "system"]

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=chat_messages,
            system=self.generate_initial_prompt(),
        )

        assistant_message = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_message})

        return assistant_message