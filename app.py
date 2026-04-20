import streamlit as st
from openai import OpenAI

# =========================
# 1. API 配置
# =========================
API_KEY = "你的新DeepSeek_API_Key".strip()

client = OpenAI(
    api_key="sk-793d2a72d8fb4f7ebd42478b4a50b405",
    base_url="https://api.deepseek.com"
)

# =========================
# 2. 页面设置
# =========================
st.set_page_config(
    page_title="聊天辅助助手",
    page_icon="💬",
    layout="wide"
)

# =========================
# 3. 自定义样式
# =========================
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}
.main-title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 4px;
}
.sub-title {
    color: #666;
    margin-bottom: 20px;
}
.card {
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #e6e6e6;
    background-color: #fafafa;
    margin-bottom: 14px;
}
.card-title {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}
.reply-box {
    padding: 14px;
    border-radius: 12px;
    background-color: #f0f8ff;
    border: 1px solid #d7ebff;
    font-size: 16px;
    line-height: 1.7;
    white-space: pre-wrap;
}
.small-reply-box {
    padding: 12px;
    border-radius: 12px;
    background-color: #f8f8f8;
    border: 1px solid #ececec;
    min-height: 120px;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">💬 聊天辅助助手</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">支持聊天记录上下文、自动回复生成、原回复优化</div>', unsafe_allow_html=True)

# =========================
# 4. session_state 初始化
# =========================
default_keys = {
    "emotion_result": "",
    "risk_result": "",
    "main_reply": "",
    "backup_1": "",
    "backup_2": "",
    "backup_3": "",
    "advice_result": "",
    "raw_result": ""
}

for key, value in default_keys.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================
# 5. 工具函数
# =========================
def clear_results():
    for key in default_keys:
        st.session_state[key] = ""


def call_deepseek(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个擅长中文聊天表达优化、聊天情绪判断、上下文理解的助手。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    return response.choices[0].message.content


def extract_section(text: str, title: str) -> str:
    start = text.find(title)
    if start == -1:
        return ""
    start += len(title)

    next_titles = [
        "【情绪判断】",
        "【原回复风险】",
        "【推荐回复】",
        "【备用回复1】",
        "【备用回复2】",
        "【备用回复3】",
        "【修改建议】",
        "【提醒】"
    ]

    next_positions = []
    for t in next_titles:
        pos = text.find(t, start)
        if pos != -1:
            next_positions.append(pos)

    end = min(next_positions) if next_positions else len(text)
    return text[start:end].strip()


def parse_result(result: str, mode: str):
    st.session_state.raw_result = result
    st.session_state.emotion_result = extract_section(result, "【情绪判断】")
    st.session_state.risk_result = extract_section(result, "【原回复风险】")
    st.session_state.main_reply = extract_section(result, "【推荐回复】")
    st.session_state.backup_1 = extract_section(result, "【备用回复1】")
    st.session_state.backup_2 = extract_section(result, "【备用回复2】")
    st.session_state.backup_3 = extract_section(result, "【备用回复3】")

    if mode == "自动帮我回复":
        st.session_state.advice_result = extract_section(result, "【提醒】")
    else:
        st.session_state.advice_result = extract_section(result, "【修改建议】")


# =========================
# 6. 主布局
# =========================
left, right = st.columns([1, 1.25], gap="large")

with left:
    st.markdown("## 输入区")

    mode = st.radio(
        "选择模式",
        ["自动帮我回复", "修改我的回复"],
        horizontal=True
    )

    chat_history = st.text_area(
        "聊天记录上下文（可选）",
        placeholder="比如：\n她：今天累死了\n你：怎么了\n她：开了一天会\n你：那也太折腾了",
        height=180
    )

    girl_msg = st.text_area(
        "她刚刚发来的内容",
        placeholder="比如：今天真的不想动了",
        height=120
    )

    my_reply = ""
    if mode == "修改我的回复":
        my_reply = st.text_area(
            "你原本想回复的话",
            placeholder="比如：那你早点睡",
            height=100
        )

    chat_stage = st.selectbox(
        "你们目前的状态",
        ["刚认识", "普通聊天", "有点熟了", "她有点冷淡"]
    )

    reply_style = st.selectbox(
        "回复风格",
        ["自然温和", "轻松幽默", "高情商体贴", "简短不油腻"]
    )

    simple_mode = st.checkbox("极简回复模式（更短，更适合直接发送）", value=True)

    c1, c2 = st.columns(2)
    with c1:
        generate_btn = st.button("生成结果", use_container_width=True)
    with c2:
        regen_btn = st.button("再生成一版", use_container_width=True)

    if generate_btn or regen_btn:
        clear_results()

        if not girl_msg.strip():
            st.warning("请先输入她刚刚发来的内容。")
        elif mode == "修改我的回复" and not my_reply.strip():
            st.warning("请输入你原本想回复的话。")
        else:
            short_rule = "如果开启极简回复模式，请尽量控制每条回复在15字以内，简洁自然。" if simple_mode else "回复可以正常自然一些，不必刻意压短。"

            if mode == "自动帮我回复":
                prompt = f"""
你是一个中文聊天辅助助手。

任务：
结合聊天记录上下文、女生刚发来的内容，生成适合直接发送的回复。

要求：
1. 回复像真人
2. 不要油腻
3. 不要套路
4. 不要夸张
5. 不要爹味
6. 适合手机聊天
7. 每条回复都要能直接发送
8. 要参考聊天记录上下文，避免答非所问
9. {short_rule}

聊天阶段：
{chat_stage}

回复风格：
{reply_style}

聊天记录上下文：
{chat_history if chat_history.strip() else "无"}

女生刚发来的内容：
{girl_msg}

请严格按下面格式输出，不要多写：

【情绪判断】
一句话判断她现在的情绪状态

【推荐回复】
给出1条最适合直接发送的回复

【备用回复1】
给出第1条备用回复

【备用回复2】
给出第2条备用回复

【备用回复3】
给出第3条备用回复

【提醒】
一句话提醒用户现在该怎么聊
"""
            else:
                prompt = f"""
你是一个中文聊天优化助手。

任务：
结合聊天记录上下文，分析用户原回复是否合适，并给出优化版本。

要求：
1. 不要油腻
2. 不要套路
3. 不要夸张
4. 不要爹味
5. 要像真人聊天
6. 适合手机聊天场景
7. 给出的回复都要能直接发送
8. 要参考聊天记录上下文
9. {short_rule}

聊天阶段：
{chat_stage}

回复风格：
{reply_style}

聊天记录上下文：
{chat_history if chat_history.strip() else "无"}

女生刚发来的内容：
{girl_msg}

用户原本想回复：
{my_reply}

请严格按下面格式输出，不要多写：

【情绪判断】
一句话判断她现在的情绪状态

【原回复风险】
判断用户原回复属于：冷淡 / 用力过猛 / 太敷衍 / 还可以，并简要说明

【推荐回复】
给出优化后的最佳版本

【备用回复1】
给出第1条备用回复

【备用回复2】
给出第2条备用回复

【备用回复3】
给出第3条备用回复

【修改建议】
一句话说明为什么这样修改更好
"""

            with st.spinner("正在生成中..."):
                result = call_deepseek(prompt)
                parse_result(result, mode)

with right:
    st.markdown("## 结果区")

    if st.session_state.raw_result:
        top1, top2 = st.columns(2)

        with top1:
            st.markdown("""
            <div class="card">
                <div class="card-title">🧠 情绪判断</div>
            """, unsafe_allow_html=True)
            st.info(st.session_state.emotion_result or "暂无内容")
            st.markdown("</div>", unsafe_allow_html=True)

        with top2:
            if mode == "修改我的回复":
                st.markdown("""
                <div class="card">
                    <div class="card-title">⚠️ 原回复风险</div>
                """, unsafe_allow_html=True)
                st.warning(st.session_state.risk_result or "暂无内容")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="card">
                    <div class="card-title">📌 聊天提醒</div>
                """, unsafe_allow_html=True)
                st.warning(st.session_state.advice_result or "暂无内容")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 💬 推荐回复")
        st.markdown(
            f'<div class="reply-box">{st.session_state.main_reply or "暂无内容"}</div>',
            unsafe_allow_html=True
        )

        st.download_button(
            label="下载推荐回复",
            data=st.session_state.main_reply or "",
            file_name="best_reply.txt",
            mime="text/plain",
            use_container_width=False
        )

        st.markdown("### 📝 备用回复")
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            st.markdown("**备用回复1**")
            st.markdown(
                f'<div class="small-reply-box">{st.session_state.backup_1 or "暂无内容"}</div>',
                unsafe_allow_html=True
            )

        with col_b:
            st.markdown("**备用回复2**")
            st.markdown(
                f'<div class="small-reply-box">{st.session_state.backup_2 or "暂无内容"}</div>',
                unsafe_allow_html=True
            )

        with col_c:
            st.markdown("**备用回复3**")
            st.markdown(
                f'<div class="small-reply-box">{st.session_state.backup_3 or "暂无内容"}</div>',
                unsafe_allow_html=True
            )

        if mode == "修改我的回复":
            st.markdown("### ✍️ 修改建议")
            st.info(st.session_state.advice_result or "暂无内容")

        with st.expander("查看模型原始返回"):
            st.write(st.session_state.raw_result)
    else:
        st.info("左侧填写内容后，点击“生成结果”。")