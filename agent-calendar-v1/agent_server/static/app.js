const chat = document.querySelector("#chat");
const form = document.querySelector("#form");
const input = document.querySelector("#message");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  chat.textContent += `You: ${message}\n\n`;
  input.value = "";

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  const data = await response.json();
  chat.textContent += `Assistant: ${data.response || data.detail || "Request failed"}\n\n`;
});
