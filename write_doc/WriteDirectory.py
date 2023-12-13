import ast
from typing import Union, Dict

from metagpt.actions import Action
from metagpt.logs import logger
from metagpt.utils.common import OutputParser


class WriteDirectory(Action):
    """Action class for writing tutorial directories.

    Args:
        name: The name of the action.
        language: The language to output, default is "Chinese".
    """

    def __init__(self, name: str = "", language: str = "Chinese", *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.language = language

    async def run(self, topic: str, *args, **kwargs) -> Dict:
        """Execute the action to generate a tutorial directory according to the topic.

        Args:
            topic: The tutorial topic.

        Returns:
            the tutorial directory information, including {"title": "xxx", "directory": [{"dir 1": ["sub dir 1", "sub dir 2"]}]}.
        """
        COMMON_PROMPT = """
        You are now a seasoned technical professional in the field of the internet. 
        We need you to write a technical tutorial with the topic "{topic}".
        """

        DIRECTORY_PROMPT = COMMON_PROMPT + """
        Please provide the specific table of contents for this tutorial, strictly following the following requirements:
        1. The output must be strictly in the specified language, {language}.
        2. Answer strictly in the dictionary format like {{"title": "xxx", "directory": [{{"dir 1": ["sub dir 1", "sub dir 2"]}}, {{"dir 2": ["sub dir 3", "sub dir 4"]}}]}}.
        3. The directory should be as specific and sufficient as possible, with a primary and secondary directory.The secondary directory is in the array.
        4. Do not have extra spaces or line breaks.
        5. Each directory title has practical significance.
        """
        prompt = DIRECTORY_PROMPT.format(topic=topic, language=self.language)
        resp = await self._aask(prompt=prompt)
        return OutputParser.extract_struct(resp, dict)

    def extract_struct(cls, text: str, data_type: Union[type(list), type(dict)]) -> Union[list, dict]:
        """Extracts and parses a specified type of structure (dictionary or list) from the given text.
        The text only contains a list or dictionary, which may have nested structures.

        Args:
            text: The text containing the structure (dictionary or list).
            data_type: The data type to extract, can be "list" or "dict".

        Returns:
            - If extraction and parsing are successful, it returns the corresponding data structure (list or dictionary).
            - If extraction fails or parsing encounters an error, it throw an exception.

        Examples:
            >>> text = 'xxx [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}] xxx'
            >>> result_list = OutputParser.extract_struct(text, "list")
            >>> print(result_list)
            >>> # Output: [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}]

            >>> text = 'xxx {"x": 1, "y": {"a": 2, "b": {"c": 3}}} xxx'
            >>> result_dict = OutputParser.extract_struct(text, "dict")
            >>> print(result_dict)
            >>> # Output: {"x": 1, "y": {"a": 2, "b": {"c": 3}}}
        """
        # Find the first "[" or "{" and the last "]" or "}"
        start_index = text.find("[" if data_type is list else "{")
        end_index = text.rfind("]" if data_type is list else "}")

        if start_index != -1 and end_index != -1:
            # Extract the structure part
            structure_text = text[start_index: end_index + 1]

            try:
                # Attempt to convert the text to a Python data type using ast.literal_eval
                result = ast.literal_eval(structure_text)

                # Ensure the result matches the specified data type
                if isinstance(result, list) or isinstance(result, dict):
                    return result

                raise ValueError(f"The extracted structure is not a {data_type}.")

            except (ValueError, SyntaxError) as e:
                raise Exception(f"Error while extracting and parsing the {data_type}: {e}")
        else:
            logger.error(f"No {data_type} found in the text.")
            return [] if data_type is list else {}


if __name__ == '__main__':
    text = 'xxx [1, 2, ["a", "b", [3, 4]], {"x": 5, "y": [6, 7]}] xxx'
    print(text)
    result_list = OutputParser.extract_struct(text, list)
    print(result_list)

    text = 'xxx {"x": 1, "y": {"a": 2, "b": {"c": 3}}} xxx'
    print(text)
    result_dict = OutputParser.extract_struct(text, dict)
    print(result_dict)
