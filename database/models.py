from database.connection import db

async def create_tables():
    users_query = """
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username VARCHAR(100),
        full_name VARCHAR(255),
        current_level VARCHAR(10) DEFAULT 'A1',
        target_score VARCHAR(50) DEFAULT 'CEFR C1',
        streak INTEGER DEFAULT 0,
        coins INTEGER DEFAULT 0,
        is_premium BOOLEAN DEFAULT FALSE,
        joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    progress_query = """
    CREATE TABLE IF NOT EXISTS user_progress (
        id SERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
        vocabulary_score REAL DEFAULT 0.0,
        grammar_score REAL DEFAULT 0.0,
        reading_score REAL DEFAULT 0.0,
        listening_score REAL DEFAULT 0.0,
        writing_score REAL DEFAULT 0.0,
        speaking_score REAL DEFAULT 0.0
    );
    """

    words_query = """
    CREATE TABLE IF NOT EXISTS words (
        word_id SERIAL PRIMARY KEY,
        word_type VARCHAR(10) NOT NULL,
        level VARCHAR(10) NOT NULL,
        word VARCHAR(100) NOT NULL,
        translation VARCHAR(255) NOT NULL,
        example_sentence TEXT NOT NULL
    );
    """

    placement_questions_query = """
    CREATE TABLE IF NOT EXISTS placement_questions (
        question_id SERIAL PRIMARY KEY,
        section VARCHAR(20) NOT NULL,
        level VARCHAR(5) NOT NULL,
        question TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_option VARCHAR(1) NOT NULL
    );
    """
    
    await db.execute(users_query)
    await db.execute(progress_query)
    await db.execute(words_query)
    await db.execute(placement_questions_query)