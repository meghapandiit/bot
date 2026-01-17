const API_URL = "http://127.0.0.1:8000/chat/"; 

let sessionId = localStorage.getItem("hm_session");
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem("hm_session", sessionId);
}

const messagesDiv = document.getElementById("messages");
const input = document.getElementById("input");
const inputBox = document.getElementById("inputBox");

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.innerText = text;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: text
    })
  });

  const data = await res.json();

  addMessage(data.reply, "bot");

  // 🔴 Crisis: lock input
  if (data.show_pay === false && data.show_booking === true) {
    inputBox.innerHTML = `
      <div class="cta">
        <a href="${data.booking_url}" target="_blank">
          👉 Book support with Humming Minds
        </a>
      </div>
    `;
    return;
  }

  // 🟠 Closure CTA
  if (data.show_booking) {
    const cta = document.createElement("div");
    cta.className = "cta";
    cta.innerHTML = `
      <a href="${data.booking_url}" target="_blank">
        👉 Book therapy session
      </a>
      <br><br>
      <button onclick="startPayment()">Continue chat (₹30 / 30 min)</button>
    `;
    messagesDiv.appendChild(cta);
  }
}

function startPayment() {
  window.location.href = "https://YOUR_PAYMENT_LINK";
}
