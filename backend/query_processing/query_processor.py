from ..current_timestamp import current_timestamp
class QueryProcessor():
    """
    TODO: post_checks should return data
    """

    checkers = []

    @classmethod
    def on_checks_passed(cls, data, db_session):
        raise NotImplementedError

    @classmethod
    def process(cls, data, db_session):
        for i in cls.checkers:
            if (i.get('condition') and i['condition'](data, db_session)) or not i.get('condition'):
                err_status = i['checker'](data, db_session)
                if err_status:
                    print(err_status)
                    return err_status
        data['timestamp'] = current_timestamp()
        return cls.on_checks_passed(data, db_session)
