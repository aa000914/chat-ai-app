import streamlit as st
from openai import OpenAI

# =========================
# 1. API 配置
# =========================
API_KEY = st.secrets["DEEPSEEK_API_KEY"]

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

# =========================
# 2. 页面配置
# =========================
st.set_page_config(
    page_title="ChatMate AI",
    page_icon="💬",
    layout="wide"
)

# =========================
# 3. 自定义样式
# =========================
st.markdown("""
<style>
:root {
    --bg: #f5f7fb;
    --card: #ffffff;
    --border: #e8edf5;
    --text: #1f2937;
    --subtext: #6b7280;
    --primary: #4f46e5;
    --primary-soft: #eef2ff;
    --success-soft: #ecfdf3;
    --warning-soft: #fff7ed;
    --info-soft: #eff6ff;
    --shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    --radius: 18px;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #f8fbff 0%, #f5f7fb 100%);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    border-radius: 24px;
    padding: 28px 28px 24px 28px;
    color: white;
    box-shadow: var(--shadow);
    margin-bottom: 22px;
}

.hero-title {
    font-size: 34px;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 10px;
}

.hero-sub {
    font-size: 15px;
    line-height: 1.8;
    color: rgba(255,255,255,0.88);
    max-width: 760px;
}

.badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 16px;
}

.badge {
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.2);
    color: white;
    border-radius: 999px;
    padding: 7px 12px;
    font-size: 12px;
}

.panel {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 18px;
    box-shadow: var(--shadow);
}

.section-title {
    font-size: 20px;
    font-weight: 800;
    color: var(--text);
    margin-bottom: 6px;
}

.section-sub {
    font-size: 13px;
    color: var(--subtext);
    margin-bottom: 14px;
}

.result-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 16px;
    box-shadow: var(--shadow);
    height: 100%;
}

.result-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 10px;
}

.main-reply {
    background: linear-gradient(180deg, #f5f8ff 0%, #eef4ff 100%);
    border: 1px solid #dbe7ff;
    border-radius: 18px;
    padding: 18px;
    font-size: 17px;
    line-height: 1.8;
    color: var(--text);
    white-space: pre-wrap;
}

.small-reply {
    background: #fafcff;
    border: 1px solid #e7eefc;
    border-radius: 16px;
    padding: 14px;
    min-height: 140px;
    line-height: 1.8;
    color: var(--text);
    white-space: pre-wrap;
}

.tip-box {
    border-radius: 16px;
    padding: 14px 16px;
    line-height: 1.7;
    border: 1px solid transparent;
}

.tip-info {
    background: var(--info-soft);
    border-color: #dbeafe;
}

.tip-warn {
    background: var(--warning-soft);
    border-color: #fed7aa;
}

.tip-ok {
    background: var(--success-soft);
    border-color: #bbf7d0;
}

.divider-space {
    height: 10px;
}

.stButton > button {
    border-radius: 14px !important;
    height: 46px;
    font-weight: 700;
    border: 1px solid #dbe2f0 !important;
}

.stDownloadButton > button {
    border-radius: 14px !important;
    font-weight: 700;
    height: 44px;
}

[data-testid="stTextArea"] textarea {
    border-radius: 14px !important;
}

[data-baseweb="select"] > div {
    border-radius: 14px !important;
}

@media (max-width: 900px) {
    .hero-title {
        font-size: 28px;
    }
}
</style>
""", unsafe_allow_html=True)

# =========================
# 4. 头部
# =========================
st.markdown("""
<div class="hero">
    <div class="hero-title">💬 ChatMate AI</div>
    <div class="hero-sub">
        根据聊天上下文，帮你生成更自然、更舒服、更像真人的回复。
        支持自动回复、原回复优化、情绪判断和多种风格建议。
    </div>
    <div class="badge-row">
        <div class="badge">聊天上下文理解</div>
        <div class="badge">自动生成回复</div>
        <div class="badge">原回复优化</div>
        <div class="badge">情绪判断</div>
        <div class="badge">多风格建议</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# 5. session_state 初始化
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
# 6. 工具函数
# =========================
def clear_results():
    for key in default_keys:
        st.session_state[key] = ""


def call_deepseek(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个擅长中文聊天表达优化、情绪判断、上下文理解的助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
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
# 7. 左右布局
# =========================
left, right = st.columns([0.95, 1.25], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">输入区</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">填写聊天内容，选择场景和风格，然后生成结果。</div>', unsafe_allow_html=True)

    mode = st.radio(
        "模式",
        ["自动帮我回复", "修改我的回复"],
        horizontal=True
    )

    scene = st.selectbox(
        "聊天场景",
        ["通用", "她说累了", "她冷淡了", "她在分享日常", "她在吐槽", "她在试探你"]
    )

    chat_history = st.text_area(
        "聊天记录上下文（可选）",
        placeholder="例如：\n她：今天累死了\n你：怎么了\n她：开了一天会\n你：那也太折腾了",
        height=170
    )

    girl_msg = st.text_area(
        "她刚刚发来的内容",
        placeholder="例如：今天真的不想动了",
        height=120
    )

    my_reply = ""
    if mode == "修改我的回复":
        my_reply = st.text_area(
            "你原本想回复的话",
            placeholder="例如：那你早点睡",
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

    btn1, btn2 = st.columns(2)
    with btn1:
        generate_btn = st.button("生成结果", use_container_width=True)
    with btn2:
        regen_btn = st.button("再生成一版", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    if generate_btn or regen_btn:
        clear_results()

        if not girl_msg.strip():
            st.warning("请先输入她刚刚发来的内容。")
        elif mode == "修改我的回复" and not my_reply.strip():
            st.warning("请输入你原本想回复的话。")
        else:
            scene_rule = ""
            if scene == "她说累了":
                scene_rule = "重点是安慰和共情，不要讲道理。"
            elif scene == "她冷淡了":
                scene_rule = "回复要轻一点，不要追问，不要显得需求感太强。"
            elif scene == "她在分享日常":
                scene_rule = "要接住她的话，并自然延展话题。"
            elif scene == "她在吐槽":
                scene_rule = "先站在她这边，表达理解和支持。"
            elif scene == "她在试探你":
                scene_rule = "回答要稳，别太急着表态，也不要太油。"
            else:
                scene_rule = "正常自然聊天即可。"

            short_rule = "如果开启极简回复模式，请尽量控制每条回复在15字以内，简洁自然。" if simple_mode else "回复长度正常自然即可。"

            if mode == "自动帮我回复":
                prompt = f"""
你是一个中文聊天辅助助手。

任务：
结合聊天上下文和女生刚发来的内容，生成适合直接发送的回复。

要求：
1. 回复像真人
2. 不要油腻
3. 不要套路
4. 不要夸张
5. 不要爹味
6. 适合手机聊天
7. 每条回复都要能直接发送
8. 要参考上下文，避免答非所问
9. {short_rule}

聊天场景：
{scene}

场景策略：
{scene_rule}

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
结合聊天上下文，分析用户原回复是否合适，并给出优化版本。

要求：
1. 不要油腻
2. 不要套路
3. 不要夸张
4. 不要爹味
5. 要像真人聊天
6. 适合手机聊天场景
7. 给出的回复都要能直接发送
8. 要参考上下文
9. {short_rule}

聊天场景：
{scene}

场景策略：
{scene_rule}

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

    st.markdown('<div class="section-title">结果区</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">生成结果后，这里会展示情绪判断、推荐回复和备用回复。</div>', unsafe_allow_html=True)

    if st.session_state.raw_result:
        top1, top2 = st.columns(2)

        with top1:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">🧠 情绪判断</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="tip-box tip-info">{st.session_state.emotion_result or "暂无内容"}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with top2:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            if mode == "修改我的回复":
                st.markdown('<div class="result-title">⚠️ 原回复风险</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="tip-box tip-warn">{st.session_state.risk_result or "暂无内容"}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown('<div class="result-title">📌 聊天提醒</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="tip-box tip-warn">{st.session_state.advice_result or "暂无内容"}</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">💬 推荐回复</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="main-reply">{st.session_state.main_reply or "暂无内容"}</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
        st.download_button(
            label="下载推荐回复",
            data=st.session_state.main_reply or "",
            file_name="best_reply.txt",
            mime="text/plain",
            use_container_width=False
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
        st.markdown('<div class="result-title">📝 备用回复</div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">备用回复 1</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="small-reply">{st.session_state.backup_1 or "暂无内容"}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">备用回复 2</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="small-reply">{st.session_state.backup_2 or "暂无内容"}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">备用回复 3</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="small-reply">{st.session_state.backup_3 or "暂无内容"}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        if mode == "修改我的回复":
            st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown('<div class="result-title">✍️ 修改建议</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="tip-box tip-ok">{st.session_state.advice_result or "暂无内容"}</div>',
                unsafe_allow_html=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with st.expander("查看模型原始返回"):
            st.write(st.session_state.raw_result)
    else:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown('<div class="result-title">等待生成</div>', unsafe_allow_html=True)
        st.caption("左侧填写内容后，点击“生成结果”，这里会展示完整分析。")
        st.markdown('</div>', unsafe_allow_html=True)
