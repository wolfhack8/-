from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="منصة مسار - تجربة مستخدم مطورة")

# --- نماذج البيانات ---
class Course(BaseModel):
    title: str
    code: str
    skills: List[str]

# بيانات المقررات المرجعية المستخرجة من ملفاتك
db_courses = [
    Course(title="شبكات الحاسب", code="CS301", skills=["IPv4/IPv6 Addressing", "Routing Protocols", "Tunneling"]),
    Course(title="بحوث العمليات", code="CS302", skills=["Linear Programming", "Duality Principle", "Optimization"])
]

# --- واجهة المستخدم المطورة ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مسار | Masar AI</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Tajawal', sans-serif; background-color: #f0f4f8; }
        .glass { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); }
        .sidebar-item:hover { background: rgba(59, 130, 246, 0.1); border-right: 4px solid #3b82f6; }
        .card-shadow { box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05); }
    </style>
</head>
<body class="flex min-h-screen">

    <aside class="w-64 bg-white border-l border-gray-200 hidden lg:flex flex-col">
        <div class="p-6">
            <h1 class="text-2xl font-bold text-blue-600">بُوصَلة <span class="text-gray-400 text-sm">مسار</span></h1>
        </div>
        <nav class="flex-1 mt-4">
            <a href="#" class="sidebar-item flex items-center px-6 py-3 text-blue-600 bg-blue-50 border-right-4 border-blue-600">
                <span class="ml-3 text-lg font-medium">لوحة التحكم</span>
            </a>
            <a href="#" class="sidebar-item flex items-center px-6 py-3 text-gray-500 hover:text-blue-600 transition">
                <span class="ml-3 text-lg">المقررات</span>
            </a>
            <a href="#" class="sidebar-item flex items-center px-6 py-3 text-gray-500 hover:text-blue-600 transition">
                <span class="ml-3 text-lg">التقارير الذكية</span>
            </a>
        </nav>
        <div class="p-6 border-t border-gray-100">
            <div class="bg-blue-600 rounded-xl p-4 text-white text-center text-sm shadow-lg">
                نسخة الهاكاثون 1.0
            </div>
        </div>
    </aside>

    <main class="flex-1 p-4 lg:p-8 overflow-y-auto">
        
        <header class="flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
            <div>
                <h2 class="text-2xl font-bold text-gray-800">مرحباً بك في لوحة تحليل الأداء الأكاديمي</h2>
                <p class="text-gray-500">نظام التنبؤ الاستباقي للتعثر الدراسي باستخدام AI</p>
            </div>
            <div class="flex gap-2">
                <button onclick="switchRole('faculty')" id="btn-faculty" class="px-6 py-2 rounded-full font-bold transition bg-blue-600 text-white shadow-md">المحاضر</button>
                <button onclick="switchRole('student')" id="btn-student" class="px-6 py-2 rounded-full font-bold transition bg-white text-gray-600 border">الطالب</button>
            </div>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl card-shadow border-b-4 border-blue-500">
                <p class="text-gray-400 text-sm">إجمالي المقررات</p>
                <h3 class="text-3xl font-bold text-gray-800">2</h3>
            </div>
            <div class="bg-white p-6 rounded-2xl card-shadow border-b-4 border-green-500">
                <p class="text-gray-400 text-sm">دقة التنبؤ</p>
                <h3 class="text-3xl font-bold text-gray-800">94%</h3>
            </div>
            <div class="bg-white p-6 rounded-2xl card-shadow border-b-4 border-purple-500">
                <p class="text-gray-400 text-sm">التخصص</p>
                <h3 class="text-xl font-bold text-gray-800">علوم الحاسب</h3>
            </div>
        </div>

        <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
            <div id="faculty-section" class="xl:col-span-1 bg-white p-8 rounded-3xl card-shadow overflow-hidden relative">
                <div class="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full -mr-16 -mt-16"></div>
                <h3 class="text-xl font-bold mb-6 relative">رصد وتحليل جديد</h3>
                <div class="space-y-4 relative">
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">اسم الطالب</label>
                        <input type="text" id="s_name" class="w-full px-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 transition" placeholder="مثال: سفيان الخلفي">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">الدرجة الحالية (من 100)</label>
                        <input type="number" id="s_score" class="w-full px-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 transition" placeholder="مثال: 55">
                    </div>
                    <div>
                        <label class="block text-sm text-gray-400 mb-1">نسبة الحضور (%)</label>
                        <input type="number" id="s_attendance" class="w-full px-4 py-3 bg-gray-50 border-0 rounded-xl focus:ring-2 focus:ring-blue-500 transition" placeholder="مثال: 70">
                    </div>
                    <button onclick="runAI()" class="w-full bg-blue-600 text-white py-4 rounded-2xl font-bold text-lg hover:bg-blue-700 shadow-lg shadow-blue-200 transition transform hover:-translate-y-1">تحليل بواسطة AI</button>
                </div>
            </div>

            <div class="xl:col-span-2 space-y-6">
                <div id="aiResult" class="hidden bg-white p-8 rounded-3xl card-shadow border border-blue-50">
                    <div class="flex flex-col md:flex-row items-center gap-8">
                        <div class="w-full md:w-1/3">
                             <canvas id="gaugeChart" height="200"></canvas>
                        </div>
                        <div class="w-full md:w-2/3">
                            <div class="flex items-center gap-3 mb-2">
                                <span id="riskBadge" class="px-4 py-1 rounded-full text-sm font-bold">--</span>
                                <h4 id="resNameDisplay" class="text-2xl font-bold text-gray-800">--</h4>
                            </div>
                            <p class="text-gray-500 text-lg mb-4" id="aiLogic">محرك التنبؤ يقوم بتحليل البيانات...</p>
                            <div class="bg-blue-50 p-4 rounded-2xl border-r-4 border-blue-600">
                                <p class="text-blue-800 font-medium italic" id="recommendationText">--</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {% for course in courses %}
                    <div class="bg-white p-5 rounded-2xl card-shadow border border-gray-50 hover:border-blue-200 transition group">
                        <div class="flex justify-between items-start mb-4">
                            <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                            </div>
                            <span class="text-xs font-bold text-gray-300 uppercase tracking-widest">{{ course.code }}</span>
                        </div>
                        <h4 class="font-bold text-lg text-gray-800">{{ course.title }}</h4>
                        <div class="flex flex-wrap gap-2 mt-3">
                            {% for skill in course.skills %}
                            <span class="px-2 py-1 bg-gray-50 text-gray-500 text-xs rounded-md border border-gray-100">{{ skill }}</span>
                            {% endfor %}
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </main>

    <script>
        let chartInstance;
        let currentRole = 'faculty';

        function switchRole(role) {
            currentRole = role;
            const btnF = document.getElementById('btn-faculty');
            const btnS = document.getElementById('btn-student');
            
            if(role === 'faculty') {
                btnF.className = "px-6 py-2 rounded-full font-bold transition bg-blue-600 text-white shadow-md";
                btnS.className = "px-6 py-2 rounded-full font-bold transition bg-white text-gray-600 border";
            } else {
                btnS.className = "px-6 py-2 rounded-full font-bold transition bg-blue-600 text-white shadow-md";
                btnF.className = "px-6 py-2 rounded-full font-bold transition bg-white text-gray-600 border";
            }
        }

        function runAI() {
            const name = document.getElementById('s_name').value;
            const score = parseInt(document.getElementById('s_score').value);
            const attendance = parseInt(document.getElementById('s_attendance').value);

            if (!name || isNaN(score)) return alert("يرجى إدخال البيانات كاملة");

            document.getElementById('aiResult').classList.remove('hidden');
            document.getElementById('resNameDisplay').innerText = name;

            let status = "مستقر (Low Risk)";
            let badgeClass = "bg-green-100 text-green-700";
            let color = "#10b981";
            let rec = "أداء ممتاز! ننصح بالتركيز على 'IPv6 Tunneling' في الفصل القادم لتعزيز الخبرة التقنية.";

            if (score < 60) {
                status = "خطر تعثر (Critical)";
                badgeClass = "bg-red-100 text-red-700";
                color = "#ef4444";
                rec = "تحذير استباقي: الطالب يواجه صعوبة في فهم منطق 'Duality'. ننصح بتقديم خطة علاجية فورية تتضمن جلسات تقوية قبل منتصف الفصل.";
            } else if (score < 75) {
                status = "تنبيه (Medium Risk)";
                badgeClass = "bg-yellow-100 text-yellow-700";
                color = "#f59e0b";
                rec = "أداء متوسط. يُنصح الطالب بمراجعة أساسيات 'Routing protocols' لرفع مستواه الأكاديمي.";
            }

            document.getElementById('riskBadge').innerText = status;
            document.getElementById('riskBadge').className = `px-4 py-1 rounded-full text-sm font-bold ${badgeClass}`;
            document.getElementById('recommendationText').innerText = rec;

            updateChart(score, color);
        }

        function updateChart(score, color) {
            const ctx = document.getElementById('gaugeChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();
            chartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [score, 100 - score],
                        backgroundColor: [color, '#f3f4f6'],
                        borderWidth: 0,
                        circumference: 180,
                        rotation: 270
                    }]
                },
                options: {
                    cutout: '80%',
                    plugins: { legend: { display: false } }
                }
            });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    # تمرير بيانات المقررات ديناميكياً لتظهر في البطاقات
    course_cards = ""
    for c in db_courses:
        skills = "".join([f'<span class="px-2 py-1 bg-gray-50 text-gray-500 text-xs rounded-md border border-gray-100">{s}</span>' for s in c.skills])
        course_cards += f'''
        <div class="bg-white p-5 rounded-2xl card-shadow border border-gray-50 hover:border-blue-200 transition group">
            <div class="flex justify-between items-start mb-4">
                <div class="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                </div>
                <span class="text-xs font-bold text-gray-300 uppercase tracking-widest">{c.code}</span>
            </div>
            <h4 class="font-bold text-lg text-gray-800">{c.title}</h4>
            <div class="flex flex-wrap gap-2 mt-3">{skills}</div>
        </div>'''
    
    return HTML_TEMPLATE.replace("{% for course in courses %}", "").replace("{% endfor %}", "").replace("{% for skill in course.skills %}", "").replace("{% endfor %}", "").replace("", f'<div class="grid grid-cols-1 md:grid-cols-2 gap-4">{course_cards}</div>')
