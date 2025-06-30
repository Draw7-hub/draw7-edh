# Draw 7 EDH Pairing Web App with Streamlit
# Free version for deployment on Streamlit Cloud

import streamlit as st
import pandas as pd
import math
import json
from collections import defaultdict

# Initialize session state
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

st.title("🎴 Draw 7 EDH Pairing")
st.caption("MTG Commander tournament pairing with Elo-like system")

# Sidebar: Setup
with st.sidebar:
    st.header("⚙️ Setup")
    max_r = st.number_input("Set number of rounds", 1, 20, value=st.session_state.max_rounds)
    if st.button("Update Rounds"):
        st.session_state.max_rounds = max_r

    new_player = st.text_input("Add new player")
    if st.button("➕ Add Player"):
        if new_player and new_player not in st.session_state.players:
            st.session_state.players[new_player] = 1000
        elif new_player in st.session_state.players:
            st.warning("Player already exists.")

    if st.button("🗑 Clear All Players"):
        st.session_state.players = {}
        st.session_state.rounds = []
        st.session_state.results = []
        st.session_state.current_round = 0

# Player List
st.subheader("👥 Player List")
if st.session_state.players:
    df = pd.DataFrame.from_dict(st.session_state.players, orient='index', columns=['Score'])
    st.dataframe(df.sort_values("Score", ascending=False))
else:
    st.info("No players added yet.")

# Pair Next Round
st.subheader(f"🔄 Round {st.session_state.current_round + 1} / {st.session_state.max_rounds}")

if st.button("🔀 Pair Next Round"):
    if st.session_state.current_round >= st.session_state.max_rounds:
        st.warning("Maximum rounds reached")
    elif len(st.session_state.players) < 3:
        st.warning("Need at least 3 players")
    else:
        sorted_players = sorted(st.session_state.players.items(), key=lambda x: -x[1])
        group_size = 4 if len(sorted_players) % 4 < len(sorted_players) % 3 else 3
        groups = [sorted_players[i:i+group_size] for i in range(0, len(sorted_players), group_size)]
        st.session_state.rounds.append(groups)
        st.session_state.current_round += 1
        st.success(f"Round {st.session_state.current_round} paired.")

# Display current round pairing
if st.session_state.rounds:
    st.markdown("### 📋 Current Pairings")
    last_round = st.session_state.rounds[-1]
    for i, group in enumerate(last_round):
        names = [name for name, _ in group]
        st.write(f"Table {i+1}: {', '.join(names)}")

# Enter results
if st.session_state.rounds and st.button("✅ Enter Results for This Round"):
    round_result = []
    for i, group in enumerate(st.session_state.rounds[-1]):
        names = [name for name, _ in group]
        winner = st.selectbox(f"🏆 Winner of Table {i+1}", names, key=f"win_{i}")
        if winner:
            losers = [n for n in names if n != winner]
            win_score = st.session_state.players[winner]
            st.session_state.players[winner] = int(win_score * 1.07)
            for loser in losers:
                lose_score = st.session_state.players[loser]
                st.session_state.players[loser] = int(lose_score * 0.93)
            round_result.append((winner, losers))
    st.session_state.results.append(round_result)
    st.success("Scores updated.")

# Final standings
if st.button("📊 Show Standings"):
    st.subheader("🏁 Final Standings")
    final_df = pd.DataFrame.from_dict(st.session_state.players, orient='index', columns=['Score'])
    final_df = final_df.sort_values("Score", ascending=False).reset_index()
    final_df.index += 1
    final_df.columns = ["Rank", "Name", "Score"]
    st.table(final_df)

# Save/Load buttons
with st.expander("💾 Save/Load Tournament"):
    if st.download_button("⬇ Download Backup", data=json.dumps({
        "players": st.session_state.players,
        "rounds": st.session_state.rounds,
        "results": st.session_state.results,
        "current_round": st.session_state.current_round,
        "max_rounds": st.session_state.max_rounds
    }), file_name="draw7_tournament.json"):
        pass

    uploaded = st.file_uploader("⬆ Upload Tournament File", type="json")
    if uploaded:
        data = json.load(uploaded)
        st.session_state.players = data.get("players", {})
        st.session_state.rounds = data.get("rounds", [])
        st.session_state.results = data.get("results", [])
        st.session_state.current_round = data.get("current_round", 0)
        st.session_state.max_rounds = data.get("max_rounds", 3)
        st.success("Tournament loaded.")
