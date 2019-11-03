import requests

def create_b():
    return requests.post(
        "http://127.0.0.1:5000/api/new_board",
        {
            "name": "Бред",
            "address": "b",
            "description": "Тестовый /b/",
            "hidden": False,
            "admin_only": False,
            "read_only": False,
        }
    )
    

def create_thread(board_id):
    return requests.post(
        "127.0.0.1:5000/api/new_thread",
        {
            "board_id": board_id,
            "to_thread": 0,
            "reply_to": None,
            "ip_address": "127.0.0.1",
            "title": "test thread",
            "text": "Создаем тестовый тред (пока без картинки)",
            "tripcode": None,
            "sage": False,

        }
    )

def reply_to_thread(to_thread):
    return requests.post(
        "127.0.0.1:5000/api/new_post",
        {
            "board_id": 1,
            "to_thread": to_thread,
            "reply_to": 1,
            "ip_address": "127.0.0.1",
            "title": "Тестовый ответ",
            "text": "Test reply on thread",
            "tripcode": None,
            "sage": False,

        }
    )

def launch_tests_01():
    answer = create_b()
    try:
        b_json = answer.json()
        print("/b/ has been created")
        print(b_json)
        answer = create_thread(b_json['id'])
        thread_json = answer.json()
        print("thread has been created")
        print(thread_json)
        answer = reply_to_thread(thread_json['id'])
        reply_json = answer.json()
        print("post has been created")
        print(reply_json)
    except:
        print("%i: %s"%(answer.status_code, answer.text))
            


launch_tests_01()


