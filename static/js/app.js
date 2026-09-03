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
    timerSection.style.display = 'none';

    // ✅ CHECK FOR ACTIVE TIMER ON PAGE LOAD
    fetch('/active-timer')
        .then(res => res.json())
        .then(data => {
            if (data.active) {
                console.log('⏱️ Active timer found:', data);
                selectedColor = data.color;
                const activity = data.activity;
                startTimer(activity, data.elapsed_seconds);
                colorGrid.style.display = 'none';
                timerSection.style.display = 'block';
            }
        })
        .catch(err => console.error('Error checking active timer:', err));

    // Color click handler
    colorSquares.forEach(square => {
        square.addEventListener('click', () => {
            console.log('🟦 Color clicked:', square.dataset.color);
            
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
                timerSection.style.display = 'none';
                colorGrid.style.display = 'grid';
            }
            
            selectedColor = square.dataset.color;
            const activity = square.querySelector('.color-label').textContent;
            
            // ✅ Start the timer on the server
            fetch('/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ color: selectedColor })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ Timer started on server at:', data.start_time);
                    startTimer(activity, 0);
                    colorGrid.style.display = 'none';
                    timerSection.style.display = 'block';
                }
            })
            .catch(err => console.error('Error starting timer:', err));
        });
    });

    // Stop button handler
    stopBtn.addEventListener('click', () => {
        console.log('⏹ Stop button clicked');
        if (timerInterval) {
            stopTimer();
            saveLog();
        }
    });

    function startTimer(activity, offset = 0) {
        console.log('⏱️ Starting timer for:', activity, 'offset:', offset);
        timerSection.style.display = 'block';
        currentActivity.textContent = '⏱️ ' + activity;
        timerBar.textContent = Math.floor(offset) + 's';
        timerProgressFill.style.width = '0%';
        startTime = Date.now() - (offset * 1000);
        elapsedSeconds = offset;
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
        console.log('📤 Sending stop request:', payload);

        // ✅ Stop the timer on the server
        fetch('/stop', {
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