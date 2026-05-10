import streamlit as st
import random
import time

# Set page config for a cleaner look
st.set_page_config(page_title="Streamlit Snake", page_icon="🐍", layout="centered")

# Initialize session state variables
if 'snake' not in st.session_state:
    st.session_state.snake = [(10, 10), (10, 9), (10, 8)]
    st.session_state.direction = 'RIGHT'
    st.session_state.food = (10, 15)
    st.session_state.score = 0
    st.session_state.game_over = False

st.title("🐍 Streamlit Snake Game")
st.write("Use the buttons to play. The game auto-advances every 0.5 seconds.")

# Game Controls
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("⬆️ Up", use_container_width=True) and st.session_state.direction != 'DOWN':
        st.session_state.direction = 'UP'
with col1:
    if st.button("⬅️ Left", use_container_width=True) and st.session_state.direction != 'RIGHT':
        st.session_state.direction = 'LEFT'
with col3:
    if st.button("➡️ Right", use_container_width=True) and st.session_state.direction != 'LEFT':
        st.session_state.direction = 'RIGHT'
with col2:
    if st.button("⬇️ Down", use_container_width=True) and st.session_state.direction != 'UP':
        st.session_state.direction = 'DOWN'

# Game Logic
if not st.session_state.game_over:
    head_y, head_x = st.session_state.snake[0]
    
    if st.session_state.direction == 'UP':
        new_head = (head_y - 1, head_x)
    elif st.session_state.direction == 'DOWN':
        new_head = (head_y + 1, head_x)
    elif st.session_state.direction == 'LEFT':
        new_head = (head_y, head_x - 1)
    elif st.session_state.direction == 'RIGHT':
        new_head = (head_y, head_x + 1)
        
    # Check boundaries (20x20 grid) or collision with self
    if (new_head[0] < 0 or new_head[0] >= 20 or 
        new_head[1] < 0 or new_head[1] >= 20 or 
        new_head in st.session_state.snake):
        st.session_state.game_over = True
    else:
        st.session_state.snake.insert(0, new_head)
        
        # Check if food eaten
        if new_head == st.session_state.food:
            st.session_state.score += 10
            # Generate new food
            while True:
                new_food = (random.randint(0, 19), random.randint(0, 19))
                if new_food not in st.session_state.snake:
                    st.session_state.food = new_food
                    break
        else:
            st.session_state.snake.pop()

# UI Layout
st.markdown(f"### Score: {st.session_state.score}")

if st.session_state.game_over:
    st.error("Game Over! 💥")
    if st.button("Restart Game", type="primary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Render Grid using HTML and Emojis
grid_html = "<div style='line-height: 1.1; font-family: monospace; font-size: 18px; text-align: center; background-color: #1e1e1e; padding: 15px; border-radius: 10px; width: fit-content; margin: auto;'>"
for i in range(20):
    for j in range(20):
        if (i, j) == st.session_state.snake[0]:
            grid_html += "🟩" # Snake Head
        elif (i, j) in st.session_state.snake:
            grid_html += "🟢" # Snake Body
        elif (i, j) == st.session_state.food:
            grid_html += "🍎" # Food
        else:
            grid_html += "⬛" # Empty Background
    grid_html += "<br>"
grid_html += "</div>"

st.markdown(grid_html, unsafe_allow_html=True)

# Auto-refresh to keep the game moving continuously
if not st.session_state.game_over:
    time.sleep(0.5)
    st.rerun()
