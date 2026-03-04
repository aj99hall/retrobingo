/**
 * Retro Bingo — client-side game logic
 *
 * Called from game.html via:
 *   initGame(hasBingo, hasFullhouse, markedArray)
 */

(function () {
  'use strict';

  let lastNotificationId = 0;
  let pollTimer = null;
  let localMarked = new Set();
  let localHasBingo = false;
  let localHasFullhouse = false;

  // -------------------------------------------------------------------------
  // Entry point
  // -------------------------------------------------------------------------

  window.initGame = function (hasBingo, hasFullhouse, markedArray) {
    localHasBingo = hasBingo;
    localHasFullhouse = hasFullhouse;
    localMarked = new Set(markedArray);

    bindTileClicks();
    startPolling();
  };

  // -------------------------------------------------------------------------
  // Tile interaction
  // -------------------------------------------------------------------------

  function bindTileClicks() {
    document.getElementById('bingo-grid').addEventListener('click', function (e) {
      const tile = e.target.closest('.tile');
      if (!tile) return;
      const index = parseInt(tile.dataset.index, 10);
      if (index === 12) return; // FREE tile — never toggle

      toggleTile(index);
    });
  }

  async function toggleTile(index) {
    try {
      const res = await fetch('/api/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ index }),
      });

      if (!res.ok) return;
      const data = await res.json();

      // Update local state
      localMarked = new Set(data.marked);
      renderMarked();

      if (data.new_bingo) {
        localHasBingo = true;
        showBingoOverlay();
        updateBingoBadge(true);
      }

      if (data.new_fullhouse) {
        localHasFullhouse = true;
        showFullhouseOverlay();
      }
    } catch (err) {
      console.error('mark error', err);
    }
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  function renderMarked() {
    const tiles = document.querySelectorAll('.tile');
    tiles.forEach(tile => {
      const idx = parseInt(tile.dataset.index, 10);
      if (idx === 12) return; // FREE — always styled separately
      if (localMarked.has(idx)) {
        tile.classList.add('tile--marked');
      } else {
        tile.classList.remove('tile--marked');
      }
    });
  }

  function updateBingoBadge(show) {
    const header = document.querySelector('.header');
    if (!header) return;
    if (show && !header.querySelector('.bingo-badge')) {
      const badge = document.createElement('span');
      badge.className = 'bingo-badge';
      badge.textContent = '★ BINGO ★';
      header.appendChild(badge);
    }
  }

  // -------------------------------------------------------------------------
  // Overlays
  // -------------------------------------------------------------------------

  function showBingoOverlay() {
    const overlay = document.getElementById('bingo-overlay');
    if (overlay) overlay.classList.add('active');
  }

  function showFullhouseOverlay() {
    const overlay = document.getElementById('fullhouse-overlay');
    if (overlay) overlay.classList.add('active');
    // Redirect after short delay
    setTimeout(() => {
      window.location.href = '/end';
    }, 2800);
  }

  // -------------------------------------------------------------------------
  // Polling for broadcast notifications
  // -------------------------------------------------------------------------

  function startPolling() {
    poll();
  }

  async function poll() {
    try {
      const url = '/api/poll?since=' + lastNotificationId;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        handlePollData(data);
      }
    } catch (err) {
      // Silently ignore network errors — will retry
    } finally {
      pollTimer = setTimeout(poll, 2000);
    }
  }

  function handlePollData(data) {
    if (!data.notifications) return;

    data.notifications.forEach(n => {
      if (n.id > lastNotificationId) lastNotificationId = n.id;

      if (n.type === 'fullhouse') {
        // Game over — show overlay then redirect
        if (!localHasFullhouse) {
          clearTimeout(pollTimer);
          showToast(n.message, 'fullhouse');
          setTimeout(() => {
            window.location.href = '/end';
          }, 2500);
        }
      } else if (n.type === 'bingo') {
        // Only show global BINGO toast for other players' BINGO
        // (own BINGO is handled in toggleTile via new_bingo flag)
        if (!data._ownBingo) {
          showToast(n.message, 'bingo');
        }
      }
    });

    // If game ended externally (e.g., another player got full house),
    // and we haven't already handled it above, redirect.
    if (!data.game_active && !localHasFullhouse) {
      clearTimeout(pollTimer);
      showToast('Full house! Game over!', 'fullhouse');
      setTimeout(() => {
        window.location.href = '/end';
      }, 2500);
    }
  }

  // showToast is defined in base.html and available globally
})();
