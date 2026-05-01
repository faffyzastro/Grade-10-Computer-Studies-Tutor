// ─── REPLACE YOUR sendMessage() function with this ────────────────────────
// This uses fetch() with ReadableStream to consume SSE tokens in real-time.
// Drop this entire block into your index.html <script> section.

async function sendMessage() {
  if (isLoading) return;

  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query) return;

  input.value = '';
  input.style.height = 'auto';
  isLoading = true;
  document.getElementById('send-btn').disabled = true;

  // Show the user's message
  addMessage('user', query);

  // Create an empty assistant bubble that we'll fill token by token
  const { bubbleEl, metaEl } = addStreamingBubble();

  let fullText   = '';
  let finalMode  = currentMode;
  let finalSources = [];

  try {
    const response = await fetch('/ask/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query:   query,
        mode:    currentMode,
        subject: currentSubject,   // your subject variable (cs / chem / bio)
      }),
    });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    // Read the SSE stream as it arrives
    const reader  = response.body.getReader();
    const decoder = new TextDecoder();
    let   buffer  = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // SSE events are separated by double newlines
      const events = buffer.split('\n\n');
      buffer = events.pop(); // keep the incomplete last chunk

      for (const event of events) {
        const line = event.trim();
        if (!line.startsWith('data: ')) continue;

        let chunk;
        try {
          chunk = JSON.parse(line.slice(6)); // strip "data: "
        } catch {
          continue;
        }

        if (chunk.error) {
          // Show error inside the bubble
          bubbleEl.innerHTML = `<span style="color:#c0392b">⚠️ ${chunk.error}</span>`;
          break;
        }

        if (!chunk.done) {
          // Append the token and re-render markdown
          fullText += chunk.token;
          bubbleEl.innerHTML = formatMessage(fullText);
          scrollToBottom();
        } else {
          // Final frame — update mode badge and sources
          finalMode    = chunk.mode    || finalMode;
          finalSources = chunk.sources || [];
          updateModeBadge(finalMode, metaEl);
        }
      }
    }

  } catch (err) {
    bubbleEl.innerHTML = `
      <span style="color:#c0392b">
        ⚠️ Could not reach the server.<br>
        <code style="font-size:12px">uvicorn server:app --host 0.0.0.0 --port 8000</code><br><br>
        Error: ${err.message}
      </span>`;
  }

  isLoading = false;
  document.getElementById('send-btn').disabled = false;
  document.getElementById('chat-input').focus();
}


// ─── HELPER: Creates an empty streaming bubble ─────────────────────────────
function addStreamingBubble() {
  hideWelcome();
  const msgs = document.getElementById('messages');

  const msgDiv = document.createElement('div');
  msgDiv.className = 'msg assistant';

  const avatar = document.createElement('div');
  avatar.className = 'msg-avatar';
  avatar.textContent = '🤖';

  const col = document.createElement('div');

  const bubble = document.createElement('div');
  bubble.className = 'msg-bubble';
  // Blinking cursor shown while streaming
  bubble.innerHTML = '<span class="typing-cursor">▋</span>';

  const metaDiv = document.createElement('div');
  metaDiv.className = 'msg-meta';

  col.appendChild(bubble);
  col.appendChild(metaDiv);
  msgDiv.appendChild(avatar);
  msgDiv.appendChild(col);
  msgs.appendChild(msgDiv);
  scrollToBottom();

  return { bubbleEl: bubble, metaEl: metaDiv };
}


// ─── HELPER: Update the mode badge after stream completes ─────────────────
function updateModeBadge(mode, metaEl) {
  const badge = document.createElement('span');
  badge.className = `meta-badge badge-${mode || 'chitchat'}`;
  badge.textContent = (mode || 'auto').toUpperCase();
  metaEl.innerHTML = '';
  metaEl.appendChild(badge);

  // Also update the header badge
  const hb = document.getElementById('current-mode-badge');
  if (hb) {
    hb.className = `mode-badge badge-${mode || 'chitchat'}`;
    hb.textContent = (mode || 'auto').toUpperCase();
  }
}

/* ── Add this CSS to your <style> block ──────────────────────────────────── */
/*
.typing-cursor {
  display: inline-block;
  width: 2px;
  background: currentColor;
  animation: blink 0.8s step-end infinite;
  margin-left: 1px;
  font-size: 1em;
  vertical-align: text-bottom;
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}
*/
