# type: ignore
from comfy_api.latest import io
import requests

print("🤖 Prompt GPT Node is loading")  

# Store history outside the class to avoid the locked class issue in comfyui (`self` is not allowed in ComfyUI class instances?)
_node_history = {}


class PromptGPTNode(io.ComfyNode):

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="PromptGPTNode",
            display_name="Prompt Generator",
            category="PromptGPT",
            inputs=[
                io.String.Input("system_prompt", 
                    default="You are a prompt generator for stable diffusion. You come up with ONE prompt, using an unexpected, varied and original setting, in an unexpected visual style. Only return one prompt. Do not repeat previous ideas. Do not include the word 'prompt'.",
                    multiline=True),
                io.String.Input("OpenAI_key", default="Your OpenAI API key here"),
                io.Boolean.Input("use_history", default=False),
                io.Boolean.Input("debug_logs", default=False),
            ],
            outputs=[
                io.String.Output("output_text"),
            ],
        )

    # make sure there is always a new prompt generated on workflow queues
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    @classmethod
    def execute(cls, system_prompt, OpenAI_key, use_history=False, debug_logs=False, **kwargs) -> io.NodeOutput:
        print("🤖 Waiting for OpenAI response...")

        # Use a unique key per node or use "global" for shared history among all nodes
        node_key = "global"

        # Initialize/reset history when not using history or when no prior history exists
        if not use_history or node_key not in _node_history:
            _node_history[node_key] = [{"role": "system", "content": system_prompt}]
        
        # check what is in history
        if debug_logs:
            print(f"🤖 History is: {_node_history[node_key]}")

        try:
            text = cls.call_openai(OpenAI_key, node_key, use_history, debug_logs)
        except Exception as e:
            text = f"⚠️ Error: {e}"
        
        return io.NodeOutput(text)

    @classmethod
    def call_openai(cls, api_key, node_key, use_history=False, debug_logs=False):
        url = "https://api.openai.com/v1/responses"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {"model": "gpt-4.1", "input": _node_history[node_key]}

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        textresult = result["output"][0]["content"][0]["text"]

        # Add response to history
        if use_history:
            _node_history[node_key].append({"role": "assistant", "content": textresult})

        if debug_logs:
            print(f"🤖 History length is now: {len(_node_history[node_key])}")

        return textresult