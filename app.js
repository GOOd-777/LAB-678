const animations = [
  { key: 'pulse', name: 'Pulse', previewColor: '#38BDF8', stageBackground: '#0EA5E9', shape: 'circle' },
  { key: 'rotate', name: 'Rotate', previewColor: '#A78BFA', stageBackground: '#7C3AED', shape: 'square' },
  { key: 'slide', name: 'Slide', previewColor: '#34D399', stageBackground: '#10B981', shape: 'square' },
  { key: 'fade', name: 'Fade', previewColor: '#FBBF24', stageBackground: '#F59E0B', shape: 'circle' },
  { key: 'bounce', name: 'Bounce', previewColor: '#F472B6', stageBackground: '#DB2777', shape: 'square' },
];

const THEME_LABELS = { dark: 'Dark', neon: 'Neon', pastel: 'Pastel' };

const state = {
  selectedKey: 'pulse',
  speed: 1,
  use3d: false,
  combine: false,
  playing: true,
  runningAnimations: [],
  loadedModel: null,
};

const modelRotation = { x: -18, y: 28 };
let animRotY = 0;
let modelDrag = null;

const body = document.body;
const stage = document.getElementById('stage');
const actor = document.getElementById('actor');
const shape = document.getElementById('shape');
const model3d = document.getElementById('model3d');
const list = document.getElementById('animationList');
const themeSelect = document.getElementById('themeSelect');
const use3d = document.getElementById('use3d');
const speed = document.getElementById('speed');
const speedValue = document.getElementById('speedValue');
const combine = document.getElementById('combine');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');

window.motionState = state;
window.motionModelRotation = modelRotation;
window.motionThemeSelect = themeSelect;

function selectedAnimation() {
  return animations.find(item => item.key === state.selectedKey) ?? animations[0];
}

function animLabel(key) {
  return animations.find(item => item.key === key)?.name ?? key;
}

function shapeLabel(key) {
  const item = animations.find(a => a.key === key);
  return item?.shape === 'square' ? 'квадрат' : 'круг';
}

function emit(type, text, patch) {
  if (!window.motionIsSessionActive?.()) return;
  if (typeof window.motionBroadcast === 'function') {
    window.motionBroadcast(type, text, patch);
  }
}

function renderAnimations() {
  list.innerHTML = '';
  for (const item of animations) {
    const btn = document.createElement('button');
    btn.id = `anim-${item.key}`;
    btn.className = `anim-card ${item.key === state.selectedKey ? 'active' : ''}`;
    btn.type = 'button';
    btn.setAttribute('role', 'option');
    btn.setAttribute('aria-selected', item.key === state.selectedKey ? 'true' : 'false');
    btn.innerHTML = `<span class="dot" style="background:${item.previewColor}"></span><span>${item.name}</span>`;
    btn.addEventListener('click', () => {
      state.selectedKey = item.key;
      renderAnimations();
      applySelectedAnimation();
      state.playing = true;
      start({ broadcast: true, actionType: 'animation' });
    });
    list.appendChild(btn);
  }
}

function applyModelTransform() {
  if (!model3d) return;
  model3d.style.transform = `rotateX(${modelRotation.x}deg) rotateY(${modelRotation.y + animRotY}deg)`;
}

function setModelRotationFromDrag(start, clientX, clientY) {
  const dx = clientX - start.startX;
  const dy = clientY - start.startY;
  modelRotation.y = start.rotY + dx * 0.5;
  modelRotation.x = Math.max(-85, Math.min(85, start.rotX - dy * 0.5));
  applyModelTransform();
}

window.motionRotateLocalModelBy = function motionRotateLocalModelBy(start, clientX, clientY) {
  setModelRotationFromDrag(start, clientX, clientY);
};

window.motionEmitModelRotation = function motionEmitModelRotation() {
  emit(
    'model_rotate',
    `повернул 3D-куб (X: ${Math.round(modelRotation.x)}°, Y: ${Math.round(modelRotation.y)}°)`,
  );
};

function applyTheme(theme) {
  body.classList.remove('theme-dark', 'theme-neon', 'theme-pastel');
  body.classList.add(`theme-${theme}`);
  themeSelect.value = theme;
}

function applySelectedAnimation() {
  const item = selectedAnimation();
  const loaded = state.loadedModel;
  stage.style.backgroundColor = loaded?.stageBackground || item.stageBackground;
  const shapeName = loaded?.shape === 'cube' ? 'square' : (loaded?.shape || item.shape);
  shape.className = `shape ${shapeName}`;
  if (loaded?.previewColor) shape.style.background = loaded.previewColor;
  else shape.style.removeProperty('background');
  shape.style.display = state.use3d ? 'none' : 'block';
  model3d.classList.toggle('hidden', !state.use3d);
  if (state.use3d) applyModelTransform();
  const nameEl = document.getElementById('loadedModelName');
  if (nameEl) nameEl.textContent = loaded?.name || 'Модель не загружена';
}

function stop(options = {}) {
  const { broadcast = false } = options;
  for (const animation of state.runningAnimations) animation.cancel();
  state.runningAnimations = [];
  actor.style.transform = 'translate(0, 0) scale(1) rotate(0deg)';
  actor.style.opacity = '1';
  animRotY = 0;
  modelRotation.x = -18;
  modelRotation.y = 28;
  applyModelTransform();
  state.playing = false;
  if (broadcast) {
    emit('stop', 'остановил анимацию');
  }
}

function makeKeyframes(key) {
  if (key === 'pulse') return [{ transform: 'scale(1)' }, { transform: 'scale(1.15)' }, { transform: 'scale(1)' }];
  if (key === 'rotate') return [{ transform: 'rotate(0deg)' }, { transform: 'rotate(360deg)' }];
  if (key === 'slide') return [
    { transform: 'translateX(0)' },
    { transform: 'translateX(70px)' },
    { transform: 'translateX(0)' },
    { transform: 'translateX(-70px)' },
    { transform: 'translateX(0)' },
  ];
  if (key === 'fade') return [{ opacity: 1 }, { opacity: 0.25 }, { opacity: 1 }];
  if (key === 'bounce') return [
    { transform: 'translateY(0)', easing: 'cubic-bezier(.2,.8,.2,1)' },
    { transform: 'translateY(-50px)', easing: 'cubic-bezier(.2,.8,.2,1)' },
    { transform: 'translateY(0)', easing: 'cubic-bezier(.34,1.56,.64,1)' },
  ];
  return [];
}

function durationFor(key) {
  const base = { pulse: 1200, rotate: 3000, slide: 2000, fade: 1500, bounce: 1500 }[key] ?? 1000;
  return base / Math.max(0.1, state.speed);
}

function runCssAnimation(key) {
  const animation = actor.animate(makeKeyframes(key), {
    duration: durationFor(key),
    iterations: Infinity,
    easing: key === 'rotate' ? 'linear' : 'ease-in-out',
  });
  state.runningAnimations.push(animation);
}

function runModelRotation() {
  let frameId = null;
  const started = performance.now();
  const duration = durationFor('rotate');
  let active = true;

  function tick(now) {
    if (!active) return;
    animRotY = (((now - started) % duration) / duration) * 360;
    applyModelTransform();
    frameId = requestAnimationFrame(tick);
  }

  frameId = requestAnimationFrame(tick);
  state.runningAnimations.push({ cancel: () => { active = false; cancelAnimationFrame(frameId); } });
}

function start(options = {}) {
  const { broadcast = false, actionType = 'start', silent = false } = options;
  if (!silent) {
    for (const animation of state.runningAnimations) animation.cancel();
    state.runningAnimations = [];
    actor.style.transform = 'translate(0, 0) scale(1) rotate(0deg)';
    actor.style.opacity = '1';
    animRotY = 0;
    if (!state.use3d) {
      modelRotation.x = -18;
      modelRotation.y = 28;
    }
    applyModelTransform();
  }

  applySelectedAnimation();

  const key = selectedAnimation().key;
  if (state.use3d && key === 'rotate') runModelRotation();
  else runCssAnimation(key);

  if (state.combine) {
    if (key !== 'rotate') {
      if (state.use3d) runModelRotation();
      else runCssAnimation('rotate');
    }
    if (key !== 'pulse') runCssAnimation('pulse');
  }

  state.playing = true;
  if (broadcast) {
    const mode = state.use3d ? '3D-куб' : `2D, ${shapeLabel(key)}`;
    const extra = state.combine ? ', комбинация Вращение + Пульс' : '';
    const item = selectedAnimation();
    emit(
      actionType,
      `выбрал анимацию ${animLabel(key)} (${mode}), цвет сцены ${item.stageBackground}${extra}`,
    );
  }
}

window.motionApplyRemoteState = function applyRemoteState(remote) {
  state.selectedKey = remote.selectedKey ?? state.selectedKey;
  state.speed = Number(remote.speed ?? state.speed);
  state.use3d = Boolean(remote.use3d);
  state.combine = Boolean(remote.combine);
  modelRotation.x = Number(remote.modelRotX ?? modelRotation.x);
  modelRotation.y = Number(remote.modelRotY ?? modelRotation.y);

  applyTheme(remote.theme ?? themeSelect.value);
  use3d.checked = state.use3d;
  combine.checked = state.combine;
  speed.value = String(state.speed);
  speedValue.textContent = `x${state.speed.toFixed(1)}`;

  renderAnimations();
  applySelectedAnimation();

  if (remote.playing) start({ silent: true });
  else stop();
};

themeSelect.addEventListener('change', () => {
  applyTheme(themeSelect.value);
  emit('theme', `сменил тему на ${THEME_LABELS[themeSelect.value] ?? themeSelect.value}`);
});

use3d.addEventListener('change', () => {
  state.use3d = use3d.checked;
  applySelectedAnimation();
  const text = state.use3d ? 'включил 3D-режим (куб)' : 'выключил 3D, показал 2D-фигуру';
  emit('mode', text);
  start({ broadcast: true, actionType: 'mode' });
});

speed.addEventListener('input', () => {
  state.speed = Number(speed.value);
  speedValue.textContent = `x${state.speed.toFixed(1)}`;
  if (state.playing) start({ silent: true });
  emit('speed', `изменил скорость на x${state.speed.toFixed(1)}`);
});

combine.addEventListener('change', () => {
  state.combine = combine.checked;
  const text = state.combine
    ? 'включил комбинацию: Вращение + Пульс'
    : 'выключил комбинацию анимаций';
  emit('combine', text);
  if (state.playing) start({ broadcast: true, actionType: 'combine' });
});

startBtn.addEventListener('click', () => start({ broadcast: true }));
stopBtn.addEventListener('click', () => stop({ broadcast: true }));

function setupModelDrag() {
  if (!stage) return;

  function canStartFromEvent(e) {
    if (!state.use3d) return false;
    if (e.button !== undefined && e.button !== 0) return false;
    return true;
  }

  function beginDrag(clientX, clientY, pointerId = null, source = 'pointer') {
    modelDrag = {
      pointerId,
      source,
      startX: clientX,
      startY: clientY,
      rotX: modelRotation.x,
      rotY: modelRotation.y,
      moved: false,
    };
    model3d?.classList.add('dragging');
    stage.classList.add('dragging-3d');
  }

  function moveDrag(clientX, clientY) {
    if (!modelDrag) return;
    const dx = clientX - modelDrag.startX;
    const dy = clientY - modelDrag.startY;
    if (Math.abs(dx) + Math.abs(dy) > 2) modelDrag.moved = true;
    setModelRotationFromDrag(modelDrag, clientX, clientY);
  }

  function finishDrag(pointerId = null, source = null) {
    if (!modelDrag) return;
    if (pointerId !== null && modelDrag.pointerId !== null && pointerId !== modelDrag.pointerId) return;
    if (source && modelDrag.source !== source) return;
    const shouldEmit = modelDrag.moved;
    modelDrag = null;
    model3d?.classList.remove('dragging');
    stage.classList.remove('dragging-3d');
    if (shouldEmit) window.motionEmitModelRotation();
  }

  // Pointer Events: пальцы/стилус/часть браузеров с мышью.
  stage.addEventListener('pointerdown', (e) => {
    if (!canStartFromEvent(e)) return;
    e.preventDefault();
    beginDrag(e.clientX, e.clientY, e.pointerId, 'pointer');
    try { stage.setPointerCapture(e.pointerId); } catch {}
  });

  stage.addEventListener('pointermove', (e) => {
    if (!modelDrag || modelDrag.source !== 'pointer' || e.pointerId !== modelDrag.pointerId) return;
    e.preventDefault();
    moveDrag(e.clientX, e.clientY);
  });

  function endPointerDrag(e) {
    if (!modelDrag || modelDrag.source !== 'pointer' || e.pointerId !== modelDrag.pointerId) return;
    try {
      if (stage.hasPointerCapture(e.pointerId)) stage.releasePointerCapture(e.pointerId);
    } catch {}
    finishDrag(e.pointerId, 'pointer');
  }

  stage.addEventListener('pointerup', endPointerDrag);
  stage.addEventListener('pointercancel', endPointerDrag);
  stage.addEventListener('lostpointercapture', () => finishDrag(null, 'pointer'));

  // Отдельный обязательный desktop-fallback: многие ноутбуки/браузеры отдают mouse-события,
  // даже когда Pointer Events есть. Поэтому не отключаем его через window.PointerEvent.
  stage.addEventListener('mousedown', (e) => {
    if (!canStartFromEvent(e)) return;
    e.preventDefault();
    beginDrag(e.clientX, e.clientY, 'mouse', 'mouse');
  });

  document.addEventListener('mousemove', (e) => {
    if (!modelDrag || modelDrag.source !== 'mouse') return;
    e.preventDefault();
    moveDrag(e.clientX, e.clientY);
  });

  document.addEventListener('mouseup', () => finishDrag('mouse', 'mouse'));
  model3d?.addEventListener('dragstart', (e) => e.preventDefault());
}

setupModelDrag();

let appInitialized = false;

window.motionApplyLoadedModel = function motionApplyLoadedModel() {
  applySelectedAnimation();
  if (state.playing) start({ silent: true });
};

window.motionGetLocalState = function motionGetLocalState() {
  return {
    selectedKey: state.selectedKey,
    speed: state.speed,
    use3d: state.use3d,
    combine: state.combine,
    playing: state.playing,
    loadedModel: state.loadedModel,
    animationCount: state.runningAnimations.length,
  };
};

window.motionInitApp = function motionInitApp() {
  if (appInitialized) return;
  appInitialized = true;
  renderAnimations();
  applySelectedAnimation();
  start({ silent: true });
};

window.motionStopApp = function motionStopApp() {
  stop();
  appInitialized = false;
};
