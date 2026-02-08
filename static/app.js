document.addEventListener('DOMContentLoaded', () => {
    // --- Tab Switching ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');

            // Update nav
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');

            // Update content
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${targetTab}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });

    // --- Loading Control ---
    const loadingOverlay = document.getElementById('loading-overlay');
    const showLoading = () => loadingOverlay.classList.remove('hidden');
    const hideLoading = () => loadingOverlay.classList.add('hidden');

    // --- Storyboard Logic ---
    const generateBtn = document.getElementById('generate-btn');
    const storyInput = document.getElementById('story-input');
    const resultsGrid = document.getElementById('storyboard-results');

    generateBtn.addEventListener('click', async () => {
        const text = storyInput.value.trim();
        if (!text) {
            alert('请输入剧本内容！');
            return;
        }

        showLoading();
        try {
            const response = await fetch('/api/storyboard', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_input: text })
            });

            if (!response.ok) throw new Error('生成失败');
            const data = await response.json();
            renderStoryboard(data);
        } catch (error) {
            console.error(error);
            alert('发生错误：' + error.message);
        } finally {
            hideLoading();
        }
    });

    function renderStoryboard(data) {
        resultsGrid.innerHTML = ''; // Clear previous

        const titleEl = document.createElement('h3');
        titleEl.style.marginBottom = '20px';
        titleEl.textContent = `项目：${data.title}`;
        resultsGrid.appendChild(titleEl);

        data.shots.forEach(shot => {
            const card = document.createElement('div');
            card.className = 'shot-card';
            card.innerHTML = `
                <div class="shot-number">${shot.shot_number}</div>
                <div class="shot-info">
                    <div class="shot-header">
                        <span class="shot-type">${shot.shot_type}</span>
                    </div>
                    <div class="shot-content"><strong>画面：</strong>${shot.content}</div>
                    <div class="shot-audio"><strong>声音/旁白：</strong>${shot.audio}</div>
                </div>
            `;
            resultsGrid.appendChild(card);
        });
    }

    // --- Chat Logic ---
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    const addMessage = (text, role) => {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        msgDiv.textContent = text;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    sendBtn.addEventListener('click', async () => {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        chatInput.value = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) throw new Error('助手回复失败');
            const data = await response.json();
            addMessage(data.answer, 'assistant');
        } catch (error) {
            addMessage('抱歉，发生了错误。', 'assistant');
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendBtn.click();
    });
});
