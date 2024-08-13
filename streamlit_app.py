import streamlit as st
import os
from dotenv import load_dotenv
from main import DebateBot

# Load environment variables
load_dotenv()

# Initialize session state
if 'debate_bot' not in st.session_state:
    api_key = os.getenv("claude_api_key")
    if not api_key:
        st.error("API key not found. Please set it in your .env file.")
        st.stop()
    st.session_state.debate_bot = DebateBot(api_key)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'evaluation_result' not in st.session_state:
    st.session_state.evaluation_result = None

if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = None

if 'debate_started' not in st.session_state:
    st.session_state.debate_started = False

def display_message(sender, message):
    if sender == "You":
        st.markdown(
            f'''
            <div style="
                background-color: #007BFF; 
                color: white; 
                padding: 10px; 
                border-radius: 20px; 
                margin: 5px 0; 
                max-width: 70%; 
                float: right; 
                clear: both; 
                word-wrap: break-word;
                box-shadow: 0px 2px 12px rgba(0, 123, 255, 0.5);
            ">
                {message}
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.markdown(
            f'''
            <div style="
                background-color: #F1F1F1; 
                color: black; 
                padding: 10px; 
                border-radius: 20px; 
                margin: 5px 0; 
                max-width: 70%; 
                float: left; 
                clear: both; 
                word-wrap: break-word;
                box-shadow: 0px 2px 12px rgba(0, 0, 0, 0.1);
            ">
                {message}
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('<div style="clear: both;"></div>', unsafe_allow_html=True)

def main():
    st.markdown(
        """
        <style>
        .main {
            background-color: white;
        }
        .gray-text {
            color: gray;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
    """
    <div style="text-align: center;">
        <h1 style="color: #0184FF;">토독토독</h1>
    </div>
    """, 
    unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
        .stTextInput > div > input {
            background-color: #333333;
            color: white;
            border-radius: 20px;
            padding: 10px;
            box-shadow: 0px 2px 12px rgba(255, 255, 255, 0.1);
        }
        .stButton > button {
            background-color: white;
            color: black;
            border-radius: 20px;
            box-shadow: 0px 2px 12px rgba(232, 232, 232, 0.5);
        }
        .stButton > button:hover {
            background-color: #F1F1F1;
            color: black;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    # 캐릭터 선택
    char_options = [char['char_type'] for char in st.session_state.debate_bot.debate_characters['characters']]
    selected_char = st.selectbox("토론 상대의 말투를 선택해주세요:", char_options)

    # 토론 주제 선택
    topic_options = [topic['keyword'] for topic in st.session_state.debate_bot.debate_topics]
    selected_topic = st.selectbox("토론 주제를 선택해주세요:", topic_options)

    # 사용자가 '멋진 신세계'를 선택했을 때 줄거리 표시
    if selected_topic == "멋진 신세계":
        st.markdown(
            '''
            <p class="gray-text">
            소설은 미래의 세계를 배경으로 하며, 이 세계에서는 과학적 방법에 의해 인간이 체계적으로 생산되고 통제됩니다. 
            모든 사람은 인위적으로 만들어지고, 태어날 때부터 계급이 정해지며, 사회적 역할이 철저하게 배정됩니다. 
            사람들은 가짜 행복을 느끼도록 유전자 조작과 세뇌 교육을 통해 조정됩니다. 
            '소마(Soma)'라는 마약은 사람들이 고통을 잊고 쾌락만을 추구하게 만드는 도구로 사용됩니다.
            </p>
            ''', 
            unsafe_allow_html=True
        )

    # 사용자 입장 선택
    user_stance = st.radio("당신의 입장을 선택하세요:", ["찬성", "반대"])

    if st.button("토론 시작"):
        st.session_state.debate_bot.start_debate(selected_char, selected_topic, user_stance)
        st.session_state.debate_started = True
        st.session_state.chat_history = []
        st.session_state.evaluation_result = None
        st.session_state.selected_topic = selected_topic
        st.rerun()

    if st.session_state.get('debate_started', False):
        # 사용자 입장에 따라 메시지 표시
        if st.session_state.selected_topic == "멋진 신세계":
            if user_stance == "찬성":
                st.markdown(
                    '<p class="gray-text">당신은 가상세계에서 가짜 행복을 주입받는 세상에 찬성 하셨습니다. 즐겁게 토론 해보세요.</p>', 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<p class="gray-text">당신은 가상세계에서 가짜 행복을 주입받는 세상에 반대 하셨습니다. 즐겁게 토론 해보세요.</p>', 
                    unsafe_allow_html=True
                )

        
        # 채팅 히스토리 표시
        for sender, message in st.session_state.chat_history:
            display_message(sender, message)
            

        # 채팅 인터페이스
        with st.form(key='chat_form'):
            user_input = st.text_input("당신의 의견을 입력하세요:", key="user_input")
            col1, col2 = st.columns([1, 1])

            with col1:
                submit_button = st.form_submit_button("전송")

            with col2:
                end_debate_button = st.form_submit_button("토론 종료")

        if submit_button and user_input:
            st.session_state.chat_history.append(("You", user_input))
            response = st.session_state.debate_bot.chat(user_input)
            st.session_state.chat_history.append(("AI", response))
            st.rerun()

        if end_debate_button:
            # 사용자 발언만 필터링
            user_messages = [msg for sender, msg in st.session_state.chat_history if sender == "You"]
            
            # 사용자 발언만 평가
            st.session_state.evaluation_result = st.session_state.debate_bot.evaluate_debate(user_messages)
            st.session_state.debate_started = False
            st.rerun()

    # 평가 결과 표시
    if st.session_state.evaluation_result:
        result = st.session_state.evaluation_result
        if isinstance(result, dict) and all(key in result for key in ['주제의 일관성', '논리적 연결성', '반박의 적절성', '근거의 타당성', '언어 선택의 적절성', '총점']):
            st.subheader("토론 평가 결과")
            st.markdown(f"**총점: {result['총점']} / 100**")
            st.markdown("### 세부 평가")
            for key in ['주제의 일관성', '논리적 연결성', '반박의 적절성', '근거의 타당성', '언어 선택의 적절성']:
                st.markdown(f"**{key}**")
                st.markdown(f"- 점수: {result[key]['점수']} / 20")
                st.markdown(f"- 코멘트: {result[key]['코멘트']}")
                st.markdown(f"- 개선방안: {result[key]['개선방안']}")
        else:
            st.error("평가 결과를 처리하는 중 오류가 발생했습니다. 다시 시도해 주세요.")

        # 죄와벌 비디오 표시 로직
        if selected_topic == "비질란테":
            st.markdown("")
            st.markdown("")
            st.markdown("이 영상을 참고해보세요.")
            st.video("https://youtu.be/sXkKd88gdL0?si=q0g41YeWA1gbeZu0")

        # 멋진 신세계 비디오 표시 로직
        if selected_topic == "멋진 신세계":
            st.markdown("")
            st.markdown("")
            st.markdown("이 영상을 참고해보세요.")
            st.video("https://youtu.be/BQ-u_w9-IWg?si=Ln9NgvLQpdVHwRo8")

if __name__ == "__main__":
    main()
