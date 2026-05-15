from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

app = FastAPI(title="مسار - Masar AI Platform")

# --- النماذج (Models) ---
class User(BaseModel):
    id: int
    name: str
    role: str # "Faculty" or "Student"
    specialization: str
    faculty_id: Optional[int] = None # لربط الطالب بعضو هيئة التدريس

class Course(BaseModel):
    id: int
    title: str
    code: str
    specialization: str
    syllabus_attached: bool = False

class GradeRecord(BaseModel):
    student_id: int
    course_code: str
    grade: float
    faculty_id: int

class QuizAnswers(BaseModel):
    student_id: int
    test_number: int # 1, 2, or 3
    answers: Dict[str, str] # {"q1": "a", "q2": "c"...}

# --- قواعد البيانات الوهمية ---
db_users = [
    User(id=1, name="د. أحمد (شبكات)", role="Faculty", specialization="هندسة حاسب"),
    User(id=2, name="د. سارة (بحوث)", role="Faculty", specialization="علوم حاسب"),
    # ربطنا الطلاب بأعضاء التدريس (5 لكل عضو كحد أقصى نظرياً)
    User(id=101, name="سفيان الخلفي", role="Student", specialization="علوم حاسب", faculty_id=2),
    User(id=102, name="لينا القحطاني", role="Student", specialization="هندسة حاسب", faculty_id=1),
]

db_courses = [
    Course(id=1, title="شبكات الحاسب", code="CS301", specialization="هندسة حاسب"),
    Course(id=2, title="بحوث العمليات", code="CS302", specialization="علوم حاسب")
]

db_grades = []
db_student_progress = {101: {"tests_completed": 0, "skills": []}, 102: {"tests_completed": 0, "skills": []}}

# --- الأسئلة المستخرجة من المراجع ---
QUIZ_BANK = {
    "Networks": [
        {"id": "n1", "q": "ما هي وظيفة الـ Forwarding في الشبكات؟", "options": {"a": "تحديد المسار (Routing)", "b": "نقل الحزم من مدخل الموجه إلى المخرج المناسب", "c": "التحكم في الازدحام"}, "answer": "b", "skill": "Data Plane Understanding"},
        {"id": "n2", "q": "في الإصدار IPv6، أي بروتوكول يستخدم لإدارة مجموعات Multicast؟", "options": {"a": "ICMPv4", "b": "IGMP", "c": "ICMPv6"}, "answer": "c", "skill": "IPv6 Features"},
        {"id": "n3", "q": "ما هي آلية Tunneling لربط IPv4 مع IPv6؟", "options": {"a": "تغليف حزم IPv6 كبيانات داخل حزم IPv4", "b": "حذف حزم IPv4", "c": "تغيير العناوين فيزيائياً"}, "answer": "a", "skill": "Transition Mechanisms"},
        {"id": "n4", "q": "ما هو دور الـ Control Plane؟", "options": {"a": "محلي لكل موجه", "b": "منطق الشبكة لتحديد مسار الحزمة من المصدر للوجهة", "c": "فحص الـ Checksum"}, "answer": "b", "skill": "Control Plane"},
        {"id": "n5", "q": "ما هو التغيير في الـ Checksum في IPv6؟", "options": {"a": "تمت إزالته بالكامل لتسريع المعالجة", "b": "تمت مضاعفة حجمه", "c": "أصبح يعتمد على الـ TCP فقط"}, "answer": "a", "skill": "IPv6 Header"}
    ],
    "OperationsResearch": [
        {"id": "or1", "q": "عند تحويل مسألة Primal بصيغة (Max) إلى Dual، ما هي صيغة دالة الهدف الجديدة؟", "options": {"a": "Max", "b": "Min", "c": "تظل كما هي"}, "answer": "b", "skill": "Duality Principle"},
        {"id": "or2", "q": "ماذا يمثل $Z_D$ في مسألة الـ Dual؟", "options": {"a": "المتغيرات الأولية", "b": "القيود التقنية", "c": "قيمة دالة الهدف المقابلة (المصغرة)"}, "answer": "c", "skill": "Objective Functions"},
        {"id": "or3", "q": "إذا كان القيد في مسألة الـ Primal يحتوي على $\\le$ ، فما هي طبيعة المتغير المقابل في الـ Dual؟", "options": {"a": "$\\omega_i \\ge 0$", "b": "$\\omega_i \\le 0$", "c": "غير مقيد"}, "answer": "a", "skill": "Constraints Mapping"},
        {"id": "or4", "q": "بناءً على المرجع المرفق، ثوابت الطرف الأيمن (b) في الـ Primal تصبح في الـ Dual:", "options": {"a": "معاملات المتغيرات التقنية", "b": "معاملات دالة الهدف (Objective Coefficients)", "c": "تختفي من المعادلة"}, "answer": "b", "skill": "Mathematical Modeling"},
        {"id": "or5", "q": "كم عدد المتغيرات في مسألة الـ Dual إذا كانت مسألة الـ Primal تحتوي على $m$ من القيود؟", "options": {"a": "$n$ متغيرات", "b": "$m$ متغيرات", "c": "$m+n$ متغيرات"}, "answer": "b", "skill": "Dimensionality Analysis"}
    ]
}

# --- مسارات API الرئيسية ---

@app.post("/faculty/upload-syllabus")
def upload_syllabus(course_code: str, faculty_id: int):
    # محاكاة إرفاق المنهج المعتمد ليعتمد عليه الـ API
    for course in db_courses:
        if course.code == course_code:
            course.syllabus_attached = True
            return {"message": f"تم إرفاق المنهج المعتمد لمقرر {course.title} بنجاح. سيقوم الـ API الآن بالاعتماد عليه في التقييم."}
    raise HTTPException(status_code=404, detail="Course not found")

@app.post("/faculty/record-grade")
def record_grade(record: GradeRecord):
    # رصد الدرجات
    db_grades.append(record)
    return {"message": "تم رصد الدرجة بنجاح."}

@app.get("/faculty/my-students/{faculty_id}")
def get_my_students(faculty_id: int):
    # إرجاع الطلاب المرتبطين بعضو هيئة التدريس المخصص وتخصصهم
    students = [s for s in db_users if s.role == "Student" and s.faculty_id == faculty_id]
    return {"students": students}

@app.post("/student/submit-quiz")
def submit_quiz(submission: QuizAnswers):
    student_id = submission.student_id
    if student_id not in db_student_progress:
        db_student_progress[student_id] = {"tests_completed": 0, "skills": []}
    
    # محاكاة تصحيح وتحليل الـ API
    correct_count = 0
    weaknesses = []
    new_skills = []
    
    # دمج أسئلة الشبكات والبحوث للبحث عن الإجابة الصحيحة
    all_qs = QUIZ_BANK["Networks"] + QUIZ_BANK["OperationsResearch"]
    
    for q_id, user_ans in submission.answers.items():
        q_obj = next((q for q in all_qs if q["id"] == q_id), None)
        if q_obj:
            if q_obj["answer"] == user_ans:
                correct_count += 1
                new_skills.append(q_obj["skill"])
            else:
                weaknesses.append(f"ضعف في: {q_obj['skill']}")
    
    # تحديث نسبة الإنجاز والمهارات
    db_student_progress[student_id]["tests_completed"] += 1
    db_student_progress[student_id]["skills"].extend(new_skills)
    
    # كل اختبار يمثل 33% من الإنجاز (بما أنهم 3 اختبارات)
    completion_rate = min(100, db_student_progress[student_id]["tests_completed"] * 33)
    
    return {
        "score": correct_count,
        "total": 10,
        "completion_rate": completion_rate,
        "acquired_skills": list(set(db_student_progress[student_id]["skills"])),
        "weaknesses": weaknesses,
        "ai_analysis": "بناءً على المرجع المرفق، تم تحديد نقاط قوتك وضعفك بنجاح."
    }

# --- محرك البوت الإرشادي ---
@app.post("/chatbot/ask")
def chatbot_ask(question: str = Body(..., embed=True)):
    q = question.strip()
    responses = {
        "أين يمكن ان اجد اختباري؟": "يمكنك إيجاد اختباراتك (الشبكات والبحوث) في قسم 'الاختبارات الذكية' في اللوحة الجانبية.",
        "أين اجد تحليلي؟": "يظهر تحليلك الذكي تلقائياً بعد تسليم أي اختبار في بطاقة 'التحليل الاستباقي'.",
        "كيف ارى مهاراتي المكتسبة؟": "يتم عرض مهاراتك المكتسبة في قسم 'ملفي الشخصي' وتحت نتيجتك بعد كل اختبار.",
        "كم هي نسبة انجازي في شبكات؟": "نسبة إنجازك تزيد بمقدار 33.3% بعد كل اختبار من الاختبارات الثلاثة المقررة.",
        "كيف اتابع درجات طلابي؟": "من خلال حسابك كعضو هيئة تدريس، اذهب لتبويب 'متابعة الطلاب'. ستجد مجموعتك (حتى 5 طلاب).",
        "كيف أرصد درجات طلابي؟": "يمكنك استخدام قسم 'رصد الدرجات' المخصص لأعضاء هيئة التدريس وتحديد اسم الطالب والمقرر.",
        "كيف أضيف مقرر؟": "من خلال صلاحيات عضو هيئة التدريس، يمكنك إرفاق المنهج وإضافة المقرر لربطه بتخصصك.",
        "كم طالب يوجد لدي؟": "بناءً على التوزيع الحالي، يتم إسناد مجموعة من 5 طلاب كحد أقصى لكل عضو هيئة تدريس لمتابعتهم بدقة.",
        "كيف اسجل دخول؟": "المنصة تدعم الدخول الموحد، أدخل رقمك الجامعي أو الوظيفي ليتم توجيهك للوحة المخصصة لك.",
        "هل لايزال هناك اختبار لم أختبره؟": "النظام يوفر 3 اختبارات متتالية. تحقق من نسبة إنجازك؛ إذا كانت أقل من 100%، فهناك اختبار متبقي.",
        "ماهو IPv4?": "هو الإصدار الرابع من بروتوكول الإنترنت، ويستخدم عناوين بطول 32 بت، وهو الأكثر شيوعاً حتى الآن.",
        "ماهو IPv6?": "هو الإصدار السادس والمطور، يستخدم عناوين بطول 128 بت، وأزال خاصية Checksum لتسريع المعالجة عبر الـ Routers.",
        "ماهي Network?": "الشبكة في سياق مسارك الأكاديمي تركز على طبقة الشبكة (Network Layer) وعمليات الـ Forwarding و Routing.",
        "ماهي البحوث؟": "مقرر بحوث العمليات (Operations Research) يركز على البرمجة الخطية، تقليل التكلفة، ومبدأ Duality.",
        "ماهو Dule?": "الـ Duality (المشكلة المقابلة) هو مفهوم رياضي يحول مسألة Primal (مثل تعظيم الربح) إلى مسألة Dual (تصغير التكلفة $Z_D$) للحصول على نفس الحل الأمثل."
    }
    
    # البحث عن إجابة مناسبة
    for key, val in responses.items():
        if key in q or q in key:
            return {"answer": val}
    
    return {"answer": "عذراً، لم أفهم سؤالك. يرجى اختيار أحد الأسئلة المبرمجة مسبقاً في الدليل الإرشادي."}
