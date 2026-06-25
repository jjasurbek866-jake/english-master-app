from database.connection import db

class VocabularyService:
    @staticmethod
    async def get_words_by_level(level: str) -> list:
        return await db.fetch("SELECT word_id, word, translation, example_sentence FROM words WHERE level = $1 LIMIT 10", level)