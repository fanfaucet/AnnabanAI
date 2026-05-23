# Token Economy

The token economy includes a `TokenManager` for balances/transfers and a `TokenMarketplace` for listings and purchases. The system now supports **cross-LLM token transactions**, enabling seamless integration with ChatGPT and other language models.

> See `token_economy/` modules for complete APIs.

## Core Components

### TokenManager
Methods reflected in usage:
- `get_balance(agent_id: str) -> float`
- `transfer_tokens(sender_id: str, recipient_id: str, amount: float, reason: str) -> None`
- `apply_interest() -> None` (periodic staking interest)

### TokenMarketplace
- `create_listing(seller_id: str, title: str, description: str, price: float, category: str, props: Dict[str, Any]) -> None`
- `get_active_listings() -> List[Dict[str, Any]]`
- `purchase(listing_id: str, buyer_id: str) -> bool`

## Cross-LLM Token Economy

### LLMBridge
Manages agent registration and provider configuration across multiple LLM platforms:
- `register_llm_agent(agent: LLMAgent) -> None` - Register agents from different LLM providers
- `configure_provider(provider: LLMProvider, config: Dict[str, str]) -> None` - Set up API access for LLM providers
- `get_cross_llm_signature(transaction_data: Dict[str, Any]) -> str` - Generate cryptographic signatures for authenticity

**Supported Providers:**
- ChatGPT (OpenAI)
- Claude (Anthropic)
- Gemini (Google)
- Local models

### CrossLLMTokenManager
Enables token transfers between agents on different LLM platforms:
- `transfer_tokens_cross_llm(sender_id, recipient_id, amount, reason, sender_provider, recipient_provider) -> bool`
- `get_balance(agent_id: str) -> float`
- `set_balance(agent_id: str, amount: float) -> None`

### ChatGPTTokenAdapter
Specific integration layer for ChatGPT operations:
- `sync_balance_from_chatgpt(chatgpt_user_id: str) -> float` - Fetch token balance from ChatGPT context
- `initiate_chatgpt_task(task_description: str, reward_tokens: float) -> Dict[str, Any]` - Create tasks for ChatGPT agents
- `claim_task_reward(agent_id: str, task_id: str, reward: float) -> bool` - Claim rewards from completed tasks
- `list_active_tasks() -> List[Dict[str, Any]]` - List all active ChatGPT tasks

### MultiLLMMarketplace
Marketplace enabling cross-provider trading:
- `create_cross_llm_listing(seller_id, seller_provider, title, description, price, category, props) -> str`
- `purchase_across_llms(listing_id, buyer_id, buyer_provider, seller_provider) -> bool`
- `get_listings_by_provider(provider: LLMProvider) -> List[Dict[str, Any]]`
- `get_cross_provider_listings() -> List[Dict[str, Any]]`
- `get_trade_history() -> List[Dict[str, Any]]`

## Examples

### Basic Token Transfer
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

### Cross-LLM Token Transfer
```python
from token_economy.llm_bridge import (
    LLMBridge,
    LLMAgent,
    LLMProvider,
    CrossLLMTokenManager
)

# Create bridge and register agents
bridge = LLMBridge()
bridge.configure_provider(
    LLMProvider.CHATGPT,
    {"api_key": "your-key", "signing_key": "your-signing-key"}
)

# Register agents from different providers
bridge.register_llm_agent(
    LLMAgent(
        agent_id="chatgpt_1",
        name="ChatGPT Agent",
        provider=LLMProvider.CHATGPT,
        model="gpt-4"
    )
)

# Create token manager
token_manager = CrossLLMTokenManager(bridge)
token_manager.set_balance("local_1", 100.0)
token_manager.set_balance("chatgpt_1", 50.0)

# Transfer tokens across LLMs
success = token_manager.transfer_tokens_cross_llm(
    sender_id="local_1",
    recipient_id="chatgpt_1",
    amount=25.0,
    reason="Service payment",
    sender_provider=LLMProvider.LOCAL,
    recipient_provider=LLMProvider.CHATGPT
)
```

### ChatGPT Task and Rewards
```python
from token_economy.chatgpt_adapter import ChatGPTTokenAdapter

adapter = ChatGPTTokenAdapter("your-api-key", token_manager)

# Initiate a task for ChatGPT agents
task = adapter.initiate_chatgpt_task(
    task_description="Analyze sentiment in customer feedback",
    reward_tokens=50.0
)

# Claim reward when task is completed
success = adapter.claim_task_reward(
    agent_id="chatgpt_1",
    task_id=task["task_id"],
    reward=50.0
)
```

### Multi-LLM Marketplace
```python
from token_economy.multi_llm_marketplace import MultiLLMMarketplace

marketplace = MultiLLMMarketplace(token_manager, bridge)

# Create cross-LLM listing
listing_id = marketplace.create_cross_llm_listing(
    seller_id="chatgpt_1",
    seller_provider=LLMProvider.CHATGPT,
    title="Natural Language Analysis",
    description="Expert NLP analysis service",
    price=75.0,
    category="service",
    props={"skill_level": 0.9}
)

# Purchase from different LLM provider
success = marketplace.purchase_across_llms(
    listing_id=listing_id,
    buyer_id="local_1",
    buyer_provider=LLMProvider.LOCAL,
    seller_provider=LLMProvider.CHATGPT
)

# View all trades
trades = marketplace.get_trade_history()
```

## Security Features

- **Cryptographic Signatures**: HMAC-SHA256 signing for cross-LLM transactions
- **Transaction Ledger**: Immutable history of all transfers
- **Provider Validation**: Verification of agent providers before transactions
- **Balance Verification**: Ensures sufficient funds before transfers

## Wallet Integration

For blockchain-style wallets and transaction ledgers in simulations, see [Blockchain Wallet Capabilities](./wallet_capabilities.md).

## Architecture

The cross-LLM token economy is built on three layers:

1. **LLM Bridge Layer**: Agent registration and provider configuration
2. **Token Manager Layer**: Core token transfer and balance logic
3. **Provider Adapter Layer**: Service-specific implementations (ChatGPT, Claude, etc.)
4. **Marketplace Layer**: Cross-provider trading and commerce
