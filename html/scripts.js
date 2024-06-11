// Flags to track if audio is ready
let moistureAudioReady = false;
let sunlightAudioReady = false;

function checkPlantStatus() {
    fetch("https://irrigation.ajanthank.com/devices/0/status")
        .then(response => response.json())
        .then(data => {
            const moistureStatus = data.moisture.status;
            const sunlightStatus = data.light.status;

            if (moistureStatus === -1) {
                synthesizeAndPrepare('moistureAudio', 'Your plant has dropped below moisture levels and is too dry, please water it!', () => {
                    moistureAudioReady = true;
                    playAudioIfReady();
                });
            } else {
                moistureAudioReady = true;
                playAudioIfReady();
            }

            if (sunlightStatus === -1) {
                synthesizeAndPrepare('sunlightAudio', 'Your plant has not absorbed enough sunlight for today please move it into the sunlight!', () => {
                    sunlightAudioReady = true;
                    playAudioIfReady();
                });
            } else {
                sunlightAudioReady = true;
                playAudioIfReady();
            }
        })
        .catch(error => console.error('Error:', error));
}

function synthesizeAndPrepare(audioId, message, callback) {
    console.log(`Synthesizing and preparing audio: ${audioId}, message: ${message}`);
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.onend = () => {
        callback();
    };
    speechSynthesis.speak(utterance);
}

function playAudioIfReady() {
    if (moistureAudioReady && sunlightAudioReady) {
        console.log("Both audio messages are ready to play.");
        // Additional logic to handle simultaneous audio playback if needed
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const leavesContainer = document.getElementById('leaves-container');
    const numberOfLeaves = 20; // Adjust the number of leaves as needed

    for (let i = 0; i < numberOfLeaves; i++) {
        const leaf = document.createElement('div');
        leaf.className = 'leaf';
        leaf.style.left = `${Math.random() * 100}vw`; // Random horizontal position
        leaf.style.animationDuration = `${Math.random() * 5 + 5}s`; // Random fall duration
        leaf.style.opacity = `${Math.random()}`; // Random opacity
        leavesContainer.appendChild(leaf);
    }
});

// Test the function
checkPlantStatus();
