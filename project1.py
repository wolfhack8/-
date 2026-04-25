import re
class AlNukhbaRecruitment:
    def __init__(self, job_title, mandatory_skills):
        self.job_title = job_title
        self.mandatory_skills = [skill.lower() for skill in mandatory_skills]
        self.qualified_candidates = []

    def validate_input(self, prompt):
        data = input(prompt).strip()
        while not data:
            print("خطأ: لا يمكن ترك الحقل فارغاً.")
            data = input(prompt).strip()
        return data

    def screen_cv(self, cv_text):
        cv_text = cv_text.lower()
        matched_skills = [skill for skill in self.mandatory_skills if skill in cv_text]
        score = (len(matched_skills) / len(self.mandatory_skills)) * 100
        return score, matched_skills

    def conduct_interview(self):
        questions = [
            "تحدث عن أكبر تحدي تقني واجهته وكيف تعاملت معه؟",
            "لماذا تعتقد أنك المرشح الأنسب لهذه الوظيفة؟",
            "كيف تصف بيئة العمل المثالية بالنسبة لك؟"
        ]
        answers = []
        print("\n--- بدء المقابلة النصية الأولية ---")
        for q in questions:
            ans = self.validate_input(f"{q}: ")
            answers.append(ans)
        
        personality_score = sum(len(a.split()) for a in answers) / 10
        return min(personality_score, 100), answers

    def run_system(self):
        print(f"مرحباً بك في نظام النخبة لتوظيف: {self.job_title}")
        candidate_name = self.validate_input("الرجاء إدخال اسم المتقدم: ")
        cv_content = self.validate_input("الرجاء إدخال نص السيرة الذاتية (CV): ")

        skill_score, skills_found = self.screen_cv(cv_content)
        
        if skill_score < 50:
            print(f"\nالنتيجة: نعتذر {candidate_name}، السيرة الذاتية لا تطابق الحد الأدنى من المعايير.")
            return

        personality_score, interview_responses = self.conduct_interview()
        
        final_score = (skill_score * 0.6) + (personality_score * 0.4)
        
        print("\n" + "="*30)
        print(f"تحليل النظام للمرشح: {candidate_name}")
        print(f"درجة المهارات: {skill_score:.2f}%")
        print(f"درجة التفاعل الشخصي: {personality_score:.2f}%")
        print(f"الدرجة النهائية: {final_score:.2f}%")

        if final_score >= 70:
            print("الحالة: تم الترشيح بنجاح (Shortlisted)")
            print("الإجراء: سيتم جدولة مقابلة نهائية مع الإدارة تلقائياً.")
            self.qualified_candidates.append({
                "name": candidate_name,
                "score": final_score
            })
        else:
            print("الحالة: لم يتم اجتياز مرحلة التقييم الآلي.")
        print("="*30)

if __name__ == "__main__":
    required_skills = ["python", "data analysis", "sql", "communication"]
    system = AlNukhbaRecruitment("مطور برمجيات", required_skills)
    
    while True:
        system.run_system()
        cont = input("\nهل ترغب في إدخال متقدم آخر؟ (نعم/لا): ").strip().lower()
        if cont not in ['نعم', 'yes', 'y']:
            break
