# UniCrypt

UniCrypt منصة تواصل جامعية تعليمية مبنية على FastAPI. تجمع بين تسجيل الدخول بالأدوار، محادثات خاصة فورية عبر WebSocket، رسائل صوتية مسجلة، ومعمل لتجربة Caesar وHill وVigenère وPlayfair وRail Fence وDES وAES-256-GCM.

## تشغيل محلي

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# للتشغيل عبر HTTP المحلي: COOKIE_SECURE=false
COOKIE_SECURE=false uvicorn app.main:app --reload --port 3000
```

افتح `http://localhost:3000`. ينشئ التشغيل الأول حسابين تجريبيين: `demo_student / Student@123` و`demo_professor / Professor@123`. غيّر `SECRET_KEY` قبل أي نشر.

## PostgreSQL وDocker

اضبط `DATABASE_URL` على DSN PostgreSQL ثم شغّل `docker compose up --build`. الملفات الصوتية في الإصدار الأول محلية؛ استخدم object storage دائمًا في بيئة متعددة النسخ.

## النشر

استخدم خدمة Python/Container تدعم WebSocket. اضبط `PORT` و`DATABASE_URL` و`SECRET_KEY` و`COOKIE_SECURE=true` ومرّر التطبيق خلف HTTPS. عند تفعيل HTTPS يصبح عنوان WebSocket تلقائيًا `wss://`. مسار الفحص هو `/health`.

## الأمن والنطاق

كلمات المرور تستخدم Argon2id. الرسائل النصية والملفات الصوتية تُشفّر AES-GCM مع nonce فريد وtag للتحقق من السلامة، ولا تُحفظ كلمات المرور أو المفاتيح الخاصة صراحة في جداول الرسائل. Secure Chat في هذا المشروع نموذج تعليمي؛ لا يُسمى E2EE كاملًا لأن مفتاح الجلسة تحت إدارة الخادم. الخوارزميات الكلاسيكية وDES موجودة للتجربة والمقارنة فقط.

## الاختبارات

```bash
COOKIE_SECURE=false pytest -q
python3 -m compileall app
```
