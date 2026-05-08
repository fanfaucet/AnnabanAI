import torch
import torch.nn.functional as F
from llm_architecture import AnnabanAILLM
from llm_training import SimpleTokenizer # Reusing the conceptual tokenizer

class InferenceSystem:
    """Handles text generation (inference) and conceptual tool integration."""
    def __init__(self, model: AnnabanAILLM, tokenizer: SimpleTokenizer, device: torch.device, checkpoint_path: str = None):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.model.to(self.device)
        if checkpoint_path:
            self.model.load_state_dict(torch.load(checkpoint_path, map_location=self.device))
        self.model.eval()

    @torch.no_grad()
    def generate_text(self, prompt: str, max_new_tokens: int, temperature: float = 1.0, top_k: int = None) -> str:
        """Generates text based on a given prompt."""
        input_ids = torch.tensor(self.tokenizer.encode(prompt), dtype=torch.long).unsqueeze(0).to(self.device)
        generated_tokens = input_ids.tolist()[0]

        for _ in range(max_new_tokens):
            # Create causal mask for the current sequence length
            seq_len = input_ids.size(1)
            causal_mask = self.model.generate_square_subsequent_mask(seq_len).to(self.device)

            # Get logits for the last token
            logits = self.model(input_ids, causal_mask)[:, -1, :]

            # Apply temperature
            logits = logits / temperature

            # Apply top-k sampling
            if top_k is not None:
                v, _ = torch.topk(logits, top_k)
                logits[logits < v[:, [-1]]] = -float('Inf')

            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            generated_tokens.append(next_token.item())
            input_ids = torch.cat([input_ids, next_token], dim=1)

            if next_token.item() == self.tokenizer.vocab_size - 1: # Assuming last token is EOS
                break

        return self.tokenizer.decode(generated_tokens)

    def _call_tool(self, tool_name: str, args: dict) -> str:
        """Conceptual function to simulate calling an external tool."""
        print(f"[Tool Call] Executing tool: {tool_name} with args: {args}")
        # In a real system, this would involve actual API calls or function execution
        if tool_name == "search_web":
            query = args.get("query", "")
            return f"Search results for '{query}': ... (simulated data)"
        elif tool_name == "get_time":
            import datetime
            return f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}"
        else:
            return f"Unknown tool: {tool_name}"

    def integrate_tool_use(self, model_output: str) -> str:
        """Conceptual function to parse model output for tool calls and execute them."""
        # This is a simplified example. Real tool integration involves more sophisticated parsing
        # and potentially a dedicated tool-calling agent.
        if "<CALL_TOOL>" in model_output and "</CALL_TOOL>" in model_output:
            try:
                tool_call_str = model_output.split("<CALL_TOOL>")[1].split("</CALL_TOOL>")[0]
                # Example format: {"tool_name": "search_web", "args": {"query": "latest AI news"}}
                import json
                tool_call = json.loads(tool_call_str)
                tool_name = tool_call.get("tool_name")
                tool_args = tool_call.get("args", {})
                tool_result = self._call_tool(tool_name, tool_args)
                return model_output.replace(f"<CALL_TOOL>{tool_call_str}</CALL_TOOL>", f"[TOOL_RESULT] {tool_result}")
            except json.JSONDecodeError:
                return f"Error parsing tool call: {tool_call_str}"
            except Exception as e:
                return f"Error during tool execution: {e}"
        return model_output

# Example Usage (conceptual)
if __name__ == '__main__':
    # Model Hyperparameters (matching llm_architecture.py example)
    vocab_size = 10000
    d_model = 512
    num_heads = 8
    num_layers = 6
    d_ff = 2048
    max_seq_len = 1024

    # Instantiate the LLM and Tokenizer
    llm_model = AnnabanAILLM(vocab_size, d_model, num_heads, num_layers, d_ff, max_seq_len)
    tokenizer = SimpleTokenizer(vocab_size)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Create an InferenceSystem instance (without loading a real checkpoint for this example)
    inference_system = InferenceSystem(llm_model, tokenizer, device)

    print("\n--- Text Generation Example ---")
    prompt = "The quick brown fox jumps over the lazy"
    generated_text = inference_system.generate_text(prompt, max_new_tokens=20, temperature=0.7, top_k=50)
    print(f"Prompt: {prompt}")
    print(f"Generated: {generated_text}")

    print("\n--- Tool Use Integration Example ---")
    # Simulate model output that includes a tool call
    model_output_with_tool = "What is the current time? <CALL_TOOL>{\"tool_name\": \"get_time\", \"args\": {}}</CALL_TOOL>"
    processed_output = inference_system.integrate_tool_use(model_output_with_tool)
    print(f"Model output with tool call: {model_output_with_tool}")
    print(f"Processed output: {processed_output}")

    model_output_with_search_tool = "I need to find information about the latest AI advancements. <CALL_TOOL>{\"tool_name\": \"search_web\", \"args\": {\"query\": \"latest AI advancements\"}}</CALL_TOOL>"
    processed_search_output = inference_system.integrate_tool_use(model_output_with_search_tool)
    print(f"\nModel output with search tool call: {model_output_with_search_tool}")
    print(f"Processed search output: {processed_search_output}")
