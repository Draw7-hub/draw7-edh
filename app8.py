# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ------------------ Setup session ------------------
if 'players' not in st.session_state:
    st.session_state.players = {}
if 'rounds' not in st.session_state:
    st.session_state.rounds = []
if 'results' not in st.session_state:
    st.session_state.results = []  # เก็บผลการแข่งขันแต่ละรอบ
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'max_rounds' not in st.session_state:
    st.session_state.max_rounds = 3
if 'group_size' not in st.session_state:
    st.session_state.group_size = 4
if 'pending_winners' not in st.session_state:
    st.session_state.pending_winners = {}  # เก็บผู้ชนะที่เลือกในรอบนี้ ยังไม่ยืนยันคะแนน
if 'timeout_groups' not in st.session_state:
    st.session_state.timeout_groups = set()  # เก็บโต๊ะที่หมดเวลา

# ------------------ Style for theme ------------------
primary_color = "#0047AB"  # น้ำเงิน
secondary_color = "#D32F2F"  # แดง
accent_color = "#FFFFFF"  # ขาว

st.markdown(f"""
<style>
    /* Mobile-first responsive design */
    .main > div {{
        color: {primary_color};
        padding: 0 10px;
    }}
    
    .stButton > button {{
        background-color: {primary_color};
        color: {accent_color};
        border-radius: 8px;
        border: none;
        padding: 12px 20px;
        font-weight: bold;
        width: 100%;
        margin: 4px 0;
        font-size: 16px;
        min-height: 48px;
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
        padding: 12px 16px;
        font-size: 16px;
        width: 100%;
        min-height: 48px;
    }}
    
    .stTextArea>div>textarea {{
        border-radius: 8px;
        border: 1.5px solid {primary_color};
        padding: 12px 16px;
        font-size: 16px;
        min-height: 120px;
    }}
    
    .stSelectbox>div>div>div>div {{
        border-radius: 8px;
        border: 1.5px solid {primary_color};
        padding: 12px 16px;
        font-size: 16px;
        min-height: 48px;
    }}
    
    .remove-btn {{
        background-color: {secondary_color};
        color: {accent_color};
        border-radius: 5px;
        padding: 8px 12px;
        font-size: 14px;
        margin-left: 8px;
        border: none;
        cursor: pointer;
        min-height: 40px;
    }}
    

    
    /* Mobile responsive */
    @media (max-width: 768px) {{
        .stButton > button {{
            padding: 16px 20px;
            font-size: 18px;
            min-height: 52px;
        }}
        
        .main > div {{
            padding: 0 5px;
        }}
        
        .stTextInput>div>input, .stSelectbox>div>div>div>div {{
            padding: 14px 16px;
            font-size: 18px;
            min-height: 52px;
        }}
    }}
    
    @media (max-width: 480px) {{
        /* Responsive styles for small screens */
    }}
    
    /* Sidebar responsive */
    .css-1d391kg {{
        padding: 1rem 0.5rem;
    }}
    
    /* Table responsive */
    .stTable {{
        font-size: 16px;
    }}
    
    @media (max-width: 768px) {{
        .stTable {{
            font-size: 14px;
        }}
    }}
    
    @media (max-width: 480px) {{
        .stTable {{
            font-size: 12px;
        }}
    }}

</style>
""", unsafe_allow_html=True)


# ------------------ Title ------------------
st.title("🎴 Draw 7 EDH Pairing")
st.caption("Powered by Balu Draw Seven")

# ------------------ Sidebar ------------------
with st.sidebar:
    st.header("⚙️ Setup")

    group_size = st.selectbox("จำนวนคนต่อกลุ่ม", options=[3, 4, 5], index=[3,4,5].index(st.session_state.group_size))
    st.session_state.group_size = group_size

    max_r = st.number_input("ตั้งจำนวนรอบ", 1, 20, value=st.session_state.max_rounds)
    if st.button("อัปเดตจำนวนรอบ"):
        st.session_state.max_rounds = max_r

    st.markdown("---")
    


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
        st.session_state.pending_winners = {}
        st.session_state.timeout_groups = set()
        st.success("ล้างข้อมูลทั้งหมดเรียบร้อย")


# ------------------ Player List with remove button ------------------
st.subheader("👥 รายชื่อผู้เล่น")
if st.session_state.players:
    df = pd.DataFrame.from_dict(st.session_state.players, orient='index', columns=['คะแนน'])
    df = df.sort_values("คะแนน", ascending=False).reset_index()
    df.index += 1
    df.columns = ["ชื่อผู้เล่น", "คะแนน"]
    df_display = df.copy()
    df_display.insert(0, "อันดับ", df.index)
    for idx, row in df_display.iterrows():
        col1, col2, col3, col4 = st.columns([1,4,2,1])
        with col1:
            st.write(f"**{row['อันดับ']}**")
        with col2:
            st.write(row["ชื่อผู้เล่น"])
        with col3:
            st.write(f"{row['คะแนน']}")
        with col4:
            btn_label = f"ลบ"
            if st.button(btn_label, key=f"remove_{row['ชื่อผู้เล่น']}", help=f"ลบ {row['ชื่อผู้เล่น']}"):
                # ลบผู้เล่น
                st.session_state.players.pop(row['ชื่อผู้เล่น'], None)
                # ลบจาก pending_winners ถ้ามี
                st.session_state.pending_winners = {k:v for k,v in st.session_state.pending_winners.items() if v != row['ชื่อผู้เล่น']}
                st.rerun()
else:
    st.info("ยังไม่มีผู้เล่น")

# ------------------ Pairing ------------------
st.subheader(f"🔄 รอบที่ {st.session_state.current_round + 1} / {st.session_state.max_rounds}")


def can_start_new_round():
    return st.session_state.current_round < st.session_state.max_rounds

if st.button("🔀 จับกลุ่มรอบใหม่"):
    if not can_start_new_round():
        st.warning("ครบจำนวนรอบที่กำหนดแล้ว")
    elif len(st.session_state.players) < st.session_state.group_size:
        st.warning(f"ต้องมีผู้เล่นอย่างน้อย {st.session_state.group_size} คน")
    else:
        sorted_players = sorted(st.session_state.players.items(), key=lambda x: -x[1])
        groups = [sorted_players[i:i+st.session_state.group_size] for i in range(0, len(sorted_players), st.session_state.group_size)]
        st.session_state.rounds.append(groups)
        st.session_state.current_round += 1
        st.session_state.pending_winners = {}
        st.session_state.timeout_groups = set()
        st.success(f"จับกลุ่มรอบ {st.session_state.current_round} เรียบร้อย")

# ------------------ แก้ไขกลุ่ม ------------------
if st.session_state.rounds:
    st.markdown("### 📋 กลุ่มล่าสุด (แก้ไขได้)")
    last_round = st.session_state.rounds[-1]
    new_groups = []
    for i, group in enumerate(last_round):
        st.markdown(f"**โต๊ะที่ {i+1}**")
        group_names = [name for name, _ in group]
        edited = st.text_area(f"รายชื่อผู้เล่นโต๊ะ {i+1} (บรรทัดละชื่อ)", value="\n".join(group_names), key=f"group_edit_{i}")
        names = [n.strip() for n in edited.split("\n") if n.strip()]
        updated_group = []
        for n in names:
            score = st.session_state.players.get(n, 1000)
            st.session_state.players[n] = score
            updated_group.append((n, score))
        new_groups.append(updated_group)
    st.session_state.rounds[-1] = new_groups

# ------------------ กรอกผลการแข่งขัน ------------------
if st.session_state.rounds:
    st.subheader("✅ กรอกผลการแข่งขันรอบนี้")

    last_round = st.session_state.rounds[-1]

    # แสดงกลุ่มและเลือกผู้ชนะ (ค้างไว้ใน pending_winners)
    for i, group in enumerate(last_round):
        names = [name for name, _ in group]
        st.markdown(f"**โต๊ะที่ {i+1}**")
        sorted_players = sorted(st.session_state.players.items(), key=lambda x: -x[1])
        rank_map = {name: rank+1 for rank, (name, _) in enumerate(sorted_players)}
        for name in names:
            rank = rank_map.get(name, "-")
            st.write(f"{rank}. {name}")

        # แสดงสถานะว่าหมดเวลาหรือไม่
        if i in st.session_state.timeout_groups:
            st.warning("⏰ โต๊ะนี้หมดเวลา - ทุกคนจะได้รับ -3% คะแนน")

        col1, col2 = st.columns(2)
        with col1:
            winner_key = f"winner_select_{i}_round{st.session_state.current_round}"
            selected_winner = st.selectbox("เลือกผู้ชนะ", options=names, key=winner_key)
            # เก็บไว้ใน pending_winners
            st.session_state.pending_winners[i] = selected_winner
        
        with col2:
            timeout_key = f"timeout_{i}_round{st.session_state.current_round}"
            if st.button("⏰ หมดเวลาทุกคน", key=timeout_key):
                if i in st.session_state.timeout_groups:
                    st.session_state.timeout_groups.remove(i)
                    st.success("ยกเลิกสถานะหมดเวลา")
                else:
                    st.session_state.timeout_groups.add(i)
                    st.warning("ตั้งสถานะหมดเวลา - ทุกคนจะได้รับ -3% คะแนน")
                st.rerun()

    # ปุ่มยืนยันผลการแข่งขันรอบนี้ครั้งเดียวจบ
    if st.button("✔️ ยืนยันผลการแข่งขันรอบนี้"):
        if len(st.session_state.pending_winners) != len(last_round):
            st.warning("กรุณาเลือกผู้ชนะทุกโต๊ะก่อนยืนยัน")
        elif None in st.session_state.pending_winners.values():
            st.warning("กรุณาเลือกผู้ชนะทุกโต๊ะก่อนยืนยัน")
        else:
            # อัปเดตคะแนนจริง
            for i, group in enumerate(last_round):
                winner = st.session_state.pending_winners.get(i)
                if winner:
                    # ตรวจสอบว่าโต๊ะนี้หมดเวลาหรือไม่
                    if i in st.session_state.timeout_groups:
                        # ทุกคนในโต๊ะนี้ได้รับ -3% คะแนน
                        for name, _ in group:
                            current_score = st.session_state.players[name]
                            st.session_state.players[name] = int(current_score * 0.97)
                    else:
                        # ระบบคะแนนปกติ
                        losers = [n for n, _ in group if n != winner]
                        win_score = st.session_state.players[winner]
                        st.session_state.players[winner] = int(win_score * 1.07)
                        for loser in losers:
                            lose_score = st.session_state.players[loser]
                            st.session_state.players[loser] = int(lose_score * 0.93)
            
            # บันทึกผลรอบนี้
            st.session_state.results.append(st.session_state.pending_winners.copy())
            st.session_state.pending_winners = {}
            st.session_state.timeout_groups = set()
            st.success("บันทึกผลการแข่งขันรอบนี้เรียบร้อย")

# ------------------ ดูตารางอันดับคะแนน ------------------
if st.button("📊 ดูตารางอันดับคะแนน"):
    st.subheader("🏁 ตารางอันดับคะแนน")
    df = pd.DataFrame.from_dict(st.session_state.players, orient='index', columns=['คะแนน'])
    df = df.sort_values("คะแนน", ascending=False).reset_index()
    df.index += 1
    df.columns = ["ชื่อผู้เล่น", "คะแนน"]
    df_display = df.copy()
    df_display.insert(0, "อันดับ", df.index)
    st.table(df_display)

# ------------------ แสดงคนชนะแต่ละรอบ (สรุป) ------------------
if st.session_state.results:
    st.subheader("🏆 คนชนะแต่ละรอบ")
    for r, winners in enumerate(st.session_state.results, start=1):
        st.write(f"รอบที่ {r}:")
        for table_idx, winner in winners.items():
            st.write(f"  โต๊ะ {table_idx+1}: {winner}")