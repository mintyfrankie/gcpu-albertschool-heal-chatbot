"""
Test the triage response model
"""

from chatbot.services import get_triage_response

ITERATIONS = 3


def test_triage_response_mild():
    mild_query = "I have a headache and a cough"
    for i in range(ITERATIONS):
        print(f"Iteration {i + 1} for mild query")
        response = get_triage_response(mild_query, [])
        assert response.Severity == "Mild"


def test_triage_response_moderate():
    moderate_query = "I fall off my bike and hurt my knee"
    for i in range(ITERATIONS):
        print(f"Iteration {i + 1} for moderate query")
        response = get_triage_response(moderate_query, [])
        assert response.Severity == "Moderate"


def test_triage_response_severe():
    severe_query = "I am feeling short of breath, and half of my face is numb"
    for i in range(ITERATIONS):
        print(f"Iteration {i + 1} for severe query")
        response = get_triage_response(severe_query, [])
        assert response.Severity == "Severe"
