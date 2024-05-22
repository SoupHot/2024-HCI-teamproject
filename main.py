from openai import OpenAI
import streamlit as st
from configs import OAI_MODEL, EXPORT_DIR
from utils import export_current_conversation # num_tokens_from_messages
from datetime import datetime

st.title("챗봇 답변 요약 정도에 따른 문제풀이 사용성 테스트")
st.subheader("3조: 김예원, 구민서, 이효림, 함영욱")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = OAI_MODEL

if "messages" not in st.session_state:
    st.session_state.messages = []

if "messages_time_stamp" not in st.session_state: # 채팅 입력, 챗봇 답변 시간을 측정
    st.session_state.messages_time_stamp = []

# 세션 상태 초기화
if "start_solving_button_clicked" not in st.session_state:
    st.session_state.start_solving_button_clicked = False
if "end_solving_button_clicked" not in st.session_state:
    st.session_state.end_solving_button_clicked = True  # 처음에는 비활성화 상태
if "solve_problem_time_stamp" not in st.session_state:
    st.session_state.solve_problem_time_stamp = []

summary_level = st.sidebar.selectbox(
    "챗봇 답변의 요약 정도",
    ("상", "중", "하"),
    index=None,
    placeholder="Select summary level...",
)

persona_description = ""
if summary_level == "상":
    st.sidebar.success('선택 완료!', icon="✅")
    persona_description = """
        문제를 풀어주는 챗봇
        사용자와는 문제에 관한 얘기만 진행해
        문제에 대한 질문의 답은 정확히 답만을 보여주는 형식을 가져
        답에 대한 다른 설명은 추가하지마

        예시
        문제 : ERP를 보완하기 위해 만들어진 개념으로 기업 내 생산계획의 최적화를 넘어 전체 공급망 내 자원의 최적화를 목표로 하는 시스템은?
        답 : APS
        """
elif summary_level == "중":
    st.sidebar.success('선택 완료!', icon="✅")
    persona_description = """
        문제를 풀어주는 챗봇
        사용자와는 문제에 관한 얘기만 진행해
        문제에 대한 질문의 답과 간단한 설명을 추가해

        예시
        문제 : ERP를 보완하기 위해 만들어진 개념으로 기업 내 생산계획의 최적화를 넘어 전체 공급망 내 자원의 최적화를 목표로 하는 시스템은?
        답 : APS(Advanced Planning and Scheduling, 고급 계획 및 일정 관리)는 ERP 시스템을 보완하는 시스템으로, 기업 내 생산 계획의 최적화를 넘어 전체 공급망 내 자원의 최적화를 목표로 합니다. APS는 고급 알고리즘을 사용해 생산 일정, 자재 조달, 용량 계획 등을 최적화하여 생산 효율성을 높이고 비용을 절감하며, 고객 요구에 신속하게 대응할 수 있게 합니다.
        """
    
elif summary_level == "하":
    st.sidebar.success('선택 완료!', icon="✅")
    persona_description = """
        문제를 풀어주는 챗봇
        사용자와는 문제에 관한 얘기만 진행해
        문제에 대한 질문의 답과 자세한 설명을 추가해

        예시
        문제 : ERP를 보완하기 위해 만들어진 개념으로 기업 내 생산계획의 최적화를 넘어 전체 공급망 내 자원의 최적화를 목표로 하는 시스템은?
        답 : APS(Advanced Planning and Scheduling, 고급 계획 및 일정 관리)는 ERP 시스템을 보완하는 고도화된 계획 및 일정 관리 시스템입니다. APS는 복잡한 공급망과 제조 환경에서 자원의 최적화를 목표로 하며, 다양한 기능과 장점을 통해 기업의 생산성과 효율성을 향상시킵니다. APS의 주요 기능으로는 수요 계획, 생산 계획, 물류 계획, 자재 소요 계획, 용량 계획 등이 있습니다. 수요 계획은 시장 수요를 예측하고 이를 바탕으로 생산 계획을 수립하며, 생산 계획은 최적의 생산 일정과 자원 할당을 통해 생산 공정을 계획합니다. 물류 계획은 공급망 내의 물류 흐름을 최적화하고, 자재 소요 계획은 생산 계획에 따라 필요한 자재를 정확히 계산하여 조달 일정을 계획합니다. 용량 계획은 생산 설비와 작업자 용량을 최적화하여 생산 효율을 극대화합니다.

        APS의 장점으로는 효율성 증대, 비용 절감, 유연한 대응, 통합된 정보 관리, 고객 만족도 향상이 있습니다. 고도화된 알고리즘을 통해 생산 계획과 자원 배분의 효율성을 극대화하고, 재고 수준을 최적화하며, 불필요한 자재 구매를 줄여 비용을 절감합니다. 또한, 시장 변화와 고객 요구에 신속하게 대응할 수 있는 유연성을 제공하며, ERP 시스템과 통합하여 전사적인 데이터를 효과적으로 관리합니다. 이를 통해 정확한 수요 예측과 적시 생산을 통해 고객 요구를 신속히 충족시키고, 품질 향상과 납기 준수로 고객 만족도를 높입니다.

        APS의 도입 사례로는 제조업체, 유통업체, 자동차 산업 등이 있습니다. 대규모 제조업체는 APS를 도입하여 생산 계획과 자원 관리를 최적화하고, 복잡한 생산 공정과 다수의 제품 라인을 효과적으로 관리합니다. 유통업체는 물류와 재고 관리를 최적화하여 배송 시간을 단축하고 비용을 절감하며, 수요 변동에 빠르게 대응하여 재고 부족이나 과잉을 방지합니다. 자동차 제조업체는 APS를 통해 부품 조달과 생산 일정을 최적화하여 조립 라인의 효율성을 높이고, 글로벌 공급망을 효과적으로 관리하여 비용 절감과 생산성 향상을 달성합니다.

        결론적으로, APS는 복잡한 공급망과 제조 환경에서 자원의 최적화를 통해 생산성과 효율성을 극대화하는 필수적인 시스템입니다. 이를 통해 기업은 경쟁력을 강화하고, 비용을 절감하며, 고객 요구에 신속하게 대응할 수 있습니다. APS의 도입은 전사적인 생산 계획과 자원 관리를 통합하여 기업의 지속 가능한 성장을 지원합니다.
        """

else:
    st.sidebar.warning('챗봇 답변의 요약 정도를 선택해 주세요.', icon="⚠️")
    st.stop()


client = OpenAI(api_key=st.secrets["API_KEY"])

# 버튼을 클릭했을 때 호출되는 함수
def start_solving_button_click():
    st.session_state.start_solving_button_clicked = True
    st.session_state.end_solving_button_clicked = False
    st.session_state.solve_problem_time_stamp.append({"state": "start", "time_stamp": datetime.now()})

def end_solving_button_click():
    st.session_state.end_solving_button_clicked = True
    st.session_state.start_solving_button_clicked = False
    st.session_state.solve_problem_time_stamp.append({"state": "end", "time_stamp": datetime.now()})

# 버튼 생성 및 클릭 여부에 따른 비활성화 처리
if st.session_state.start_solving_button_clicked:
    st.sidebar.button("풀이 시작", disabled=True)
else:
    st.sidebar.button("풀이 시작", on_click=start_solving_button_click)
    # st.sidebar.success('시작!', icon="✅")

if st.session_state.end_solving_button_clicked:
    st.sidebar.button("풀이 완료", disabled=True)
else:
    st.sidebar.button("풀이 완료", on_click=end_solving_button_click)
    # st.sidebar.success('완료!', icon="✅")

# 엑셀 파일 생성 및 다운로드 버튼 추가 (풀이 완료 후 활성화)
export_button = st.sidebar.button("결과물 다운로드")

if export_button:
    excel_file = export_current_conversation(st.session_state.messages, st.session_state.messages_time_stamp, st.session_state.solve_problem_time_stamp)
    st.sidebar.download_button(
        label="Download conversation as Excel",
        data=excel_file,
        file_name="conversation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.sidebar.link_button("사용성 테스트 링크", "https://docs.google.com/forms/d/1Ckf-SXmMMVCK1oAfrxPcC6i6tNFMNAvbhBuQ4dCDZ1Y/edit?ts=664ad514")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 풀이 시작 버튼이 눌린 경우에만 채팅 입력 필드를 표시
if st.session_state.start_solving_button_clicked:
    if prompt := st.chat_input("문제에 대해 질문해 주세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages_time_stamp.append({"role": "user", "time_stamp": datetime.now()}) # 사용자 문장 입력 시간 측정
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[{"role": "system", "content": persona_description}] + 
                    [{"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages],
                stream=True,
            ):
                full_response += (response.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.messages_time_stamp.append({"role": "assistant", "time_stamp": datetime.now()}) # 챗봇 문장 답변 시간

# Use st.markdown with inline HTML styling to change text color
# st.markdown(f"<span style='color:red'>Total tokens used till now in conversation (your input + model's output): {num_tokens_from_messages(st.session_state.messages, OAI_MODEL)}</span>", unsafe_allow_html=True)