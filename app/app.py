from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI()

class StudentData(BaseModel):
    scores: List[float]
    learning_style: str 
    current_level: Optional[str] = "beginner"

class SimulationDecision(BaseModel):
    decision_id: int
    current_budget: float
    current_reputation: float

class AssessmentResult(BaseModel):
    score: float

@app.get("/")
async def root():
    return {"project": "Bousala AI Engine", "status": "active"}

@app.post("/assessment/analyze")
async def analyze_student_level(data: AssessmentResult):
    score = data.score
    if score < 0 or score > 100:
        raise HTTPException(status_code=400, detail="Invalid score range")
    
    if score >= 85:
        level = "Advanced"
    elif score >= 60:
        level = "Intermediate"
    else:
        level = "Beginner"
    
    return {"level": level, "score": score}

@app.post("/learning/recommend")
async def get_adaptive_content(data: StudentData):
    content_db = {
        "Beginner": ["Basic Video Tutorial", "Introductory Interactive Quiz"],
        "Intermediate": ["Case Study PDF", "Simulation Exercise Level 1"],
        "Advanced": ["Research Paper", "Advanced Management Simulation"]
    }
    
    level = data.current_level
    recommendations = content_db.get(level, content_db["Beginner"])
    
    filtered_content = [item for item in recommendations if data.learning_style.lower() in item.lower() or "Simulation" in item]
    
    return {
        "level": level,
        "recommendations": filtered_content if filtered_content else recommendations
    }

@app.post("/simulation/execute")
async def run_management_sim(choice: SimulationDecision):
    outcomes = {
        1: {"budget_impact": -2000, "reputation_impact": 15, "result": "Successful Expansion"},
        2: {"budget_impact": 500, "reputation_impact": -10, "result": "Cost Cutting - Low Morale"},
        3: {"budget_impact": 0, "reputation_impact": 0, "result": "Status Quo"}
    }
    
    effect = outcomes.get(choice.decision_id, outcomes[3])
    
    new_budget = choice.current_budget + effect["budget_impact"]
    new_reputation = choice.current_reputation + effect["reputation_impact"]
    
    return {
        "action": effect["result"],
        "new_budget": max(0, new_budget),
        "new_reputation": max(0, min(100, new_reputation))
    }

@app.post("/prediction/risk")
async def predict_failure_risk(data: StudentData):
    if not data.scores:
        return {"risk_level": "Low", "probability": 0.0}
    
    average_score = sum(data.scores) / len(data.scores)
    trend = data.scores[-1] - data.scores[0]
    
    risk_score = (100 - average_score) * 0.7 - (trend * 0.3)
    probability = max(0, min(100, risk_score))
    
    return {
        "risk_level": "High" if probability > 60 else "Moderate" if probability > 30 else "Low",
        "failure_probability": f"{probability:.2f}%",
        "action_required": probability > 50
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
