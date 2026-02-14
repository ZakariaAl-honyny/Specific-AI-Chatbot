let chatHistory = []; // [تحديث] لتخزين سجل المحادثة وإرساله للخادم

async function sendMessage() {
    const input = document.getElementById('userInput');
    const windowChat = document.getElementById('chatWindow');
    const loader = document.getElementById('loader');
    const userText = input.value.trim();

    if (userText === "") return;

    // 1. إضافة رسالة المستخدم للواجهة
    appendMessage('user', userText);
    input.value = "";
    
    // 2. إظهار اللودر
    loader.style.display = "flex";
    windowChat.scrollTop = windowChat.scrollHeight;

    try {
        // 3. إرسال الطلب للخادم (FastAPI) مع السجل (chatHistory)
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userText,
                history: chatHistory // [تحديث] إرسال السجل الكامل للبوت
            })
        });

        const data = await response.json();
        
        // 4. إضافة رد البوت للواجهة
        loader.style.display = "none";
        appendMessage('bot', data.response);
        
        // [تحديث] حفظ الرسائل في السجل لضمان تذكر البوت للمحادثة
        chatHistory.push({ sender: 'user', text: userText });
        chatHistory.push({ sender: 'bot', text: data.response });

    } catch (error) {
        loader.style.display = "none";
        appendMessage('bot', "عذراً يا مولاي، يبدو أن هناك عطلاً في الاتصال بالخادم.");
    }
}

// [إضافة] وظيفة لبدء محادثة جديدة وتصفير السجل
function createNewChat() {
    const windowChat = document.getElementById('chatWindow');
    windowChat.innerHTML = ""; // مسح الواجهة
    chatHistory = []; // تصفير الذاكرة
    appendMessage('bot', "أهلاً بك يا مولاي! أنا مستشارك الخاص في UX Writing. كيف يمكنني خدمتك؟");
    
    // إضافة عنصر جديد في قائمة السجلات الجانبية
    const historyList = document.getElementById('historyList');
    if (historyList) {
        const item = document.createElement('div');
        item.className = 'h-card active';
        item.textContent = `محادثة جديدة ${new Date().toLocaleTimeString('ar-EG')}`;
        historyList.prepend(item);
    }
}

function appendMessage(role, text) {
    const windowChat = document.getElementById('chatWindow');
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg-bubble ${role}`;
    msgDiv.textContent = text;
    windowChat.appendChild(msgDiv);
    windowChat.scrollTop = windowChat.scrollHeight;
}

function handleKeyPress(e) { if (e.key === 'Enter') sendMessage(); }

// تأثير تفاعل الماوس
document.addEventListener('mousemove', (e) => {
    const glow = document.querySelector('.ambient-glow');
    if(glow) {
        glow.style.left = (e.pageX - 300) + 'px';
        glow.style.top = (e.pageY - 300) + 'px';
    }
});