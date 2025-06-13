# 🧠 Abalone Game

A digital implementation of the classic **Abalone** board game using **Python** and **Pygame**. This two-player abstract strategy game challenges players to tactically move marbles on a hexagonal board to push the opponent's marbles off the edge.

---

## 🎯 Game Objective

Abalone is a two-player abstract strategy board game. The objective is to **push six of your opponent's marbles off the board** before they do the same to you.

---

## 🧩 Board Overview

- The board is a **hexagonal grid** with **61 valid positions** (forming a hexagon with side-length 5).
- Each player starts with **14 marbles**:
  - **Black marbles** begin at the top.
  - **White marbles** begin at the bottom.
- Players take turns to move.

---

## 🕹️ Controls

- 🖱️ Click on your marbles to select (up to **3 aligned**).
- 🖱️ Click on a **green-highlighted position** to move the selected marbles.
- 🔁 Press **`R` key** to reset the game when it's over.

![Gameplay Screenshot](https://github.com/user-attachments/assets/124e6a6d-c2b6-4159-abf4-d3e0530696d8)

---

## 🧱 Game Rules

### 🪄 Marble Selection Rules

- You can select up to **3 of your own marbles**.
- Selected marbles must be **aligned in a straight line** (for inline moves).
- You can change your selection anytime before making a move.

---

### 🧭 Movement Rules

There are **two types of moves** in Abalone:

#### 1. Side-step (Broadside Move)

- Move selected marbles **sideways**, i.e., **not in line** with their arrangement.
- All destination positions must be **empty**.
- Useful for maneuvering or spreading out your marbles.

#### 2. Inline Move (Push Move)

- Move selected marbles **forward/backward** along the **same line**.
- You can **push opponent marbles** only if:
  - You have **more marbles** than the opponent chain.
  - The opponent chain is **no more than 2 marbles** long.
  - The space behind the opponent marbles is **empty** or **off-board**.

---

## 📦 Requirements

- Python 3.7+
- [Pygame](https://www.pygame.org/)  
  Install via pip:

```bash
pip install pygame




