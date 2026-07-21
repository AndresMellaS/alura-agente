const form = document.getElementById("chat-form");
const input = document.getElementById("pregunta");
const messages = document.getElementById("messages");

function addMessage(text, sender, fuentes) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${sender}`;

  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;

  if (fuentes && fuentes.length > 0) {
    const fuentesEl = document.createElement("span");
    fuentesEl.className = "fuentes";
    fuentesEl.textContent = `Fuentes: ${fuentes.join(", ")}`;
    bubble.appendChild(fuentesEl);
  }

  wrapper.appendChild(bubble);
  messages.appendChild(wrapper);
  messages.scrollTop = messages.scrollHeight;
  return wrapper;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const pregunta = input.value.trim();
  if (!pregunta) return;

  addMessage(pregunta, "user");
  input.value = "";
  input.disabled = true;
  form.querySelector("button").disabled = true;

  const typingEl = addMessage("Pensando...", "bot");
  typingEl.querySelector(".bubble").classList.add("typing");

  try {
    const res = await fetch("/preguntar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pregunta }),
    });

    typingEl.remove();

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      addMessage(
        `Ocurrió un error: ${err.detail || "no se pudo procesar la pregunta."}`,
        "bot"
      );
      return;
    }

    const data = await res.json();
    addMessage(data.respuesta, "bot", data.fuentes);
  } catch (err) {
    typingEl.remove();
    addMessage("No se pudo conectar con el servidor. Probá de nuevo.", "bot");
  } finally {
    input.disabled = false;
    form.querySelector("button").disabled = false;
    input.focus();
  }
});
