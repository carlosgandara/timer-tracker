let timerInterval = null;
let startTime = null;
let elapsedSeconds = 0;
let selectedColor = null;

document.addEventListener('DOMContentLoaded', () => {
    const colorSquares = document.querySelectorAll('.color-square');
    const colorGrid = document.querySelector('.color-grid');
    const timerSection = document.getElementById('timer-section');
    const timerBar = document.getElementById('timer-bar');
    const timerProgressFill = document.getElementById('timer-progress-fill');
    const currentActivity = document.getElementById('current-activity');
    const stopBtn = document.getElementById('stop-btn');
    const mascotEmoji = document.getElementById('mascot-emoji');

    console.log('✅ Timer app loaded');

    // Hide timer section initially
    timerSection.style.display = 'none';

    colorSquares.forEach(square => {
        square.addEventListener('click', () => {
            console.log('🟦 Color clicked:', square.dataset.color);
            // If a timer is already running, stop it first
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
                timerSection.style.display = 'none';
                colorGrid.style.display = 'grid';
            }
            selectedColor = square.dataset.color;
            const activity = square.querySelector('.color-label').textContent;
            startTimer(activity);
            // Hide color grid, show timer
            colorGrid.style.display = 'none';
            timerSection.style.display = 'block';
        });
    });

    stopBtn.addEventListener('click', () => {
        console.log('⏹ Stop button clicked');
        if (timerInterval) {
            stopTimer();
            saveLog();
            const colorGrid = document.querySelector('.color-grid');
            colorGrid.style.display = 'grid';
            timerSection.style.display = 'none';
        }
    });

    function startTimer(activity) {
        console.log('⏱️ Starting timer for:', activity);
        timerSection.style.display = 'block';
        currentActivity.textContent = '⏱️ ' + activity;
        timerBar.textContent = '0s';
        timerProgressFill.style.width = '0%';
        startTime = Date.now();
        elapsedSeconds = 0;

        // Update mascot
        mascotEmoji.textContent = '🚀';

        timerInterval = setInterval(() => {
            elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
            timerBar.textContent = elapsedSeconds + 's';
            const progress = Math.min((elapsedSeconds % 60) / 60 * 100, 100);
            timerProgressFill.style.width = progress + '%';
        }, 200);
    }

    function stopTimer() {
        console.log('⏹ Stopping timer, elapsed:', elapsedSeconds);
        clearInterval(timerInterval);
        timerInterval = null;
        timerSection.style.display = 'none';
        // Mascot says goodbye
        mascotEmoji.textContent = '🎉';
    }

    function saveLog() {
        console.log('💾 saveLog() called');
        console.log('selectedColor:', selectedColor);
        console.log('elapsedSeconds:', elapsedSeconds);

        if (!selectedColor || elapsedSeconds < 1) {
            alert('Please log at least 1 second.');
            return;
        }

        const payload = { color: selectedColor, duration: elapsedSeconds };
        console.log('📤 Sending:', payload);

        fetch('/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => {
            console.log('📡 Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📦 Response data:', data);
            if (data.success) {
                alert('✅ Logged ' + selectedColor + ' for ' + elapsedSeconds + 's');
                elapsedSeconds = 0;
                selectedColor = null;
                document.querySelector('.color-grid').style.display = 'grid';
                timerSection.style.display = 'none';
            } else {
                alert('❌ Error saving log.');
            }
        })
        .catch(error => {
            console.error('❌ Network error:', error);
            alert('❌ Network error.');
        });
    }
});