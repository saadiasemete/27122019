from ..current_timestamp import current_timestamp
class QueryProcessor():

    checkers = []

    @staticmethod
    def convert_misrepresented_booleans(value):
        if isinstance(value, str):
            return value.lower() in ["true", "1"]

    @classmethod
    def on_checks_passed(cls, data, db_session):
        raise NotImplementedError

    @classmethod
    def process(cls, data, db_session, testing_mode = False):
        data.setdefault('__checkers__', {})
        for i in cls.checkers:
            if testing_mode:
                break
            if (i.get('condition') and i['condition'](data, db_session)) or not i.get('condition'):
                check_result = i['checker'](data, db_session)
                print(i['checker'].__name__)
                if check_result[0]:
                    print(check_result)
                    return check_result
                else:
                    data['__checkers__'][i['checker'].__name__] = check_result[1]
        data['__data__']['timestamp'] = current_timestamp()
        return cls.on_checks_passed(data, db_session)
