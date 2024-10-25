import json

class ToolManager:
    """
    Manages tools for interaction with OpenAI's API, specifically handling the creation
    and formatting of tools from function schemas and response data.
    """

    @staticmethod
    def tool_from_function_schema(schema: dict) -> dict:
        """
        Takes a dictionary representing a function schema and wraps it in the structure
        expected by OpenAI's API for tool specifications.

        Args:
            schema (dict): The schema defining the function.

        Returns:
            dict: A dictionary formatted as an OpenAI tool specification.
        """
        tool = {
            "type": "function",
            "function": schema
        }
        return tool

    @staticmethod
    def schema_from_response(response: str) -> dict:
        """
        Parses a JSON response from an agent to extract and format a function schema.

        Args:
            response (str): JSON string containing the function's details.

        Returns:
            dict: A dictionary representing the function's schema, ready to be used
                  in creating a new tool.
        """
        try:
            function_request_obj = json.loads(response)
        except json.JSONDecodeError as err:
            raise ValueError("Invalid JSON response") from err

        schema = {
            "name": function_request_obj["name"],
            "description": function_request_obj["description"],
            "parameters": function_request_obj.get("schema", {})
        }
        return schema

if __name__ == "__main__":
    # Example usage:
    response = '{"name": "example_function", "description": "This is a test function.", "schema": {"param1": "value1", "param2": "value2"}}'
    schema = ToolManager.schema_from_response(response)
    tool = ToolManager.tool_from_function_schema(schema)
    print(json.dumps(tool, indent=4))
