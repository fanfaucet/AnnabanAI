"""
Multi-LLM Marketplace for cross-provider token trading.
Enables agents from different LLM providers to trade services and tokens.
"""

from typing import Dict, List, Any
from datetime import datetime
from token_economy.llm_bridge import LLMProvider, CrossLLMTokenManager, LLMBridge

class MultiLLMMarketplace:
    """
    Marketplace that operates across multiple LLM providers.
    Enables agents from different LLMs to trade services and tokens.
    """
    
    def __init__(self, token_manager: CrossLLMTokenManager, bridge: LLMBridge):
        self.token_manager = token_manager
        self.bridge = bridge
        self.listings: Dict[str, Dict[str, Any]] = {}
        self.active_trades: List[Dict[str, Any]] = []
        self.listing_counter = 0
        
    def create_cross_llm_listing(
        self,
        seller_id: str,
        seller_provider: LLMProvider,
        title: str,
        description: str,
        price: float,
        category: str,
        props: Dict[str, Any]
    ) -> str:
        """
        Create a marketplace listing that's visible across LLM boundaries.
        """
        listing_id = f"{seller_provider.value}_{self.listing_counter}"
        self.listing_counter += 1
        
        self.listings[listing_id] = {
            "id": listing_id,
            "seller_id": seller_id,
            "seller_provider": seller_provider.value,
            "title": title,
            "description": description,
            "price": price,
            "category": category,
            "properties": props,
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }
        
        return listing_id
    
    def purchase_across_llms(
        self,
        listing_id: str,
        buyer_id: str,
        buyer_provider: LLMProvider,
        seller_provider: LLMProvider
    ) -> bool:
        """
        Execute a purchase between agents on different LLM platforms.
        """
        if listing_id not in self.listings:
            return False
        
        listing = self.listings[listing_id]
        
        if not listing["active"]:
            return False
        
        # Execute token transfer
        success = self.token_manager.transfer_tokens_cross_llm(
            sender_id=buyer_id,
            recipient_id=listing["seller_id"],
            amount=listing["price"],
            reason=f"Purchase: {listing['title']}",
            sender_provider=buyer_provider,
            recipient_provider=seller_provider
        )
        
        if success:
            self.active_trades.append({
                "listing_id": listing_id,
                "buyer_id": buyer_id,
                "buyer_provider": buyer_provider.value,
                "seller_id": listing["seller_id"],
                "seller_provider": seller_provider.value,
                "amount": listing["price"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            listing["active"] = False
        
        return success
    
    def get_listings_by_provider(self, provider: LLMProvider) -> List[Dict[str, Any]]:
        """Get all active listings from a specific provider."""
        return [
            listing for listing in self.listings.values()
            if listing["active"] and listing["seller_provider"] == provider.value
        ]
    
    def get_cross_provider_listings(self) -> List[Dict[str, Any]]:
        """Get all active listings across all providers."""
        return [listing for listing in self.listings.values() if listing["active"]]
    
    def get_trade_history(self) -> List[Dict[str, Any]]:
        """Get history of all cross-LLM trades."""
        return self.active_trades
    
    def cancel_listing(self, listing_id: str) -> bool:
        """Cancel an active listing."""
        if listing_id not in self.listings:
            return False
        
        self.listings[listing_id]["active"] = False
        return True
