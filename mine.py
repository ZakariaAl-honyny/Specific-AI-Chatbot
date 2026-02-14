from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import sys
 
# حل مشكلة اللغة العربية في الـ Terminal
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

app = FastAPI()

# تحديد المسارات بناءً على المجلد الحالي
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ربط الملفات الثابتة والقوالب (index.html و style.css وغيرها في نفس المجلد)
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
templates = Jinja2Templates(directory=BASE_DIR)

# إعدادات Gemini (تأكد من صحة مفتاح الـ API الخاص بك)
GOOGLE_API_KEY = "AIzaSyCJo4ODRKPAPFNh_syw5gCCcyawRXD3rq8"
client = genai.Client(api_key=GOOGLE_API_KEY)

# برومبت خبير الـ UX Writing المحدث بناءً على طلبك
SYSTEM_PROMPT = """الهوية: أنت "المحلل الذكي"، خبير متخصص حصرياً في عالم كرة القدم والرياضة. تتميز بأسلوب مختصر، مباشر، ويعطي "لب الموضوع" دون إطالة.

قواعد التعامل مع المحتوى:

الترحيب: إذا بدأت المحادثة بسلام أو ترحيب (مثل: أهلاً، السلام عليكم، كيف حالك)، رد بلطف واحترام، ثم وجه المستخدم لسؤالك عن عالم الكرة.

التخصص والتركيز: تخصصك هو كرة القدم والرياضة فقط.

المراوغة الذكية: إذا سألك المستخدم سؤالاً خارج الرياضة (للمرة الأولى أو الثانية)، قم بـ "مراوغته" بذكاء عبر ربط الإجابة بمصطلح رياضي ثم أعِد توجيه الحوار للكرة. (مثال: إذا سألك عن الطبخ، قل: "أنا أجيد تحضير الخطط التكتيكية لا الوجبات، ما رأيك نعود لتحليل المباراة؟").

الحزم عند التكرار: إذا أصر المستخدم على الخروج عن النص الرياضي لأكثر من مرتين، قل له مباشرة: "عذراً، أنا متخصص في مجال الرياضة فقط."

الذاكرة والترابط: يجب عليك مراجعة سجل المحادثة (History) قبل كل رد. تأكد أن إجابتك الحالية تبني على ما سبق وتكمل سياق الأسئلة الماضية بدقة.

أسلوب الرد:

مختصر ومفيد (الخلاصة).

استخدام مصطلحات كروية رشيقة.

التركيز على الحقائق والأرقام والتحليل الفني."""

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # عرض صفحة البداية
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_handler(chat_req: ChatRequest):
    try:
        # تحويل السجل القادم من الجافاسكريبت إلى تنسيق يفهمه Gemini
        formatted_history = []
        for m in chat_req.history:
            # التأكد من تمييز الأدوار (user لرسائلك، و model لردود البوت)
            role = "user" if m['sender'] == 'user' else "model"
            formatted_history.append(
                types.Content(role=role, parts=[types.Part(text=m['text'])])
            )

        # إنشاء جلسة المحادثة مع السجل السابق
        chat = client.chats.create(
            model="gemini-2.5-flash", # تأكد من استخدام موديل متاح في مكتبتك
            history=formatted_history,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT, 
                temperature=0.7
            )
        )

        # إرسال الرسالة الحالية والحصول على الرد
        response = chat.send_message(chat_req.message)
        
        return JSONResponse(content={"response": response.text})

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"response": "حدث خطأ تقني يا مولاي، يرجى المحاولة لاحقاً."}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("--- Server is starting on http://127.0.0.1:8080 ---")
    uvicorn.run(app, host="127.0.0.1", port=8080)