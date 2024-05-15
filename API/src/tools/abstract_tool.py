class LLMTool:
    def __init__(self, name):
        self.name = name
    
    def get_system_prompt(self):
        """Get the system prompt that will be passed to the LLM when this tool is enabled"""
        pass

    def trigger(self, line):
        """Regex on the first line outputed to trigger the tool"""
        pass

    def apply(self):
        """What the tool does, return string will be injected into the prompt after the command"""
        pass
