# SETUP

1. The facilitator of the agile retrospective (https://www.atlassian.com/agile/scrum/retrospectives) displays a QR code.
2. Players scan the QR code using their phones.
3. Players enter their names.
4. Each player receives a randomly generated BINGO card.
5. The center tile is pre-marked as FREE.

All cards are generated from the same theme pool, ensuring a shared context. Each card layout is unique.

# THE BINGO CARD

- Grid size: 5x5.
- Center tile: FREE (automatically marked).
- Remaining tiles: RETRO themes (aligned with Agile principles).
- Tiles can be marked or unmarked by tapping.

# HOW TO PLAY

1. The RETRO begins.
2. As themes emerge in the discussion, players mark matching tiles on their cards.
3. Marking is individual; there is no host-controlled calling.
4. The game flows naturally alongside the RETRO conversation, without interrupting or dominating the session.

# WIN CONDITIONS

A player achieves BINGO by completing any line (horizontal, vertical, or diagonal).

When a player gets BINGO:
- They and all players receive a BINGO notification.
- That player cannot win BINGO again, but the game continues for others.

Players can continue marking tiles after achieving BINGO. A FULL HOUSE is achieved when all 25 tiles (including the FREE tile) are marked. Upon achieving FULL HOUSE:
- The player receives a distinct FULL HOUSE notification.
- All players are notified.
- The game ends, and players are taken to an end screen.

# GAME FLOW

1. Players join.
2. RETRO discussion proceeds.
3. Players mark tiles as themes arise.
4. One or more players achieve BINGO.
5. Players continue towards FULL HOUSE.
6. The RETRO concludes naturally, or the game ends if a player achieves FULL HOUSE.

# DESIGN PRINCIPLES

- Effortless joining process.
- No additional burden on the facilitator.
- Mobile-first interaction.
- Minimal visual distractions.
- Celebrations are concise and clear.
- Interface and design are as minimal and simple as possible to achieve this MVP.

RETRO BINGO is designed to _support_ the RETRO, not compete with it.

# IMPLEMENTATION

- The source code for the web app is version-controlled on GitHub: [RetroBingo Repository](https://github.com/aj99hall/retrobingo).
- The app is hosted on Render. Render automatically builds the Docker image from the repository's Dockerfile and serves the application at this URL: [RetroBingo on Render](https://retrobingo.onrender.com/).
- The tech stack consists of:

  - A single Docker container running a Python Flask web application.
  - SQLite as the database for lightweight and efficient data storage.
- The system is designed to support up to 20 concurrent users, with typical usage expected to be lower.

This implementation ensures alignment with the MVP by providing a lightweight, scalable, and easily deployable solution.

# CURRENT STATE
The current setup consists of a static website served using Nginx. While preserving this setup is not a priority, the new implementation must align with the details outlined in the IMPLEMENTATION section and this MVP doc. However, it is essential to retain the retro-themed style of the current static website to maintain consistency.

For example, the Dockerfile will need to be updated to serve the new Flask web application while preserving the retro aesthetic.

In summary, the task is to transform the existing static website into the dynamic implementation described in the IMPLEMENTATION section and this MVP doc, ensuring the retro theme is carried forward. The entire MVP should be implemented.