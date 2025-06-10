let messagesContainer;

document.addEventListener("DOMContentLoaded", () => {
  messagesContainer = document.getElementById("messages");
  const form = document.getElementById("messageForm");
  const textarea = document.getElementById("message");

  const API_URL = "/api/messages"; // Adjust to your actual messages endpoint
  let lastMessageId = null;
  const POLLING_INTERVAL = 2000; // Poll every 2 seconds

  // Fetch and display new messages
  async function loadMessages(initialLoad = false) {
    try {
      // If initial load, get all messages; otherwise, get messages since lastMessageId
      const endpoint = initialLoad
        ? API_URL
        : `${API_URL}?since=${lastMessageId}`;
      const response = await fetch(endpoint);
      if (!response.ok)
        throw new Error(`Error fetching messages: ${response.status}`);
      const data = await response.json();
      const messages = data.messages;

      if (initialLoad) {
        messagesContainer.innerHTML = "";
      }

      if (messages && messages.length > 0) {
        messages.forEach((msg) => {
          // Only append if the message doesn't already exist in the chat
          if (!document.getElementById(`message-${msg.id}`)) {
            appendMessageToChat(msg);
          }
        });

        // Update the lastMessageId to the most recent message
        lastMessageId = messages[messages.length - 1].id;
      }
    } catch (err) {
      console.error(err);
      // Optionally show a notification in the UI
    }
  }

  // Initial load of all messages
  loadMessages(true);

  // Set up periodic polling for new messages
  setInterval(() => loadMessages(false), POLLING_INTERVAL);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const messageText = textarea.value.trim();
    if (!messageText) {
      textarea.classList.add("is-invalid");
      return;
    }
    textarea.classList.remove("is-invalid");

    const payload = {
      content: messageText,
      author: USERNAME,
      language: LANGUAGE,
    };

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const newMsg = await response.json();
      //appendMessageToChat(newMsg);
      textarea.value = "";

      // Update lastMessageId after sending a new message
      if (newMsg.id) {
        lastMessageId = newMsg.id;
      }
    } catch (err) {
      console.error("Error sending message:", err);
      // Optionally show an error notification
    }
  });
});

/**
 * Appends a message card to the messages container.
 * @param {Object} data - The message data.
 * @param {number} data.id - Message ID.
 * @param {string} data.author - Sender's name.
 * @param {string} data.content - Message text.
 * @param {string} data.timestamp - ISO timestamp.
 */
async function appendMessageToChat(data) {
  const container = document.createElement("div");
  container.className = "card message-card mb-3";
  if (data.id) container.id = `message-${data.id}`;

  const body = document.createElement("div");
  body.className = "card-body";

  const title = document.createElement("h5");
  title.className = "card-title";
  const nameSpan = document.createElement("span");
  nameSpan.className = "et-name";
  nameSpan.textContent = data.author;
  title.appendChild(nameSpan);

  const textP = document.createElement("p");
  textP.className = "card-text";
  const msgSpan = document.createElement("span");
  msgSpan.className = "et-message";
  if (LANGUAGE === data.language) {
    msgSpan.textContent = data.content;
  }
  else {
    msgSpan.textContent = await translateMessage(data.id, LANGUAGE);
  }
  // msgSpan.textContent = data.content;
  textP.appendChild(msgSpan);

  const timeP = document.createElement("p");
  const timeSpan = document.createElement("span");
  timeSpan.className = "et-timestamp";
  timeSpan.textContent = data.timestamp
    ? new Date(data.timestamp).toLocaleString()
    : "";
  timeP.appendChild(timeSpan);

  body.append(title, textP, timeP);
  container.appendChild(body);

  messagesContainer.appendChild(container);
}


/**
 * Translates a message by its ID via API and returns the translated text.
 * @param {Object} originalMessage - The original message object.
 * @param {number} originalMessage.id - ID of the message to translate.
 * @param {string} targetLanguage - The language to translate to (e.g. 'English', 'German').
 * @returns {Promise<string>} - Translated text.
 */
async function translateMessage(originalMessageID, targetLanguage) {
  // if (!originalMessage || !originalMessage.id) {
  //   throw new Error('Invalid message object: missing id');
  // }
  const url = `/api/messages/translate/${originalMessageID}/${encodeURIComponent(targetLanguage)}`;
  console.log(url);
  const response = await fetch(url, { method: 'POST' });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `Translation request failed: ${response.status}`);
  }
  const data = await response.json();
  return data.translated_text;
}