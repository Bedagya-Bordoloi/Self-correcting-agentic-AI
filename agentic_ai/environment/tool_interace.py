class ToolInterface:
    def execute_tool(self, tool_name: str, args: dict):
        if tool_name == "calculator":
            try:
                return eval(args.get("expression", "0"))
            except:
                return "Calculation error"
        elif tool_name == "search":
            return f"Mock search results for '{args.get('query', '')}'"
        return "Unknown tool"