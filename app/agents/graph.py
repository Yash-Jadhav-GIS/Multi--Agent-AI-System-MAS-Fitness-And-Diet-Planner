from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Any
from app.agents.diet_agent import diet_agent_node
from app.agents.workout_agent import workout_agent_node


class PlanState(TypedDict):
    name: str
    age: int
    gender: str
    location: str
    current_date: str
    height_cm: float
    weight_kg: float
    bmi: float
    bmi_category: str
    bmr: float
    tdee: float
    activity_level: str
    goal: str
    food_preference: str
    workout_preference: str
    medical: Optional[str]
    diet_plan: Optional[dict]
    diet_plan_error: Optional[str]
    workout_plan: Optional[dict]
    workout_plan_error: Optional[str]


def build_graph():
    """
    Builds a LangGraph where diet and workout agents run sequentially,
    each independently capturing success/failure in state.
    """
    graph = StateGraph(PlanState)

    graph.add_node("diet_agent", diet_agent_node)
    graph.add_node("workout_agent", workout_agent_node)

    graph.set_entry_point("diet_agent")
    graph.add_edge("diet_agent", "workout_agent")
    graph.add_edge("workout_agent", END)

    return graph.compile()


plan_graph = build_graph()