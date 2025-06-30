# app.py
import streamlit as st
import pandas as pd
import time
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
if 'round_time' not in st.session_state:
    st.session_state.round_time = 75  # เวลาแต่ละรอบ (นาที)
if 'round_start_time' not in st.session_state:
    st.session_state.round_start_time = None
if 'timer_active' not in st.session_state:
    st.session_state.timer_active = False
if 'time_alerts_shown' not in st.session_state:
    st.session_state.time_alerts_shown = set()  # เก็บเวลาที่แจ้งเตือนแล้ว
if 'show_popup' not in st.session_state:
    st.session_state.show_popup = False
if 'popup_message' not in st.session_state:
    st.session_state.popup_message = ""

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
    
    /* Timer display - ใหญ่มากขึ้น */
    .timer-display {{
        text-align: center;
        padding: 40px 30px;
        border-radius: 20px;
        color: white;
        font-size: 72px;
        font-weight: bold;
        margin: 30px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    
    /* Popup styles */
    .popup-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(0,0,0,0.8);
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        box-sizing: border-box;
    }}
    
    .popup-content {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 30px;
        border-radius: 20px;
        box-shadow: 0 12px 24px rgba(0,0,0,0.4);
        text-align: center;
        max-width: 90%;
        width: 400px;
        animation: popup-slide 0.3s ease-out;
    }}
    
    @keyframes popup-slide {{
        from {{
            transform: translateY(-50px);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}
    
    .popup-message {{
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 25px;
        line-height: 1.3;
    }}
    
    .popup-close-btn {{
        background-color: white;
        color: {primary_color};
        border: none;
        padding: 15px 30px;
        border-radius: 10px;
        font-size: 18px;
        cursor: pointer;
        font-weight: bold;
        min-width: 100px;
        transition: all 0.2s ease;
    }}
    
    .popup-close-btn:hover {{
        background-color: #f0f0f0;
        transform: translateY(-2px);
    }}
    
    /* Mobile responsive */
    @media (max-width: 768px) {{
        .timer-display {{
            font-size: 48px;
            padding: 25px 20px;
            margin: 20px 0;
        }}
        
        .popup-content {{
            padding: 30px 20px;
            width: 95%;
            margin: 0 10px;
        }}
        
        .popup-message {{
            font-size: 22px;
        }}
        
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
        .timer-display {{
            font-size: 36px;
            padding: 20px 15px;
        }}
        
        .popup-message {{
            font-size: 20px;
        }}
        
        .popup-close-btn {{
            padding: 12px 24px;
            font-size: 16px;
        }}
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
    
    /* Player list responsive */
    .player-row {{
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        padding: 8px;
        border-radius: 8px;
        background-color: #f8f9fa;
    }}
    
    @media (max-width: 768px) {{
        .player-row {{
            flex-direction: column;
            align-items: stretch;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ------------------ Popup Component ------------------
def show_popup():
    if st.session_state.show_popup:
        popup_html = f"""
        <div class="popup-overlay" onclick="closePopup()">
            <div class="popup-content" onclick="event.stopPropagation();">
                <div class="popup-message">{st.session_state.popup_message}</div>
                <button class="popup-close-btn" onclick="closePopup()">OK</button>
            </div>
        </div>
        <script>
            function closePopup() {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'close_popup'}}, '*');
            }}
        </script>
        """
        st.components.v1.html(popup_html, height=0)

# Function to trigger popup
def trigger_popup(message):
    st.session_state.show_popup = True
    st.session_state.popup_message = message

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
    
    # ตั้งเวลาแต่ละรอบ
    st.subheader("⏰ ตั้งเวลาแต่ละรอบ")
    time_options = [60, 75, 90]
    round_time = st.selectbox("เลือกเวลาแต่ละรอบ (นาที)", 
                              options=time_options, 
                              index=time_options.index(st.session_state.round_time))
    st.session_state.round_time = round_time

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
        st.session_state.round_start_time = None
        st.session_state.timer_active = False
        st.session_state.time_alerts_shown = set()
        st.session_state.show_popup = False
        st.success("ล้างข้อมูลทั้งหมดเรียบร้อย")

# ------------------ Handle popup close ------------------
if hasattr(st, 'query_params'):
    query_params = st.query_params
    if 'close_popup' in query_params:
        st.session_state.show_popup = False
        st.query_params.clear()

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

# ------------------ Timer Display and Logic ------------------
if st.session_state.timer_active and st.session_state.round_start_time:
    current_time = datetime.now()
    elapsed_time = current_time - st.session_state.round_start_time
    total_seconds = st.session_state.round_time * 60
    elapsed_seconds = int(elapsed_time.total_seconds())
    remaining_seconds = max(0, total_seconds - elapsed_seconds)
    
    # Check for time alerts
    remaining_minutes = remaining_seconds // 60
    
    # Alert triggers
    alert_times = [15, 10, 5, 0]  # แจ้งเตือนที่ 15, 10, 5 นาที และหมดเวลา
    
    for alert_time in alert_times:
        if alert_time not in st.session_state.time_alerts_shown:
            if alert_time == 0 and remaining_seconds == 0:
                trigger_popup("⏰ หมดเวลาแล้ว!")
                st.session_state.time_alerts_shown.add(alert_time)
            elif alert_time > 0 and remaining_minutes == alert_time and remaining_seconds % 60 < 10:
                trigger_popup(f"⚠️ เหลือเวลาอีก {alert_time} นาที!")
                st.session_state.time_alerts_shown.add(alert_time)
    
    if remaining_seconds > 0:
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        
        # สีของเวลา
        if remaining_seconds > total_seconds * 0.5:
            color = "linear-gradient(135deg, #4CAF50, #45a049)"  # เขียว
        elif remaining_seconds > total_seconds * 0.25:
            color = "linear-gradient(135deg, #FF9800, #f57c00)"  # ส้ม
        else:
            color = "linear-gradient(135deg, #F44336, #d32f2f)"  # แดง
        
        st.markdown(f"""
        <div class="timer-display" style="background: {color};">
            ⏰ {minutes:02d}:{seconds:02d}
        </div>
        """, unsafe_allow_html=True)
        
        # Auto refresh every second
        time.sleep(1)
        st.rerun()
    else:
        st.markdown("""
        <div class="timer-display" style="background: linear-gradient(135deg, #F44336, #d32f2f);">
            ⏰ หมดเวลา!
        </div>
        """, unsafe_allow_html=True)

# Show popup if needed
show_popup()

# Timer controls
if st.session_state.rounds and not st.session_state.timer_active:
    if st.button("▶️ เริ่มนับเวลารอบนี้"):
        st.session_state.round_start_time = datetime.now()
        st.session_state.timer_active = True
        st.session_state.time_alerts_shown = set()  # รีเซ็ตการแจ้งเตือน
        st.success(f"เริ่มนับเวลา {st.session_state.round_time} นาที")
        st.rerun()

if st.session_state.timer_active:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏸️ หยุดเวลา"):
            st.session_state.timer_active = False
            st.info("หยุดนับเวลาแล้ว")
    with col2:
        if st.button("🔄 รีเซ็ตเวลา"):
            st.session_state.round_start_time = datetime.now()
            st.session_state.time_alerts_shown = set()  # รีเซ็ตการแจ้งเตือน
            st.success("รีเซ็ตเวลาแล้ว")
            st.rerun()

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
        st.session_state.timer_active = False
        st.session_state.round_start_time = None
        st.session_state.time_alerts_shown = set()  # รีเซ็ตการแจ้งเตือน
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

        winner_key = f"winner_select_{i}_round{st.session_state.current_round}"
        selected_winner = st.selectbox("เลือกผู้ชนะ", options=names, key=winner_key)

        # เก็บไว้ใน pending_winners
        st.session_state.pending_winners[i] = selected_winner

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
                    losers = [n for n, _ in group if n != winner]
                    win_score = st.session_state.players[winner]
                    st.session_state.players[winner] = int(win_score * 1.07)
                    for loser in losers:
                        lose_score = st.session_state.players[loser]
                        st.session_state.players[loser] = int(lose_score * 0.93)
            # บันทึกผลรอบนี้
            st.session_state.results.append(st.session_state.pending_winners.copy())
            st.session_state.pending_winners = {}
            st.session_state.timer_active = False
            st.session_state.round_start_time = None
            st.session_state.time_alerts_shown = set()  # รีเซ็ตการแจ้งเตือน
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