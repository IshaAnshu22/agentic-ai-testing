import pytest
from tools.calculator import CalculatorTool
from tools.text_utils import TextUtilsTool

def test_calculator_valid_expression():
    tool = CalculatorTool()
    result = tool.execute(expression="2 + 2")
    assert result == "4"

def test_calculator_invalid_expression():
    tool = CalculatorTool()
    result = tool.execute(expression="2 + a")
    assert "Error evaluating expression" in result

def test_text_utils_word_count():
    tool = TextUtilsTool()
    result = tool.execute(text="Hello world!", action="count_words")
    assert result == "Word count: 2"

def test_text_utils_invalid_action():
    tool = TextUtilsTool()
    result = tool.execute(text="Hello", action="unknown")
    assert "Invalid action" in result
