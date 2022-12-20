import requests
from bs4 import BeautifulSoup


def get_questions():

    url = "https://db.chgk.info/ajaxblocks?_=1631299486553&blocks=chgk_db-1&path=last&nocache=1.json"
    response = requests.get(url)
    content_raw = eval(response.content)['chgk_db-1']['content']
    content = content_raw.replace("\\", "")

    soup = BeautifulSoup(content, "html.parser")
    questions_html = soup.find_all("div", class_="random_question")

    question_list = []

    for element in questions_html:
        question = {
            "question": "",
            "answer": "",
            "comment": "",
            "source": "",
            "author": ""
        }
        question_answer_raw = element.text.replace("'", '"')
        question_answer = question_answer_raw.split("\n...\n")

        question["question"] = "\n".join(question_answer[0].split("\n")[3:])

        text = question_answer[1]

        for sep in [["Комментарий:", "answer"], ["Источник(и):", "comment"], ["Автор:", "source"]]:

            if sep[0] in text:
                text_split = text.split(sep[0])
                question[sep[1]] = text_split[0].strip("\n")
                text = text_split[1]

            if sep[1] == "source":
                question["author"] = text.strip("\n")

        question_list.append(question)

    return question_list


if __name__ == "__main__":

    question_list = get_questions()
    
    for question in question_list:
        print(question["question"])
        print("------------------")
        print(question["answer"])
        print("------------------")
        print(question["comment"])
        print("------------------")
        print(question["source"])
        print("------------------")
        print(question["author"])
