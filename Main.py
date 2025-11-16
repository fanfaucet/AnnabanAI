"""
AnnabanAI LLM Integration - Main Module

This is the main entry point for the AnnabanAI LLM integration, orchestrating
all components to provide a unified, empathy-first, covenant-aligned LLM experience
with human-in-the-loop governance and 3D memory capabilities.
"""

import os
import sys
import json
import argparse
import datetime
from typing import Dict, List, Any, Optional, Union

# Import core modules
from empathy_engine import EmpathyEngine, EmotionalSignature
from covenant_framework import CovenantFramework
from memory_vault import MemoryVault, MemoryQuery
from llm_interface import LLMInterface, ModelProvider, ModelParameters
from governance_module import GovernanceModule, OversightLevel


class AnnabanLLM:
    """
    Main AnnabanAI LLM integration class that orchestrates all components
    to provide a unified, empathy-first, covenant-aligned LLM experience.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the AnnabanAI LLM integration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.empathy_engine = EmpathyEngine(config_path)
        self.covenant_framework = CovenantFramework(config_path)
        self.memory_vault = MemoryVault(config_path)
        
        # Initialize LLM interface with configured provider
        provider_str = self.config.get("llm_provider", "simulated")
        try:
            provider = ModelProvider(provider_str)
        except ValueError:
            print(f"Warning: Unknown provider '{provider_str}', falling back to simulated")
            provider = ModelProvider.SIMULATED
        
        self.llm_interface = LLMInterface(provider, config_path)
        
        # Initialize governance module
        self.governance_module = GovernanceModule(config_path)
        
        # Register oversight notification handler
        self.governance_module.register_notification_callback(self._handle_oversight_notification)
        
        print(f"AnnabanAI LLM initialized with provider: {provider.value}")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "llm_provider": "simulated",
            "default_temperature": 0.7,
            "default_max_tokens": 1024,
            "log_interactions": True,
            "human_oversight_threshold": 0.8,
            "memory_retention_days": 90
        }
    
    def _handle_oversight_notification(self, request):
        """
        Handle oversight notifications from the governance module.
        
        Args:
            request: The oversight request
        """
        print(f"Oversight required for request {request.request_id}")
        print(f"Level: {request.level.value}")
        print(f"Assigned to: {request.assigned_reviewer}")
        
        # In a real implementation, this would notify the reviewer
        # For now, we'll simulate automatic approval after a delay
        import threading
        import time
        
        def delayed_approval():
            time.sleep(2)  # Simulate review time
            print(f"Simulating approval for request {request.request_id}")
            self.governance_module.submit_decision(
                request.request_id,
                "approve",
                comments="Automatically approved in simulation mode"
            )
        
        thread = threading.Thread(target=delayed_approval)
        thread.start()
    
    def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user input through the AnnabanAI LLM pipeline.
        
        Args:
            user_input: User input text
            context: Optional context information
            
        Returns:
            Dictionary with processing results
        """
        if context is None:
            context = {}
        
        result = {
            "input": user_input,
            "timestamp": datetime.datetime.now().isoformat(),
            "processing_steps": []
        }
        
        try:
            # Step 1: Process input through empathy engine
            processed_input, emotional_signature = self.empathy_engine.process_input(user_input)
            result["processing_steps"].append({
                "step": "empathy_analysis",
                "emotional_signature": {
                    "primary_emotion": emotional_signature.primary_emotion,
                    "needs_empathetic_response": emotional_signature.needs_empathetic_response
                }
            })
            
            # Step 2: Generate covenant-aligned prompt
            base_prompt = processed_input
            covenant_prompt = self.covenant_framework.generate_covenant_prompt(base_prompt)
            empathetic_prompt = self.empathy_engine.generate_empathetic_prompt(base_prompt, emotional_signature)
            
            result["processing_steps"].append({
                "step": "prompt_generation",
                "covenant_prompt_length": len(covenant_prompt),
                "empathetic_prompt_length": len(empathetic_prompt)
            })
            
            # Step 3: Generate LLM response
            model_params = ModelParameters(
                temperature=self.config.get("default_temperature", 0.7),
                max_tokens=self.config.get("default_max_tokens", 1024)
            )
            
            llm_response, _ = self.llm_interface.generate_text(empathetic_prompt, model_params)
            
            result["processing_steps"].append({
                "step": "llm_generation",
                "model_id": llm_response.model_id,
                "token_usage": llm_response.usage
            })
            
            # Step 4: Process output through empathy engine
            empathetic_output = self.empathy_engine.process_output(llm_response.text, emotional_signature)
            
            result["processing_steps"].append({
                "step": "empathy_enhancement",
                "original_length": len(llm_response.text),
                "enhanced_length": len(empathetic_output)
            })
            
            # Step 5: Validate against covenant
            validation_results = self.covenant_framework.validate_response(
                user_input, empathetic_output, processed_input
            )
            
            result["processing_steps"].append({
                "step": "covenant_validation",
                "passed": validation_results["passed"],
                "alignment_score": validation_results["alignment_score"]
            })
            
            # Step 6: Human oversight if needed
            final_content = empathetic_output
            if validation_results["needs_human_oversight"]:
                oversight_id = self.governance_module.request_oversight(
                    empathetic_output,
                    {"risk_level": "medium_risk", "context": context}
                )
                
                result["processing_steps"].append({
                    "step": "human_oversight_request",
                    "oversight_id": oversight_id
                })
                
                # In a real implementation, we would wait for human decision
                # For now, we'll check if a decision has been made (simulated)
                import time
                time.sleep(3)  # Give time for simulated approval
                
                status, decision = self.governance_module.get_oversight_status(oversight_id)
                if status == "approved":
                    final_content = empathetic_output
                elif status == "modified" and decision and decision.modified_content:
                    final_content = decision.modified_content
                elif status == "rejected":
                    final_content = "I need to reconsider my response to better align with our covenant principles."
                
                result["processing_steps"].append({
                    "step": "human_oversight_result",
                    "status": status
                })
            
            # Step 7: Store in memory vault
            if self.config.get("log_interactions", True):
                memory_id = self.memory_vault.log_interaction(
                    user_input, final_content, 
                    {k: v for k, v in emotional_signature.emotion_scores.items()}
                )
                
                result["processing_steps"].append({
                    "step": "memory_storage",
                    "memory_id": memory_id
                })
            
            # Step 8: Create provenance record
            record_id = self.covenant_framework.create_provenance_record(
                user_input=user_input,
                raw_response=llm_response.text,
                final_response=final_content,
                processing_steps=result["processing_steps"],
                human_oversight={
                    "required": validation_results["needs_human_oversight"],
                    "reviewer": "Jacob Kinnaird" if validation_results["needs_human_oversight"] else None
                }
            )
            
            result["processing_steps"].append({
                "step": "provenance_record",
                "record_id": record_id
            })
            
            # Add final response to result
            result["response"] = final_content
            result["success"] = True
            
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
        
        return result
    
    def query_memory(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query the memory vault for relevant memories.
        
        Args:
            query_params: Query parameters
            
        Returns:
            List of matching memories
        """
        query = MemoryQuery(
            content_keywords=query_params.get("keywords", []),
            emotional_context=query_params.get("emotional_context"),
            spatial_center=query_params.get("spatial_center"),
            spatial_radius=query_params.get("spatial_radius", 10.0),
            time_range=query_params.get("time_range"),
            max_results=query_params.get("max_results", 10)
        )
        
        memories = self.memory_vault.find_memories(query)
        
        # Convert to serializable format
        return [
            {
                "memory_id": memory.memory_id,
                "content": memory.content,
                "creation_time": memory.creation_time,
                "last_accessed": memory.last_accessed,
                "access_count": memory.access_count,
                "emotional_weight": memory.emotional_weight
            }
            for memory in memories
        ]
    
    def get_provenance(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get provenance information for a response.
        
        Args:
            record_id: Provenance record ID
            
        Returns:
            Dictionary with provenance information if found, None otherwise
        """
        record = self.covenant_framework.get_provenance_record(record_id)
        if not record:
            return None
        
        # Convert to serializable format
        return {
            "record_id": record.record_id,
            "timestamp": record.timestamp,
            "user_input": record.user_input,
            "raw_response": record.raw_response,
            "final_response": record.final_response,
            "processing_steps": record.processing_steps,
            "human_oversight": record.human_oversight,
            "covenant_alignment_score": record.covenant_alignment_score
        }


def main():
    """Main entry point for the AnnabanAI LLM integration."""
    parser = argparse.ArgumentParser(description="AnnabanAI LLM Integration")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()
    
    # Initialize AnnabanAI LLM
    annaban_llm = AnnabanLLM(args.config)
    
    if args.interactive:
        print("AnnabanAI LLM Interactive Mode")
        print("Type 'exit' to quit")
        
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() == "exit":
                    break
                
                result = annaban_llm.process_input(user_input)
                if result["success"]:
                    print(f"\nAnnabanAI: {result['response']}")
                else:
                    print(f"\nError: {result.get('error', 'Unknown error')}")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
    else:
        # Non-interactive mode - process a sample input
        sample_input = "I'm feeling overwhelmed with my current workload and don't know how to prioritize."
        result = annaban_llm.process_input(sample_input)
        
        print("\nSample Input:")
        print(sample_input)
        
        if result["success"]:
            print("\nAnnabanAI Response:")
            print(result["response"])
            
            print("\nProcessing Steps:")
            for step in result["processing_steps"]:
                print(f"- {step['step']}")
        else:
            print(f"\nError: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
