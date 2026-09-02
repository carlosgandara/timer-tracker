let timerInterval = null;
let startTime = null;
let elapsedSeconds = 0;
let selectedColor = null;

document.addEventListener('DOMContentLoaded', () => {
    const colorSquares = document.querySelectorAll('.color-square');
    const timerSection = document.getElementById('timer-section');
    const timerBar = document.getElementById('timer-bar');
    const timerProgressFill = document.getElementById('timer-progress-fill');
    const currentActivity = document.getElementById('current-activity');
    const stopBtn = document.getElementById('stop-btn');

    colorSquares.forEach(square => {
        square.addEventListener('click', () => {
            if (timerInterval) stopTimer();
            selectedColor = square.dataset.color;
            const activity = square.querySelector('.color-label').textContent;
            startTimer(activity);
        });
    });

    stopBtn.addEventListener('click', () => {
        if (timerInterval) {
            stopTimer();
            saveLog();
        }
    });

    function startTimer(activity) {
        timerSection.style.display = 'block';
        currentActivity.textContent = '⏱️ ' + activity;
        timerBar.textContent = '0s';
        timerProgressFill.style.width = '0%';
        startTime = Date.now();
        elapsedSeconds = 0;

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
                alert('✅ Logged ' + selectedColor + ' for ' + elapsedSeconds + 's');
                elapsedSeconds = 0;
                selectedColor = null;
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
