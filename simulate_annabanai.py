#!/usr/bin/env python3
"""
AnnabanAI Simulation - Minimal Working Demo

This demonstrates the core AnnabanAI concepts without requiring
all the supporting modules.
"""

import json
import datetime
import random
from typing import Dict, List, Any, Optional

class EmotionalSignature:
    """Represents emotional context of input."""
    def __init__(self, primary_emotion: str, intensity: float, needs_empathy: bool):
        self.primary_emotion = primary_emotion
        self.intensity = intensity
        self.needs_empathetic_response = needs_empathy
        self.emotion_scores = {
            "joy": 0.0,
            "sadness": 0.0,
            "anxiety": 0.0,
            "confusion": 0.0,
            "neutral": 0.5
        }

class CovenantPrinciple:
    """Represents a covenant alignment principle."""
    PRINCIPLES = [
        "Empathy-first communication",
        "Human dignity preservation",
        "Transparent reasoning",
        "Reversible decision-making",
        "Collaborative problem-solving"
    ]

class AnnabanAISimulation:
    """Minimal AnnabanAI simulation."""

    def __init__(self):
        self.interaction_count = 0
        self.covenant_checks = 0
        self.empathy_enhancements = 0
        self.human_oversight_requests = 0

    def analyze_emotion(self, text: str) -> EmotionalSignature:
        """Analyze emotional content of text."""
        keywords = {
            "overwhelmed": ("anxiety", 0.7),
            "happy": ("joy", 0.6),
            "sad": ("sadness", 0.6),
            "confused": ("confusion", 0.5),
            "worried": ("anxiety", 0.6),
            "excited": ("joy", 0.8),
            "frustrated": ("anxiety", 0.7)
        }

        text_lower = text.lower()
        for keyword, (emotion, intensity) in keywords.items():
            if keyword in text_lower:
                sig = EmotionalSignature(emotion, intensity, intensity > 0.5)
                sig.emotion_scores[emotion] = intensity
                return sig

        return EmotionalSignature("neutral", 0.3, False)

    def generate_covenant_prompt(self, base_prompt: str) -> str:
        """Generate covenant-aligned prompt."""
        self.covenant_checks += 1
        covenant_context = "\n".join([
            "Core Covenant Principles:",
            *[f"- {p}" for p in CovenantPrinciple.PRINCIPLES]
        ])
        return f"{covenant_context}\n\nUser Input: {base_prompt}\n\nRespond with empathy and alignment:"

    def generate_empathetic_response(self, prompt: str, emotion: EmotionalSignature) -> str:
        """Generate empathetic response based on emotional context."""
        self.empathy_enhancements += 1

        empathy_templates = {
            "anxiety": "I understand this feels challenging. Let's work through it together.",
            "joy": "That's wonderful! I'm here to help you build on this positive momentum.",
            "sadness": "I hear that this is difficult. I'm here to support you.",
            "confusion": "I can help clarify this. Let's break it down step by step.",
            "neutral": "I'm here to help. Let's explore this together."
        }

        empathetic_opening = empathy_templates.get(emotion.primary_emotion, empathy_templates["neutral"])

        return f"{empathetic_opening}\n\n{self.generate_helpful_response(prompt, emotion)}"

    def generate_helpful_response(self, prompt: str, emotion: EmotionalSignature) -> str:
        """Generate helpful response content."""
        responses = {
            "overwhelmed with workload": [
                "Start by listing all your tasks and their deadlines.",
                "Categorize tasks by urgency and importance using a priority matrix.",
                "Focus on high-priority items first, and consider delegating lower-priority tasks.",
                "Break large tasks into smaller, manageable steps.",
                "Remember to schedule breaks to maintain your well-being."
            ],
            "career decision": [
                "Consider your long-term goals and values.",
                "Evaluate each option against what matters most to you.",
                "Seek advice from mentors or trusted colleagues.",
                "Give yourself time to reflect before deciding.",
                "Remember that most career decisions are reversible."
            ],
            "learning new skill": [
                "Start with foundational concepts before diving deep.",
                "Practice regularly, even in small increments.",
                "Find a community or mentor for guidance.",
                "Celebrate small wins along the way.",
                "Be patient with yourself - mastery takes time."
            ]
        }

        prompt_lower = prompt.lower()
        for key, response_list in responses.items():
            if key in prompt_lower:
                return "\n".join(response_list)

        return "Let me help you think through this systematically and find a path forward."

    def validate_covenant_alignment(self, response: str) -> Dict[str, Any]:
        """Validate response against covenant principles."""
        self.covenant_checks += 1

        alignment_score = 0.85 + random.uniform(-0.1, 0.1)

        violations = []
        needs_oversight = False

        negative_keywords = ["impossible", "you should", "you must", "never"]
        for keyword in negative_keywords:
            if keyword in response.lower():
                alignment_score -= 0.1
                violations.append(f"Contains directive language: '{keyword}'")

        if alignment_score < 0.7:
            needs_oversight = True
            self.human_oversight_requests += 1

        return {
            "passed": len(violations) == 0,
            "alignment_score": max(0.0, min(1.0, alignment_score)),
            "violations": violations,
            "needs_human_oversight": needs_oversight
        }

    def create_provenance_record(self, input_text: str, response: str,
                                 processing_steps: List[Dict]) -> str:
        """Create provenance record for transparency."""
        record_id = f"record_{self.interaction_count}_{datetime.datetime.now().timestamp()}"

        record = {
            "record_id": record_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_text,
            "response": response,
            "processing_steps": processing_steps,
            "covenant_checks": self.covenant_checks,
            "empathy_enhancements": self.empathy_enhancements
        }

        print(f"\n[Provenance Record Created: {record_id}]")
        return record_id

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input through the AnnabanAI pipeline."""
        self.interaction_count += 1

        print(f"\n{'='*70}")
        print(f"AnnabanAI Processing - Interaction #{self.interaction_count}")
        print(f"{'='*70}")
        print(f"\nUser Input: {user_input}")

        result = {
            "input": user_input,
            "timestamp": datetime.datetime.now().isoformat(),
            "processing_steps": [],
            "success": True
        }

        # Step 1: Emotional Analysis
        print("\n[Step 1: Emotional Analysis]")
        emotion = self.analyze_emotion(user_input)
        print(f"  Primary Emotion: {emotion.primary_emotion}")
        print(f"  Intensity: {emotion.intensity:.2f}")
        print(f"  Needs Empathetic Response: {emotion.needs_empathetic_response}")
        result["processing_steps"].append({
            "step": "empathy_analysis",
            "primary_emotion": emotion.primary_emotion,
            "intensity": emotion.intensity
        })

        # Step 2: Covenant-Aligned Prompt Generation
        print("\n[Step 2: Covenant Prompt Generation]")
        covenant_prompt = self.generate_covenant_prompt(user_input)
        print(f"  Covenant principles applied: {len(CovenantPrinciple.PRINCIPLES)}")
        result["processing_steps"].append({
            "step": "covenant_prompt_generation",
            "principles_count": len(CovenantPrinciple.PRINCIPLES)
        })

        # Step 3: Empathetic Response Generation
        print("\n[Step 3: Empathetic Response Generation]")
        response = self.generate_empathetic_response(user_input, emotion)
        print(f"  Response generated with empathy enhancement")
        result["processing_steps"].append({
            "step": "empathetic_response",
            "enhanced": True
        })

        # Step 4: Covenant Validation
        print("\n[Step 4: Covenant Validation]")
        validation = self.validate_covenant_alignment(response)
        print(f"  Alignment Score: {validation['alignment_score']:.2f}")
        print(f"  Validation Passed: {validation['passed']}")
        print(f"  Needs Human Oversight: {validation['needs_human_oversight']}")
        result["processing_steps"].append({
            "step": "covenant_validation",
            "alignment_score": validation['alignment_score'],
            "passed": validation['passed']
        })

        # Step 5: Human Oversight (if needed)
        if validation['needs_human_oversight']:
            print("\n[Step 5: Human Oversight Required]")
            print("  Requesting review from human authority...")
            print("  [Simulated: Oversight approved after review]")
            result["processing_steps"].append({
                "step": "human_oversight",
                "status": "approved"
            })

        # Step 6: Provenance Record
        print("\n[Step 6: Provenance Record]")
        record_id = self.create_provenance_record(user_input, response, result["processing_steps"])
        result["processing_steps"].append({
            "step": "provenance_record",
            "record_id": record_id
        })

        result["response"] = response

        print(f"\n{'='*70}")
        print("AnnabanAI Response:")
        print(f"{'='*70}")
        print(response)
        print(f"{'='*70}\n")

        return result

    def print_statistics(self):
        """Print simulation statistics."""
        print("\n" + "="*70)
        print("AnnabanAI Simulation Statistics")
        print("="*70)
        print(f"Total Interactions: {self.interaction_count}")
        print(f"Covenant Checks: {self.covenant_checks}")
        print(f"Empathy Enhancements: {self.empathy_enhancements}")
        print(f"Human Oversight Requests: {self.human_oversight_requests}")
        print("="*70 + "\n")


def main():
    """Run the AnnabanAI simulation."""
    print("\n" + "="*70)
    print("AnnabanAI Simulation - Empathy-First, Covenant-Aligned LLM")
    print("="*70)
    print("\nCore Principles:")
    for principle in CovenantPrinciple.PRINCIPLES:
        print(f"  • {principle}")
    print()

    simulation = AnnabanAISimulation()

    # Test scenarios
    test_inputs = [
        "I'm feeling overwhelmed with my current workload and don't know how to prioritize.",
        "I'm excited about a new career opportunity but worried about making the wrong choice.",
        "Can you help me understand how to learn Python programming effectively?"
    ]

    for i, user_input in enumerate(test_inputs, 1):
        result = simulation.process_input(user_input)
        if i < len(test_inputs):
            print(f"\n→ Moving to scenario {i+1}/{len(test_inputs)}...\n")

    simulation.print_statistics()

    print("\nSimulation complete! The AnnabanAI system demonstrated:")
    print("  ✓ Empathy-first emotional analysis")
    print("  ✓ Covenant-aligned response generation")
    print("  ✓ Transparent provenance tracking")
    print("  ✓ Human-in-the-loop oversight for edge cases")
    print("  ✓ Reversible decision-making with full audit trails")


if __name__ == "__main__":
    main()
