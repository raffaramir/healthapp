// HEALTHAPP — UI behaviors
(function () {
  'use strict';

  // ── Theme toggle (persisted) — light is default; dark is opt-in
  const STORAGE_KEY = 'healthapp-theme';
  const root = document.documentElement;
  const stored = localStorage.getItem(STORAGE_KEY) || 'light';
  if (stored === 'dark') root.setAttribute('data-theme', 'dark');

  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-action="toggle-theme"]')) {
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      if (next === 'dark') root.setAttribute('data-theme', 'dark');
      else root.removeAttribute('data-theme');
      localStorage.setItem(STORAGE_KEY, next);
    }
    if (e.target.closest('[data-action="toggle-sidebar"]')) {
      document.querySelector('.sidebar')?.classList.toggle('open');
    }
    if (e.target.closest('[data-action="toggle-notifs"]')) {
      e.preventDefault();
      document.querySelector('#notif-dropdown')?.classList.toggle('open');
    }
    if (!e.target.closest('#notif-dropdown') && !e.target.closest('[data-action="toggle-notifs"]')) {
      document.querySelector('#notif-dropdown')?.classList.remove('open');
    }
  });

  // ── Auto-fade messages
  document.querySelectorAll('.alert.dismissible').forEach((el) => {
    setTimeout(() => {
      el.style.transition = 'opacity .4s, transform .4s';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-8px)';
      setTimeout(() => el.remove(), 400);
    }, 5000);
  });

  // ── Stagger fade-in animation on cards
  document.querySelectorAll('[data-stagger] > *').forEach((el, i) => {
    el.classList.add('fade-up');
    el.style.animationDelay = `${Math.min(i * 0.05, 0.5)}s`;
  });

  // ── Notification poll (every 30s)
  if (document.body.dataset.authenticated === 'true') {
    const badge = document.querySelector('#notif-badge');
    const poll = async () => {
      try {
        const res = await fetch('/notifications/api/unread-count/');
        if (!res.ok) return;
        const data = await res.json();
        if (badge) {
          badge.textContent = data.unread;
          badge.style.display = data.unread > 0 ? 'grid' : 'none';
        }
      } catch (_) {}
    };
    poll();
    setInterval(poll, 30000);
  }

  // ── Chat scroll to bottom on load + WebSocket
  const chatMsgs = document.querySelector('#chat-msgs');
  if (chatMsgs) {
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
    const convId = chatMsgs.dataset.conversationId;
    const userId = chatMsgs.dataset.userId;
    if (convId && 'WebSocket' in window) {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      const ws = new WebSocket(`${proto}://${location.host}/ws/chat/${convId}/`);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type !== 'message') return;
        const bubble = document.createElement('div');
        const isSelf = String(data.sender_id) === String(userId);
        bubble.className = `chat-bubble ${isSelf ? 'self' : 'other'}`;
        bubble.innerHTML = `${escapeHtml(data.body)}<span class="ts">${formatTime(data.created_at)}</span>`;
        chatMsgs.appendChild(bubble);
        chatMsgs.scrollTop = chatMsgs.scrollHeight;
      };
      const form = document.querySelector('#chat-form');
      const input = document.querySelector('#chat-input');
      if (form && input) {
        form.addEventListener('submit', (e) => {
          if (input.value.trim() && ws.readyState === WebSocket.OPEN) {
            // Prefer WebSocket; fallback POST handles it server-side
            e.preventDefault();
            ws.send(JSON.stringify({ body: input.value }));
            input.value = '';
          }
        });
      }
    }
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }
  function formatTime(iso) {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
})();
