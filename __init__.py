from comfy_api.latest import ComfyExtension
from .prompt_gpt import PromptGPTNode

class PromptGPTExtension(ComfyExtension):
    async def get_node_list(self) -> list[type]:
        return [PromptGPTNode]

async def comfy_entrypoint():
    return PromptGPTExtension()
