class SystemPromptBuilder:

    def __init__(self, base_prompt):
        self.base_prompt = base_prompt


    def build_system_prompt(self, tools=None):
        system_prompt = self.base_prompt
        
        if tools:
            system_prompt += "\n\nTools:\n\n"

            for tool in tools:
                system_prompt += tool.get_system_prompt()

        return system_prompt
