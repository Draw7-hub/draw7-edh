
import streamlit as st
import pandas as pd

# ------------------ Setup session ------------------
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'rounds' not in st.session_state:
    st.session_state.rounds = []
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'max_rounds' not in st.session_state:
    st.session_state.max_rounds = 3
if 'group_size' not in st.session_state:
    st.session_state.group_size = 4

# ------------------ Style for theme ------------------
primary_color = "#0047AB"  # น้ำเงิน
secondary_color = "#D32F2F"  # แดง
accent_color = "#FFFFFF"  # ขาว

st.markdown(f"""
<style>
    .main > div {{
        color: {primary_color};
    }}
    .stButton > button {{
        background-color: {primary_color};
        color: {accent_color};
        border-radius: 8px;
        border: none;
        padding: 8px 15px;
        font-weight: bold;
    }}
    .stButton > button:hover {{
        background-color: {secondary_color};
        color: {accent_color};
    }}
    .css-1aumxhk {{
        background-color: {accent_color} !important;
    }}
    .stTextInput>div>input {{
        border-radius: 8px;
        border: 1.5px solid {primary_color};
        padding: 5px 10px;
    }}
    .stTextArea>div>textarea {{
        border-radius: 8px;
        border: 1.5px solid {primary_color};
        padding: 8px 10px;
    }}
    .stSelectbox>div>div>div>div {{
        border-radius: 8px;
        border: 1.5px solid {primary_color};
        padding: 5px 10px;
    }}
</style>
""", unsafe_allow_html=True)

# ------------------ Title ------------------
st.title("🎴 Draw 7 EDH Pairing")
st.caption("MTG Commander tournament pairing with Elo-like system")

# ------------------ Sidebar ------------------
with st.sidebar:
    st.header("⚙️ Setup")

    # จำนวนคนต่อกลุ่ม
    group_size = st.selectbox("จำนวนคนต่อกลุ่ม", options=[3, 4, 5], index=[3,4,5].index(st.session_state.group_size))
    st.session_state.group_size = group_size

    max_r = st.number_input("ตั้งจำนวนรอบ", 1, 20, value=st.session_state.max_rounds)
    if st.button("อัปเดตจำนวนรอบ"):
        st.session_state.max_rounds = max_r

    new_player = st.text_input("เพิ่มผู้เล่นใหม่")
    if st.button("➕ เพิ่มผู้เล่น"):
        if new_player and new_player not in st.session_state.players:
            st.session_state.players[new_player] = 1000
            st.success(f"เพิ่มผู้เล่น '{new_player}' เรียบร้อย")
        elif new_player in st.session_state.players:
            st.warning("ผู้เล่นนี้มีอยู่แล้ว")

    if st.button("🗑 ล้างรายชื่อผู้เล่นทั้งหมด"):
        st.session_state.players = {}
        st.session_state.rounds = []
        st.session_state.results = []
        st.session_state.current_round = 0
        st.success("ล้างข้อมูลทั้งหมดเรียบร้อย")

# ------------------ Player List ------------------
st.subheader("👥 รายชื่อผู้เล่น")
if st.session_state.players:
    df = pd.DataFrame.from_dict(st.session_state.players, orient='index', columns=['คะแนน'])
    st.dataframe(df.sort_values("คะแนน", ascending=False))
else:
    st.info("ยังไม่มีผู้เล่น")

# ------------------ Pairing ------------------
st.subheader(f"🔄 รอบที่ {st.session_state.current_round + 1} / {st.session_state.max_rounds}")

if st.button("🔀 จับกลุ่มรอบใหม่"):
    if st.session_state.current_round >= st.session_state.max_rounds:
        st.warning("ครบจำนวนรอบที่กำหนดแล้ว")
    elif len(st.session_state.players) < st.session_state.group_size:
        st.warning(f"ต้องมีผู้เล่นอย่างน้อย {st.session_state.group_size} คน")
    else:
        sorted_players = sorted(st.session_state.players.items(), key=lambda x: -x[1])
        groups = [sorted_players[i:i+st.session_state.group_size] for i in range(0, len(sorted_players), st.session_state.group_size)]
        st.session_state.rounds.append(groups)
        st.session_state.current_round += 1
        st.success(f"จับกลุ่มรอบ {st.session_state.current_round} เรียบร้อย")

# ------------------ แก้ไขกลุ่ม ------------------
if st.session_state.rounds:
    st.markdown("### 📋 กลุ่มล่าสุด (แก้ไขได้)")
    last_round = st.session_state.rounds[-1]
    new_groups = []
    for i, group in enumerate(last_round):
        st.markdown(f"**โต๊ะที่ {i+1}**")
        group_names = [name for name, _ in group]
        # แสดง textbox รายชื่อกลุ่ม (แยกบรรทัด)
        edited = st.text_area(f"รายชื่อผู้เล่นโต๊ะ {i+1} (บรรทัดละชื่อ)", value="\n".join(group_names), key=f"group_edit_{i}")
        # แปลงข้อความกลับเป็น list และให้คะแนน default 1000 หากคนใหม่
        names = [n.strip() for n in edited.split("\n") if n.strip()]
        updated_group = []
        for n in names:
            score = st.session_state.players.get(n, 1000)
            st.session_state.players[n] = score
            updated_group.append((n, score))
        new_groups.append(updated_group)
    st.session_state.rounds[-1] = new_groups

# ------------------ กรอกผลการแข่งขัน ------------------
if st.session_state.rounds and st.button("✅ กรอกผลการแข่งขันรอบนี้"):
    round_result = []
    for i, group in enumerate(st.session_state.rounds[-1]):
        names = [name for name, _ in group]
        winner = st.selectbox(f"ผู้ชนะโต๊ะ {i+1}", names, key=f"win_{i}")
        if winner:
            losers = [n for n in names if n != winner]
            win_score = st.session_state.players[winner]
            st.session_state.players[winner] = int(win_score * 1.07)
            for loser in losers:
                lose_score = st.session_state.players[loser]
                st.session_state.players[loser] = int(lose_score * 0.93)
            round_result.append((winner, losers))
    st.session_state.results.append(round_result)
    st.success("อัปเดตคะแนนเรียบร้อย")

# ------------------ ตารางอันดับ ------------------
if st.button("📊 ดูตารางอันดับคะแนน"):
    st.subheader("🏁 ตารางอันดับคะแนน")
    final_df = pd.DataFrame.from_dict(st.session_state.players, orient='index', columns=['คะแนน'])
    final_df = final_df.sort_values("คะแนน", ascending=False).reset_index()
    final_df.index += 1
    final_df.columns = ["อันดับ", "ชื่อผู้เล่น", "คะแนน"]
    st.table(final_df)
