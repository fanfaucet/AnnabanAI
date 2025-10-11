# Token Economy

The token economy includes a `TokenManager` for balances/transfers and a `TokenMarketplace` for listings and purchases.

> See `token_economy/` modules for complete APIs.

## TokenManager
Methods reflected in usage:
- `get_balance(agent_id: str) -> float`
- `transfer_tokens(sender_id: str, recipient_id: str, amount: float, reason: str) -> None`
- `apply_interest() -> None` (periodic staking interest)

## TokenMarketplace
- `create_listing(seller_id: str, title: str, description: str, price: float, category: str, props: Dict[str, Any]) -> None`
- `get_active_listings() -> List[Dict[str, Any]]`
- `purchase(listing_id: str, buyer_id: str) -> bool`

## Examples
```python
from main import create_demo_environment, setup_token_economy, create_marketplace_listings

env = create_demo_environment()
manager, market = setup_token_economy()
create_marketplace_listings(market, env)

# Get an active listing and purchase it
listing = market.get_active_listings()[0]
buyer = next(iter(env.agents.keys()))
success = market.purchase(listing["id"], buyer)
```
