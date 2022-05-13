const reportEmail = "frank.ortegaca@anahuac.mx";

// Función después de la carga
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("overlay").style.display = "none";
  const chatContainer = document.getElementById("chatContainer");
  const messageForm = document.getElementById("messageForm");

  // Se ajusta el tamaño de la pantalla principal

  // Evento de mandar mensaje
  messageForm.addEventListener("submit", (e) => {
    const message = messageForm.querySelector("textarea").value;
    messageForm.querySelector("textarea").value = "";
    chatContainer.innerHTML += `<p class="left-bubble">${message}</p>`;

    fetch(`${window.origin}/api/bot`, {
      method: "POST",
      cache: "no-cache",
      body: JSON.stringify({ message: message }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (Array.isArray(data))
          for (const answer of data)
            chatContainer.innerHTML += `<p class="right-bubble">${answer}</p>`;
        else chatContainer.innerHTML += `<p class="right-bubble">${data}</p>`;
      });
    e.preventDefault();
  });
});
