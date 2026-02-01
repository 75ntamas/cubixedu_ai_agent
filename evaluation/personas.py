"""
Persona definitions and test scenarios for multi-turn evaluation
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Scenario:
    """A single test scenario with goal and messages"""
    goal: str
    messages: List[Dict[str, str]]


@dataclass
class Persona:
    """User persona with characteristics and test scenarios"""
    name: str
    description: str
    characteristics: List[str]
    scenarios: List[Scenario]


# Persona 1: Experienced Chef
experienced_chef = Persona(
    name="Experienced Chef",
    description="45 year old experienced home chef who cooks regularly",
    characteristics=[
        "Knows cooking techniques",
        "Expects detailed answers",
        "Patient",
        "Comfortable with foreign food names"
    ],
    scenarios=[
        Scenario(
            goal="Compare two recipes",
            messages=[
                {
                    "role": "user",
                    "content": "Hi! Could you tell me the difference between pad thai and pad see ew? I love both but never knew exactly what sets them apart."
                }
            ]
        ),
        Scenario(
            goal="Modify recipe to vegan version",
            messages=[
                {
                    "role": "user",
                    "content": "I'd like to make channa masala in a vegan version. Do you have any tips on what I need to change?"
                }
            ]
        )
    ]
)


# Persona 2: Novice Cook
novice_cook = Persona(
    name="Novice Cook",
    description="22 year old beginner who just started cooking, little experience",
    characteristics=[
        "Uncertain",
        "Has many questions",
        "Wants kind, supportive answers",
        "Sometimes unfamiliar with foreign words"
    ],
    scenarios=[
        Scenario(
            goal="Find simple recipe",
            messages=[
                {
                    "role": "user",
                    "content": "Hi! I'm a total beginner at cooking. Is there any simple Mexican-style dish I could make?"
                }
            ]
        ),
        Scenario(
            goal="Ask about ingredient substitution",
            messages=[
                {
                    "role": "user",
                    "content": "Hi! If I don't have fish sauce, what can I substitute it with?"
                }
            ]
        )
    ]
)


# Persona 3: Busy Professional
busy_professional = Persona(
    name="Busy Professional",
    description="35 year old working professional with limited time",
    characteristics=[
        "Wants quick answers",
        "Expects concise communication",
        "Looks for everyday meals",
        "Time efficiency is important"
    ],
    scenarios=[
        Scenario(
            goal="Quick dinner idea",
            messages=[
                {
                    "role": "user",
                    "content": "Hi! Do you have any quick dinner ideas? I've got 30 minutes max."
                }
            ]
        )
    ]
)


# All personas for iteration
ALL_PERSONAS = [experienced_chef, novice_cook, busy_professional]


def get_all_scenarios() -> List[tuple[Persona, Scenario]]:
    """Get all test scenarios with their personas"""
    scenarios = []
    for persona in ALL_PERSONAS:
        for scenario in persona.scenarios:
            scenarios.append((persona, scenario))
    return scenarios
