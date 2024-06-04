window.watsonAssistantChatOptions = {
    integrationID: "fc782640-6d4f-442e-9cdf-b79a99a72ca6",
    region: "eu-gb",
    serviceInstanceID: "d6d2737e-ab10-4938-8138-2ca6fdc53c13",
    onLoad: async (instance) => { await instance.render(); }
};
setTimeout(function () {
    const t = document.createElement('script');
    t.src = "https://web-chat.global.assistant.watson.appdomain.cloud/versions/" + (window.watsonAssistantChatOptions.clientVersion || 'latest') + "/WatsonAssistantChatEntry.js";
    document.head.appendChild(t);
});

function initializeChat() {
    const unifyKey = document.getElementById('unifyKeyInput').value;
    const model = document.getElementById('modelSelector').value;
    console.log(`Unify Key: ${unifyKey}, Model: ${model}`);
    // Additional initialization code can be added here
}

function sendMessage() {
    const message = document.getElementById('chatInput').value;
    console.log(`Message sent: ${message}`);
    // Implement sending message to backend here
}

// Populate the model selector
document.addEventListener('DOMContentLoaded', function () {
    const models = [
        "mixtral-8x7b-instruct-v0.1", "llama-2-70b-chat", /* more models */
    ];
    const modelSelector = document.getElementById('modelSelector');
    models.forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelSelector.appendChild(option);
    });
});
