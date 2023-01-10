import sqlite3 as sql

class DataBase:

    def __init__(self) -> None:
        self.connection = sql.connect('ask_me_db.sqlite')

        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT,
                chat_id INTEGER,
                subscription INTEGER
                );
            ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT UNIQUE,
                comment TEXT,
                source TEXT,
                author TEXT
                );
            ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS random_question (
                user_id INTEGER,
                question_id INTEGER,
                CONSTRAINT p_key PRIMARY KEY (user_id, question_id)
                );
            ''')
        self.connection.commit()
        print("Database opened successfully")


    def close_connection(self) -> None:
        self.connection.close()


    def add_user(self, id: int, name: str, chat_id: int, subscription: str) -> None:
        self.cursor.execute(f'''
            INSERT OR IGNORE INTO users(id, name, chat_id, subscription)
                VALUES (?,?,?,?)                   
            ''', (id, name, chat_id, subscription))
        self.connection.commit()


    def delete_user(self, id: int) -> None:
        self.cursor.execute(f'''
            DELETE FROM users
                WHERE id= ?
            ''', (id,))
        self.connection.commit()


    def add_question(self, id: int, question: dict) -> None:
        self.cursor.execute(f'''
            INSERT OR IGNORE INTO questions( question, answer, comment, source, author)
                VALUES (?,?,?,?,?)
            ''', (question["question"], question["answer"], question["comment"],
                  question["source"], question["author"]))
        self.connection.commit()
        self.cursor.execute(f'''
            SELECT id FROM questions 
                ORDER BY id DESC 
                LIMIT 1
            ''')
        data = self.cursor.fetchall()
        question_id = data[0][0]
        # записываем связь в random_question, чтобы вопрос не выдавался из базы
        self.add_random_question_info(id, question_id)


    def add_random_question_info(self, user_id: int, question_id: int) -> None:
        self.cursor.execute(f'''
            INSERT INTO random_question(user_id, question_id)
                VALUES (?,?)
            ''', (user_id, question_id))
        self.connection.commit()


    def get_random_question(self, id: int) -> dict:
        self.cursor.execute(f'''
            SELECT id FROM questions
                WHERE NOT EXISTS (
                    SELECT * FROM random_question
                        WHERE user_id = ? AND question_id = questions.id
                )
            ''', (id,))
        data = self.cursor.fetchall()
        question_id = data[0][0]

        self.add_random_question_info(id, question_id)

        self.cursor.execute(f'''
            SELECT question, answer, comment, source, author FROM questions
                WHERE id = ?
            ''', (question_id,))
        data = self.cursor.fetchall()
        question = {
            "question": data[0][0],
            "answer": data[0][1],
            "comment": data[0][2],
            "source": data[0][3],
            "author": data[0][4]
        }
        return question


    def change_subscription(self, id: int, subscription: bool) -> None:
        self.cursor.execute(f'''
            UPDATE users SET subscription = ?
                WHERE id = ?
            ''', (int(subscription), id))
        self.connection.commit()


    def get_subscription(self, id: int) -> int:
        self.cursor.execute(f'''
            SELECT subscription FROM users
                WHERE id = ?
            ''', (id,))
        data = self.cursor.fetchall()
        subscription = data[0][0]
        return bool(subscription)

