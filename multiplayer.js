const mp = {
  userId: null,
  userName: '',
  connected: false,
  applyingRemote: false,
  eventSource: null,
  pingTimer: null,
  serverReady: false,
  sseOpen: false,
  roomUsers: [],
};

const SERVER_HINT =
  'Запустите в терминале: cd MotionPlayground_Web && ./run_local_server.sh\n' +
  'Затем откройте http://localhost:8080 (не открывайте index.html двойным кликом).';

function mpEl(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function setEntryStatus(text, ok) {
  const el = mpEl('entryStatus');
  if (!el) return;
  el.textContent = text;
  el.classList.toggle('online', ok);
  el.classList.toggle('offline', !ok);
}

function setSessionBadge(text, ok) {
  const el = mpEl('sessionBadge');
  if (!el) return;
  el.textContent = text;
  el.classList.toggle('online', ok);
  el.classList.toggle('offline', !ok);
}

function setEntryBusy(busy) {
  const btn = mpEl('entryConnectBtn');
  if (!btn) return;
  btn.disabled = busy;
  btn.setAttribute('aria-busy', busy ? 'true' : 'false');
}

function lockApp() {
  document.body.classList.remove('session-active');
  const gate = mpEl('entryGate');
  const main = mpEl('mainApp');
  if (gate) gate.hidden = false;
  if (main) main.inert = true;
  mp.connected = false;
  setSessionBadge('Не подключено', false);
  if (typeof window.motionStopApp === 'function') window.motionStopApp();
}

function unlockApp(userName) {
  document.body.classList.add('session-active');
  const gate = mpEl('entryGate');
  const main = mpEl('mainApp');
  if (gate) gate.hidden = true;
  if (main) main.inert = false;
  setSessionBadge(`Вы в сессии: ${userName}`, true);
  if (typeof window.motionInitApp === 'function') window.motionInitApp();
}

window.motionIsSessionActive = () => mp.connected;

function renderOnlineUsers(users) {
  const list = mpEl('onlineUsers');
  if (!list) return;
  list.innerHTML = '';
  for (const user of users || []) {
    const li = document.createElement('li');
    li.innerHTML = `<span class="user-dot" style="background:${user.color}"></span><span>${escapeHtml(user.name)}</span>`;
    list.appendChild(li);
  }
}


function normalizeUserState(user) {
  return {
    selectedKey: user?.state?.selectedKey || 'pulse',
    speed: Number(user?.state?.speed || 1),
    use3d: Boolean(user?.state?.use3d),
    combine: Boolean(user?.state?.combine),
    playing: user?.state?.playing !== false,
    modelRotX: Number(user?.state?.modelRotX ?? -18),
    modelRotY: Number(user?.state?.modelRotY ?? 28),
    theme: user?.state?.theme || 'neon',
  };
}

function showcaseShapeFor(key) {
  return ['rotate', 'slide', 'bounce'].includes(key) ? 'square' : 'circle';
}

function showcaseLabelFor(key) {
  const labels = { pulse: 'Pulse', rotate: 'Rotate', slide: 'Slide', fade: 'Fade', bounce: 'Bounce' };
  return labels[key] || key;
}

function showcaseCubeHtml(state) {
  const rotX = Number.isFinite(state.modelRotX) ? state.modelRotX : -18;
  const rotY = Number.isFinite(state.modelRotY) ? state.modelRotY : 28;
  const motionClass = state.playing ? `anim-${state.selectedKey}` : '';
  const combineClass = state.combine && state.playing ? 'anim-combine' : '';
  const spinClass = state.playing && (state.selectedKey === 'rotate' || state.combine) ? 'mini-rotate' : '';
  return `
    <div class="mini-model-motion ${motionClass} ${combineClass}" style="--speed:${Math.max(0.1, state.speed)};">
      <div class="mini-css-model ${spinClass}"
           style="--rx:${rotX}deg; --ry:${rotY}deg; --speed:${Math.max(0.1, state.speed)};">
        <div class="mini-cube3d">
          <span class="mini-face mini-front">3D</span>
          <span class="mini-face mini-back"></span>
          <span class="mini-face mini-right"></span>
          <span class="mini-face mini-left"></span>
          <span class="mini-face mini-top"></span>
          <span class="mini-face mini-bottom"></span>
        </div>
      </div>
    </div>
  `;
}


let showcaseDrag = null;

function setupShowcaseDesktopDrag(root) {
  if (!root || root.dataset.dragReady === '1') return;
  root.dataset.dragReady = '1';

  function self3dTarget(e) {
    const card = e.target.closest('.user-model-card.self');
    if (!card) return null;
    const model = card.querySelector('.mini-css-model');
    if (!model || !card.contains(e.target)) return null;
    return { card, model };
  }

  function begin(e, source, pointerId = null) {
    if (e.button !== undefined && e.button !== 0) return;
    const target = self3dTarget(e);
    if (!target) return;
    e.preventDefault();
    showcaseDrag = {
      source,
      pointerId,
      startX: e.clientX,
      startY: e.clientY,
      rotX: window.motionModelRotation?.x ?? -18,
      rotY: window.motionModelRotation?.y ?? 28,
      moved: false,
      model: target.model,
    };
    target.card.classList.add('dragging-3d');
    target.model.classList.add('dragging');
  }

  function move(e, source, pointerId = null) {
    if (!showcaseDrag || showcaseDrag.source !== source) return;
    if (pointerId !== null && showcaseDrag.pointerId !== pointerId) return;
    e.preventDefault();
    const dx = e.clientX - showcaseDrag.startX;
    const dy = e.clientY - showcaseDrag.startY;
    if (Math.abs(dx) + Math.abs(dy) > 2) showcaseDrag.moved = true;
    if (typeof window.motionRotateLocalModelBy === 'function') {
      window.motionRotateLocalModelBy(showcaseDrag, e.clientX, e.clientY);
    }
    if (showcaseDrag.model && window.motionModelRotation) {
      showcaseDrag.model.style.animation = 'none';
      showcaseDrag.model.style.transform = `rotateX(${window.motionModelRotation.x}deg) rotateY(${window.motionModelRotation.y}deg)`;
    }
  }

  function finish(source, pointerId = null) {
    if (!showcaseDrag || showcaseDrag.source !== source) return;
    if (pointerId !== null && showcaseDrag.pointerId !== pointerId) return;
    const moved = showcaseDrag.moved;
    root.querySelectorAll('.dragging-3d, .dragging').forEach(el => el.classList.remove('dragging-3d', 'dragging'));
    showcaseDrag = null;
    if (moved && typeof window.motionEmitModelRotation === 'function') window.motionEmitModelRotation();
  }

  root.addEventListener('pointerdown', (e) => {
    begin(e, 'pointer', e.pointerId);
    if (showcaseDrag) {
      try { root.setPointerCapture(e.pointerId); } catch {}
    }
  });
  root.addEventListener('pointermove', (e) => move(e, 'pointer', e.pointerId));
  root.addEventListener('pointerup', (e) => finish('pointer', e.pointerId));
  root.addEventListener('pointercancel', (e) => finish('pointer', e.pointerId));

  root.addEventListener('mousedown', (e) => begin(e, 'mouse', 'mouse'));
  document.addEventListener('mousemove', (e) => move(e, 'mouse', 'mouse'));
  document.addEventListener('mouseup', () => finish('mouse', 'mouse'));
  root.addEventListener('dragstart', (e) => e.preventDefault());
}

function renderUserShowcase(users) {
  const root = mpEl('usersShowcase');
  if (!root) return;
  setupShowcaseDesktopDrag(root);
  const list = Array.isArray(users) ? users : [];
  root.innerHTML = '';

  if (!list.length) {
    root.innerHTML = '<div class="showcase-empty">Нет подключившихся пользователей</div>';
    return;
  }

  for (const user of list) {
    const state = normalizeUserState(user);
    const card = document.createElement('article');
    card.className = `user-model-card ${user.id === mp.userId ? 'self' : ''}`;
    card.style.setProperty('--user-color', user.color || 'var(--accent)');
    card.style.setProperty('--speed', String(Math.max(0.1, state.speed)));

    const model = state.use3d
      ? showcaseCubeHtml(state)
      : `<div class="mini-actor ${state.playing ? `anim-${state.selectedKey}` : ''} ${state.combine && state.playing ? 'anim-combine' : ''}">
           <div class="mini-shape ${showcaseShapeFor(state.selectedKey)}"></div>
         </div>`;

    card.innerHTML = `
      <div class="user-model-name"><span class="user-dot" style="background:${user.color || 'var(--accent)'}"></span>${escapeHtml(user.name)}${user.id === mp.userId ? ' (вы)' : ''}</div>
      <div class="user-model-stage">${model}</div>
      <div class="user-model-meta">${state.use3d ? '3D-куб' : showcaseLabelFor(state.selectedKey)} · x${state.speed.toFixed(1)}</div>
    `;
    root.appendChild(card);
  }
}

function updateRoomUsers(users) {
  mp.roomUsers = Array.isArray(users) ? users : [];
  renderOnlineUsers(mp.roomUsers);
  renderUserShowcase(mp.roomUsers);
}

function appendFeedEntry(entry, scroll = true) {
  const feed = mpEl('activityFeed');
  if (!feed || !entry) return;

  const row = document.createElement('div');
  row.className = `feed-item feed-${entry.type}`;
  const time = new Date(entry.ts).toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
  const isSelf = entry.userId === mp.userId;
  row.innerHTML = `
    <span class="feed-time">${time}</span>
    <span class="feed-user" style="color:${entry.userColor || 'var(--accent)'}">${escapeHtml(entry.userName)}${isSelf ? ' (вы)' : ''}</span>
    <span class="feed-text">${escapeHtml(entry.text)}</span>
  `;
  feed.prepend(row);

  while (feed.children.length > 80) {
    feed.lastChild?.remove();
  }
  if (scroll) feed.scrollTop = 0;
}

function hydrateFeed(items) {
  const feed = mpEl('activityFeed');
  if (!feed) return;
  feed.innerHTML = '';
  for (const entry of (items || []).slice(-40)) {
    appendFeedEntry(entry, false);
  }
}

async function mpPost(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }
  if (!res.ok) {
    const err = new Error(data?.error || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return data;
}

function currentStatePatch() {
  return {
    selectedKey: window.motionState.selectedKey,
    speed: window.motionState.speed,
    use3d: window.motionState.use3d,
    combine: window.motionState.combine,
    playing: window.motionState.playing,
    modelRotX: window.motionModelRotation.x,
    modelRotY: window.motionModelRotation.y,
    theme: window.motionThemeSelect.value,
  };
}

function broadcastAction(type, text, patch = null) {
  if (!mp.connected || mp.applyingRemote) return;
  mpPost('/api/action', {
    userId: mp.userId,
    type,
    text,
    state: patch ?? currentStatePatch(),
  }).catch(() => {
    lockApp();
    setEntryStatus('Соединение потеряно. Войдите снова.', false);
  });
}

window.motionBroadcast = broadcastAction;

function applyRemoteState(remote) {
  if (typeof window.motionApplyRemoteState !== 'function') {
    throw new Error('app.js не загружен');
  }
  if (!mp.connected) return;
  mp.applyingRemote = true;
  try {
    window.motionApplyRemoteState(remote);
  } finally {
    mp.applyingRemote = false;
  }
}

function handleServerMessage(msg) {
  if (!mp.connected) return;
  if (msg.type === 'ping') return;

  if (msg.type === 'snapshot') {
    // Снимок комнаты больше не применяет чужое состояние объекта.
    // Каждый пользователь управляет своей фигурой независимо.
    updateRoomUsers(msg.users);
    hydrateFeed(msg.feed);
    return;
  }
  if (msg.type === 'action') {
    // Не применяем msg.state от других клиентов: объекты независимые.
    if (msg.users) updateRoomUsers(msg.users);
    if (msg.entry) {
      const user = msg.users?.find(u => u.id === msg.entry.userId);
      appendFeedEntry({ ...msg.entry, userColor: user?.color });
    }
    return;
  }
  if (msg.type === 'feed') {
    if (msg.users) updateRoomUsers(msg.users);
    if (msg.entry) {
      const user = msg.users?.find(u => u.id === msg.entry.userId);
      appendFeedEntry({ ...msg.entry, userColor: user?.color });
    }
  }
}

function startEventStream() {
  if (mp.eventSource) {
    mp.eventSource.close();
    mp.eventSource = null;
  }
  mp.sseOpen = false;

  const es = new EventSource('/api/events');
  mp.eventSource = es;

  es.onopen = () => {
    mp.sseOpen = true;
  };

  es.onmessage = (event) => {
    try {
      handleServerMessage(JSON.parse(event.data));
    } catch (err) {
      console.warn('SSE message parse error', err);
    }
  };

  es.onerror = () => {
    if (!mp.connected || !mp.sseOpen) return;
    if (mp.eventSource) mp.eventSource.close();
    mp.eventSource = null;
    setEntryStatus('Соединение потеряно. Введите имя и войдите снова.', false);
    lockApp();
    const input = mpEl('entryUserName');
    if (input) input.focus();
  };
}

function startPing() {
  if (mp.pingTimer) clearInterval(mp.pingTimer);
  mp.pingTimer = setInterval(() => {
    if (!mp.connected || !mp.userId) return;
    mpPost('/api/ping', { userId: mp.userId }).catch(() => {});
  }, 25000);
}

async function checkMultiplayerServer() {
  if (window.location.protocol === 'file:') {
    return { ok: false, message: 'Страница открыта как файл. ' + SERVER_HINT };
  }

  try {
    const res = await fetch('/api/room', { cache: 'no-store' });
    if (!res.ok) {
      return {
        ok: false,
        message:
          'Сервер без API. Запустите ./run_local_server.sh (не python3 -m http.server)',
      };
    }
    const data = await res.json();
    if (!data.multiplayer) {
      return { ok: false, message: 'Неверный ответ сервера. ' + SERVER_HINT };
    }
    return { ok: true, message: 'Введите имя и нажмите «Войти в сессию»' };
  } catch {
    return { ok: false, message: 'Сервер не запущен. ' + SERVER_HINT };
  }
}

function getEntryName() {
  const input = mpEl('entryUserName');
  return (input?.value || '').trim();
}

async function connectToRoom() {
  const input = mpEl('entryUserName');
  const form = mpEl('entryForm');

  if (!mp.serverReady) {
    const check = await checkMultiplayerServer();
    mp.serverReady = check.ok;
    if (!check.ok) {
      setEntryStatus(check.message, false);
      return;
    }
  }

  if (form && !form.reportValidity()) return;

  const name = getEntryName();
  if (!name) {
    input?.classList.add('invalid');
    input?.focus();
    setEntryStatus('Имя обязательно', false);
    return;
  }
  input?.classList.remove('invalid');

  setEntryBusy(true);
  setEntryStatus('Подключение…', false);

  try {
    const data = await mpPost('/api/join', { name });
    mp.userId = data.userId;
    mp.userName = data.userName;
    mp.connected = true;

    unlockApp(data.userName);

    if (data.state) applyRemoteState(data.state);
    updateRoomUsers(data.users);
    hydrateFeed(data.feed);

    startEventStream();
    startPing();

    setEntryStatus(`Подключено как ${data.userName}`, true);
  } catch (err) {
    console.error('connect failed', err);
    mp.connected = false;
    lockApp();
    if (err.status === 400) {
      input?.classList.add('invalid');
      input?.focus();
      setEntryStatus('Введите имя', false);
    } else if (err.status === 501 || err.status === 404) {
      setEntryStatus('Запустите ./run_local_server.sh', false);
    } else {
      setEntryStatus(`Не удалось подключиться: ${err.message}`, false);
    }
  } finally {
    setEntryBusy(false);
  }
}

async function initMultiplayer() {
  lockApp();

  const form = mpEl('entryForm');
  const input = mpEl('entryUserName');

  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      connectToRoom();
    });
  }

  input?.addEventListener('input', () => input.classList.remove('invalid'));

  const check = await checkMultiplayerServer();
  mp.serverReady = check.ok;
  setEntryStatus(check.message, false);
  input?.focus();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMultiplayer);
} else {
  initMultiplayer();
}
