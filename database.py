import aiosqlite
from config import DB_NAME

async def create_tables():
    async with aiosqlite.connect(DB_NAME) as db:
        #Таблица для состояния квиза
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state 
                         (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        
        #Таблица для статистики игроков
        await db.execute('''CREATE TABLE IF NOT EXISTS user_stats 
                         (user_id INTEGER PRIMARY KEY, 
                          username TEXT,
                          last_score INTEGER,
                          total_played INTEGER,
                          all_score INTEGER DEFAULT 0,
                          last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        await db.commit()

async def get_quiz_index(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            results = await cursor.fetchone()
            return results[0] if results else 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', 
                        (user_id, index))
        await db.commit()

async def save_quiz_result(user_id, username, score):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT total_played, all_score FROM user_stats WHERE user_id = ?', (user_id,)) as cursor:
            result = await cursor.fetchone()
            
        if result:
            total_played = result[0] + 1
            all_score = result[1] + score 
            await db.execute('''UPDATE user_stats 
                             SET last_score = ?, total_played = ?, all_score = ?, 
                                 last_played = CURRENT_TIMESTAMP, username = ?
                             WHERE user_id = ?''', 
                          (score, total_played, all_score, username, user_id))
        else:
            all_score = score
            await db.execute('''INSERT INTO user_stats 
                             (user_id, username, last_score, total_played, all_score) 
                             VALUES (?, ?, ?, 1, ?)''', 
                          (user_id, username, score, all_score))
        
        await db.commit()

async def get_user_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT last_score, total_played, last_played, all_score
                              FROM user_stats WHERE user_id = ?''', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_all_stats():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''SELECT username, last_score, total_played, last_played, all_score 
                              FROM user_stats ORDER BY all_score DESC''') as cursor:
            return await cursor.fetchall()
