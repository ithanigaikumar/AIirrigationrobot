// Flags to track if audio is ready
let moistureAudioReady = false;
let sunlightAudioReady = false;

// Queue to handle sequential audio playback
let audioQueue = [];
let isPlaying = false;

function checkPlantRaw() {
    fetch("https://irrigation.ajanthank.com/devices/0/status")
        .then(response => response.json())
        .then(data => {
            var moistureStat= data.moisture.raw;
            var tempStat = data.temperature.raw;
            console.log(moistureStat);
            console.log(tempStat);
            document.getElementById("temp").innerHTML = tempStat;
            document.getElementById("moisture").innerHTML = moistureStat;
        })
    
}

function checkPlantStatus() {
    fetch("https://irrigation.ajanthank.com/devices/0/status")
        .then(response => response.json())
        .then(data => {
            const moistureStatus = data.moisture.status;
            const sunlightStatus = data.light.status;

            // Clear any existing audioQueue to avoid duplications
            audioQueue = [];
            isPlaying = false;

            if (moistureStatus === -1) {
                queueAudio('moistureAudio');
            } else {
                moistureAudioReady = true;
            }

            if (sunlightStatus === -1) {
                queueAudio('sunlightAudio');
            } else {
                sunlightAudioReady = true;
            }

            playAudioIfReady();
            checkPlantRaw();
        })
        .catch(error => console.error('Error:', error));
}

function queueAudio(audioId) {
    audioQueue.push(audioId);
}

function playAudio(audioId, callback) {
    const audioElement = document.getElementById(audioId);
    audioElement.onended = () => {
        callback();
    };
    audioElement.play().catch(error => {
        console.error(`Error playing ${audioId}:`, error);
        callback();  // Ensure callback is called even if there is an error
    });
}

function playAudioIfReady() {
    if (!isPlaying && audioQueue.length > 0) {
        isPlaying = true;
        const nextAudio = audioQueue.shift();
        playAudio(nextAudio, () => {
            isPlaying = false;
            playAudioIfReady();
        });
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

    // Attach event listener to the button to ensure user interaction before playing audio
    document.querySelector('.btn-success').addEventListener('click', checkPlantStatus);
});

// Ensure the function is globally available
window.checkPlantStatus = checkPlantStatus;
