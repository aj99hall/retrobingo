import os
import json
import random
import uuid
import io
import base64

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, jsonify
)
import sqlite3
import qrcode

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)
app.secret_key = os.environ.get('SECRET_KEY', 'retrobingo-super-secret-key-change-me')

DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'retrobingo.db'))

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA journal_mode=WAL')
    return db


def init_db():
    with get_db() as db:
        db.executescript('''
            CREATE TABLE IF NOT EXISTS games (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                active  INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS players (
                id           TEXT PRIMARY KEY,
                game_id      INTEGER NOT NULL,
                name         TEXT NOT NULL,
                card         TEXT NOT NULL,
                marked       TEXT NOT NULL DEFAULT '[]',
                has_bingo    INTEGER NOT NULL DEFAULT 0,
                has_fullhouse INTEGER NOT NULL DEFAULT 0,
                joined_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(id)
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id    INTEGER NOT NULL,
                type       TEXT NOT NULL,
                message    TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(id)
            );
        ''')
        db.commit()
        # Ensure at least one active game exists
        row = db.execute('SELECT id FROM games WHERE active=1 LIMIT 1').fetchone()
        if not row:
            db.execute('INSERT INTO games (active) VALUES (1)')
            db.commit()


def get_active_game(db):
    return db.execute(
        'SELECT * FROM games WHERE active=1 ORDER BY id DESC LIMIT 1'
    ).fetchone()


# ---------------------------------------------------------------------------
# Game logic helpers
# ---------------------------------------------------------------------------

def load_questions():
    path = os.path.join(BASE_DIR, 'public', 'data', 'questions.json')
    with open(path) as f:
        data = json.load(f)
    return [q['text'] for q in data['questions']]


def generate_card(questions):
    """Return a 25-element list; index 12 is always FREE."""
    pool = random.sample(questions, min(24, len(questions)))
    return pool[:12] + ['FREE'] + pool[12:24]


def check_bingo(marked_set):
    """Return True if any row, column, or diagonal is fully marked."""
    N = 5
    for row in range(N):
        if all(row * N + col in marked_set for col in range(N)):
            return True
    for col in range(N):
        if all(row * N + col in marked_set for row in range(N)):
            return True
    if all(i * N + i in marked_set for i in range(N)):
        return True
    if all(i * N + (N - 1 - i) in marked_set for i in range(N)):
        return True
    return False


def check_fullhouse(marked_set):
    return len(marked_set) == 25


# ---------------------------------------------------------------------------
# QR code helper
# ---------------------------------------------------------------------------

def make_qr_b64(url: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Facilitator landing page — shows QR code and player count."""
    with get_db() as db:
        game = get_active_game(db)
        game_active = game is not None

        if game_active:
            player_count = db.execute(
                'SELECT COUNT(*) FROM players WHERE game_id=?', (game['id'],)
            ).fetchone()[0]
        else:
            # Show the most recent ended game's player count
            last_game = db.execute(
                'SELECT * FROM games ORDER BY id DESC LIMIT 1'
            ).fetchone()
            player_count = db.execute(
                'SELECT COUNT(*) FROM players WHERE game_id=?', (last_game['id'],)
            ).fetchone()[0] if last_game else 0

    join_url = request.host_url.rstrip('/') + url_for('join')
    qr_b64 = make_qr_b64(join_url)

    return render_template(
        'index.html',
        qr_b64=qr_b64,
        join_url=join_url,
        player_count=player_count,
        game_active=game_active,
    )


@app.route('/new-game', methods=['POST'])
def new_game():
    """Reset: mark all games inactive and start a fresh one."""
    with get_db() as db:
        db.execute('UPDATE games SET active=0')
        db.execute('INSERT INTO games (active) VALUES (1)')
        db.commit()
    session.pop('player_id', None)
    return redirect(url_for('index'))


@app.route('/join', methods=['GET', 'POST'])
def join():
    """Player join page — enter name and receive a bingo card."""
    with get_db() as db:
        game = get_active_game(db)
        if not game:
            return render_template('join.html', error='No active game right now.')

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            if not name:
                return render_template('join.html', error='Please enter your name.')
            if len(name) > 40:
                return render_template('join.html', error='Name must be 40 characters or fewer.')

            questions = load_questions()
            card = generate_card(questions)
            player_id = str(uuid.uuid4())

            # Index 12 (FREE tile) starts as marked
            marked = [12]

            db.execute(
                'INSERT INTO players (id, game_id, name, card, marked) VALUES (?, ?, ?, ?, ?)',
                (player_id, game['id'], name, json.dumps(card), json.dumps(marked))
            )
            db.commit()

            session['player_id'] = player_id
            return redirect(url_for('game'))

    return render_template('join.html')


@app.route('/game')
def game():
    """Player's bingo card."""
    player_id = session.get('player_id')
    if not player_id:
        return redirect(url_for('join'))

    with get_db() as db:
        player = db.execute('SELECT * FROM players WHERE id=?', (player_id,)).fetchone()
        if not player:
            return redirect(url_for('join'))

        game_row = db.execute('SELECT * FROM games WHERE id=?', (player['game_id'],)).fetchone()

    # If game ended and player hasn't seen the end screen, redirect
    if game_row and not game_row['active']:
        return redirect(url_for('end'))

    card = json.loads(player['card'])
    marked = json.loads(player['marked'])

    return render_template(
        'game.html',
        player=player,
        card=card,
        marked=marked,
        has_bingo=bool(player['has_bingo']),
        has_fullhouse=bool(player['has_fullhouse']),
    )


@app.route('/end')
def end():
    """End screen shown after full house."""
    player_id = session.get('player_id')
    player = None
    if player_id:
        with get_db() as db:
            player = db.execute('SELECT * FROM players WHERE id=?', (player_id,)).fetchone()
    return render_template('end.html', player=player)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.route('/api/mark', methods=['POST'])
def api_mark():
    """Toggle a tile mark. Returns updated state and any new win events."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json(force=True)
    tile_index = data.get('index')
    if tile_index is None or not isinstance(tile_index, int) or not (0 <= tile_index < 25):
        return jsonify({'error': 'Invalid tile index'}), 400

    with get_db() as db:
        player = db.execute('SELECT * FROM players WHERE id=?', (player_id,)).fetchone()
        if not player:
            return jsonify({'error': 'Player not found'}), 404

        game_row = db.execute('SELECT * FROM games WHERE id=?', (player['game_id'],)).fetchone()
        if not game_row or not game_row['active']:
            return jsonify({'error': 'Game is not active'}), 400

        marked = json.loads(player['marked'])
        marked_set = set(marked)

        # FREE tile (index 12) cannot be toggled
        if tile_index != 12:
            if tile_index in marked_set:
                marked_set.discard(tile_index)
            else:
                marked_set.add(tile_index)

        has_bingo = bool(player['has_bingo'])
        has_fullhouse = bool(player['has_fullhouse'])
        new_bingo = False
        new_fullhouse = False

        if not has_bingo and check_bingo(marked_set):
            has_bingo = True
            new_bingo = True
            db.execute(
                'INSERT INTO notifications (game_id, type, message) VALUES (?, ?, ?)',
                (game_row['id'], 'bingo', f"{player['name']} got BINGO!")
            )

        if not has_fullhouse and check_fullhouse(marked_set):
            has_fullhouse = True
            new_fullhouse = True
            db.execute(
                'INSERT INTO notifications (game_id, type, message) VALUES (?, ?, ?)',
                (game_row['id'], 'fullhouse', f"{player['name']} got FULL HOUSE! Game over!")
            )
            # End the game
            db.execute('UPDATE games SET active=0 WHERE id=?', (game_row['id'],))

        db.execute(
            'UPDATE players SET marked=?, has_bingo=?, has_fullhouse=? WHERE id=?',
            (json.dumps(sorted(marked_set)), int(has_bingo), int(has_fullhouse), player_id)
        )
        db.commit()

    return jsonify({
        'marked': sorted(marked_set),
        'has_bingo': has_bingo,
        'has_fullhouse': has_fullhouse,
        'new_bingo': new_bingo,
        'new_fullhouse': new_fullhouse,
    })


@app.route('/api/poll')
def api_poll():
    """Long-poll endpoint for broadcast notifications."""
    player_id = session.get('player_id')
    if not player_id:
        return jsonify({'error': 'Not authenticated'}), 401

    since_id = request.args.get('since', 0, type=int)

    with get_db() as db:
        player = db.execute('SELECT * FROM players WHERE id=?', (player_id,)).fetchone()
        if not player:
            return jsonify({'notifications': [], 'game_active': False})

        game_row = db.execute('SELECT * FROM games WHERE id=?', (player['game_id'],)).fetchone()
        notifications = db.execute(
            'SELECT id, type, message FROM notifications WHERE game_id=? AND id>? ORDER BY id ASC',
            (player['game_id'], since_id)
        ).fetchall()

    return jsonify({
        'notifications': [
            {'id': n['id'], 'type': n['type'], 'message': n['message']}
            for n in notifications
        ],
        'game_active': bool(game_row['active']) if game_row else False,
    })


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
