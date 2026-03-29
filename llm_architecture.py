import torch
import torch.nn as nn

class EmbeddingLayer(nn.Module):
    """Converts input tokens into dense vector representations."""
    def __init__(self, vocab_size: int, d_model: int, max_seq_len: int):
        super().__init__()
        self.token_embeddings = nn.Embedding(vocab_size, d_model)
        self.position_embeddings = nn.Embedding(max_seq_len, d_model)
        self.d_model = d_model

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        seq_len = input_ids.size(1)
        positions = torch.arange(0, seq_len, dtype=torch.long, device=input_ids.device)
        token_embeds = self.token_embeddings(input_ids)
        position_embeds = self.position_embeddings(positions)
        return token_embeds + position_embeds

class MultiHeadSelfAttention(nn.Module):
    """Multi-head self-attention mechanism with optional FlashAttention."""
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        self.d_k = d_model // num_heads
        self.num_heads = num_heads
        self.wq = nn.Linear(d_model, d_model)
        self.wk = nn.Linear(d_model, d_model)
        self.wv = nn.Linear(d_model, d_model)
        self.wo = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        batch_size = x.size(0)

        q = self.wq(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        k = self.wk(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        v = self.wv(x).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Scaled Dot-Product Attention
        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.d_k ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attention_weights = torch.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        output = torch.matmul(attention_weights, v)
        output = output.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        return self.wo(output)

class PositionWiseFeedForward(nn.Module):
    """Position-wise feed-forward network."""
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.w_1 = nn.Linear(d_model, d_ff)
        self.w_2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w_2(self.dropout(self.relu(self.w_1(x))))

class DecoderBlock(nn.Module):
    """A single decoder block of the transformer model."""
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.self_attn = MultiHeadSelfAttention(d_model, num_heads, dropout)
        self.feed_forward = PositionWiseFeedForward(d_model, d_ff, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        attn_output = self.self_attn(self.norm1(x), mask)
        x = x + self.dropout(attn_output)
        ff_output = self.feed_forward(self.norm2(x))
        x = x + self.dropout(ff_output)
        return x

class AnnabanAILLM(nn.Module):
    """The complete AnnabanAI Large Language Model."""
    def __init__(self, vocab_size: int, d_model: int, num_heads: int, num_layers: int, d_ff: int, max_seq_len: int, dropout: float = 0.1):
        super().__init__()
        self.embedding = EmbeddingLayer(vocab_size, d_model, max_seq_len)
        self.decoder_layers = nn.ModuleList([
            DecoderBlock(d_model, num_heads, d_ff, dropout) for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(d_model)
        self.output_layer = nn.Linear(d_model, vocab_size)

    def forward(self, input_ids: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        x = self.embedding(input_ids)
        for layer in self.decoder_layers:
            x = layer(x, mask)
        x = self.norm(x)
        logits = self.output_layer(x)
        return logits

    def generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

# Example Usage (conceptual)
if __name__ == '__main__':
    vocab_size = 10000
    d_model = 512
    num_heads = 8
    num_layers = 6
    d_ff = 2048
    max_seq_len = 1024

    model = AnnabanAILLM(vocab_size, d_model, num_heads, num_layers, d_ff, max_seq_len)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad)}")

    # Dummy input
    input_ids = torch.randint(0, vocab_size, (1, 50)) # Batch size 1, sequence length 50
    causal_mask = model.generate_square_subsequent_mask(input_ids.size(1))

    output_logits = model(input_ids, causal_mask)
    print(f"Output logits shape: {output_logits.shape}") # Expected: (1, 50, vocab_size)
