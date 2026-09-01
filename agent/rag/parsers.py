import os
from abc import ABC, abstractmethod
from utils.logger import setup_logger

logger = setup_logger("parsers")

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> str:
        pass

class TextParser(BaseParser):
    def parse(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.debug(f"Parsed text file: {file_path}")
                return content
        except Exception as e:
            logger.error(f"Failed to parse text file {file_path}: {e}")
            return ""

def get_parser(file_path: str) -> BaseParser:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        return TextParser()
    else:
        logger.warning(f"No specific parser found for {ext}, falling back to TextParser.")
        return TextParser()
