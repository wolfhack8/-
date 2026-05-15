from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(
    title="Masar AI Platform - Computer Science Edition",
    description="Learning analytics and adaptive education API for the Masar platform.",
    version="1.0.0",
)

# --- النماذج (Data Models) ---

class User(BaseModel):
    id: int
    name: str
    role: str  # "Faculty" or "Student"
    specialization: str = "Computer Science"

class Course(BaseModel):
    id: int
    title: str
    code: str
    description: str

class AssessmentResult(BaseModel):
    student_id: int
    course_code: str
    score: float # من 100
    skills_mastered: List[str]
    weak_areas: List[str]

# --- قاعدة بيانات وهمية (In-memory DB) ---
db_users: List[User] = []
db_courses: List[Course] = [
    Course(id=1, title="Computer Networking", code="CS301", description="Focus: Network Layer, IPv4/IPv6, Routing protocols"),
    Course(id=2, title="Mathematical Optimization", code="CS302", description="Focus: Linear Programming, Duality, Primal problems")
]
db_results: List[AssessmentResult] = []

# --- منطق الذكاء الاصطناعي (AI Analysis Logic) ---

def generate_ai_analysis(student_id: int):
    student_results = [r for r in db_results if r.student_id == student_id]
    if not student_results:
        return {
            "student_id": student_id,
            "status": "No data",
            "analysis": "لا توجد نتائج اختبارات لتحليلها بعد.",
        }
    
    avg_score = sum(r.score for r in student_results) / len(student_results)
    
    # محاكاة التنبؤ بالتعثر الدراسي (Predictive Risk)
    risk_level = "Low"
    if avg_score < 60:
        risk_level = "High"
    elif avg_score < 75:
        risk_level = "Medium"
    
    analysis_text = f"بناءً على أداء الطالب، مستوى الاستيعاب العام هو {avg_score}%. "
    if risk_level == "High":
        analysis_text += "توصية: يحتاج الطالب إلى خطة علاجية فورية في المفاهيم الأساسية."
    else:
        analysis_text += "توصية: الطالب يسير في المسار الصحيح، يُنصح بزيادة التحديات البرمجية."

    return {
        "student_id": student_id,
        "average_score": avg_score,
        "risk_level": risk_level,
        "ai_recommendation": analysis_text
    }

def require_faculty(user_role: str):
    if user_role.casefold() != "faculty":
        raise HTTPException(status_code=403, detail="عذراً، هذه الصلاحية مخصصة لأعضاء هيئة التدريس فقط.")

# --- المسارات (Routes) ---

@app.get("/")
def home():
    return {
        "message": "Welcome to Masar AI Platform",
        "status": "Online",
        "docs": "/docs",
        "health": "/healthz",
    }

@app.get("/healthz", include_in_schema=False)
def healthz():
    return {"status": "ok"}

# 1. عضو هيئة التدريس: إضافة مقرر
@app.post("/faculty/add-course")
def add_course(course: Course, user_role: str):
    require_faculty(user_role)
    db_courses.append(course)
    return {"message": f"تم إضافة مقرر {course.title} بنجاح."}

# 2. عضو هيئة التدريس: إضافة طالب ورصد درجة (كمرجع للاختبار)
@app.post("/faculty/record-result")
def record_student_result(result: AssessmentResult, user_role: str):
    require_faculty(user_role)
    db_results.append(result)
    return {"message": "تم رصد النتيجة وتحديث قاعدة بيانات التحليل."}

# 3. الطالب: الاطلاع على التحليل الخاص به
@app.get("/student/my-analysis/{student_id}")
def get_student_analysis(student_id: int):
    analysis = generate_ai_analysis(student_id)
    return analysis

# 4. عضو هيئة التدريس: الاطلاع على تحليل جميع الطلاب
@app.get("/faculty/all-students-analysis")
def get_all_analysis(user_role: str):
    require_faculty(user_role)
    
    all_analysis = []
    # جلب معرفات الطلاب الفريدة
    student_ids = sorted(set(r.student_id for r in db_results))
    for s_id in student_ids:
        all_analysis.append(generate_ai_analysis(s_id))
    
    return {"total_students_analyzed": len(student_ids), "reports": all_analysis}

# 5. عرض المقررات المرجعية (علوم الحاسب)
@app.get("/courses/reference")
def get_reference_courses():
    return db_courses

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
