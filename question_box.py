import parcer
import db_manager_sqlite as db_manager

class QuestionBox:

    def __init__(self) -> None:
        self.db = db_manager.DataBase()

    def add_user(self, id: int, name: str, chat_id: int, subscription: bool) -> None:
        self.db.add_user(id, name, chat_id, int(subscription))

    def get_questions(self, user_id: int) -> list[dict]:
        try:
            # парсинг вопросов
            question_list = parcer.get_questions()
            # добавление вопросов в базу данных
            for question in question_list:
                self.db.add_question(user_id, question)
        except Exception as ex:
            print('Parcer exeption', ex)
            # получение вопросов из базы данных
            # иначе вывод сообщения об ошибке
            try:
                question_list = [self.db.get_random_question(user_id) for i in range(2)]
            except Exception as ex:
                print('question_db exeption', ex)
                question_list = [{'question': 'Вопросы неожиданно закончились!'
                                            'Повторите попытку немного позже...',
                                'answer': 'Просим прощения за технические неполадки!!!',
                                'comment': '----------------'}]
        return question_list

    def close(self) -> None:
        self.db.close_connection()
