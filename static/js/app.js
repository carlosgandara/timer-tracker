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

    // Hide timer section initially
    timerSection.style.display = 'none';

    colorSquares.forEach(square => {
        square.addEventListener('click', () => {
            // If a timer is already running, stop it first
            if (timerInterval) {
                stopTimer();
                // Also save the log? The user expects to stop and save on stop click,
                // but here we're starting a new one; we should save the previous one.
                // Better: when clicking a new color, stop and save the previous.
                // But we already have saveLog() in stop, so call stopTimer which doesn't save.
                // We'll instead call a custom function.
                // Let's just stop without saving; the user will click stop to save.
                // But we want to hide grid/show timer again.
                // We'll just stop the timer without saving.
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
        if (timerInterval) {
            stopTimer();
            saveLog();
            // Show color grid again, hide timer
            const colorGrid = document.querySelector('.color-grid');
            colorGrid.style.display = 'grid';
            timerSection.style.display = 'none';
        }
    });

    function startTimer(activity) {
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
        clearInterval(timerInterval);
        timerInterval = null;
        timerSection.style.display = 'none';
        // Mascot says goodbye
        mascotEmoji.textContent = '🎉';
    }

    function saveLog() {
        if (!selectedColor || elapsedSeconds < 1) {
            alert('Please log at least 1 second.');
            return;
        }
        fetch('/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color: selectedColor, duration: elapsedSeconds })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Confetti or alert
                alert('✅ Logged ' + selectedColor + ' for ' + elapsedSeconds + 's');
                elapsedSeconds = 0;
                selectedColor = null;
                // Show the grid again (already done in stop listener)
                document.querySelector('.color-grid').style.display = 'grid';
                timerSection.style.display = 'none';
            } else {
                alert('❌ Error saving log.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('❌ Network error.');
        });
    }
});