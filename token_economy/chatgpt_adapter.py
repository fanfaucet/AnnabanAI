"""
ChatGPT-specific token operations and integration.
Bridges AnnabanAI token economy with OpenAI's ChatGPT.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from token_economy.llm_bridge import LLMProvider, CrossLLMTokenManager

class ChatGPTTokenAdapter:
    """
    Adapter for ChatGPT-specific token operations.
    Bridges AnnabanAI token economy with OpenAI's ChatGPT.
    """
    
    def __init__(self, api_key: str, cross_llm_manager: CrossLLMTokenManager):
        self.api_key = api_key
        self.manager = cross_llm_manager
        self.gpt_agent_id = "chatgpt_agent"
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        
    def sync_balance_from_chatgpt(self, chatgpt_user_id: str) -> float:
        """
        Fetch token balance from ChatGPT context.
        In practice, this would query OpenAI API or webhook responses.
        """
        return self.manager.get_balance(chatgpt_user_id)
    
    def initiate_chatgpt_task(
        self,
        task_description: str,
        reward_tokens: float
    ) -> Dict[str, Any]:
        """
        Initiate a task that ChatGPT can execute for token rewards.
        """
        task_id = f"gpt_{datetime.utcnow().timestamp()}"
        task = {
            "task_id": task_id,
            "description": task_description,
            "reward": reward_tokens,
            "provider": "chatgpt",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        self.active_tasks[task_id] = task
        return task
    
    def claim_task_reward(self, agent_id: str, task_id: str, reward: float) -> bool:
        """
        Claim reward from completed ChatGPT task.
        """
        if task_id not in self.active_tasks:
            return False
        
        if agent_id not in self.manager.balances:
            self.manager.balances[agent_id] = 0.0
        
        self.manager.balances[agent_id] += reward
        
        self.manager.transaction_history.append({
            "id": f"claim_{task_id}",
            "timestamp": datetime.utcnow().isoformat(),
            "type": "task_completion",
            "agent_id": agent_id,
            "provider": "chatgpt",
            "amount": reward,
            "task_id": task_id
        })
        
        # Mark task as completed
        self.active_tasks[task_id]["status"] = "completed"
        
        return True
    
    def list_active_tasks(self) -> list:
        """
        List all active ChatGPT tasks.
        """
        return [
            task for task in self.active_tasks.values()
            if task["status"] == "active"
        ]
    
    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific ChatGPT task.
        """
        return self.active_tasks.get(task_id)
