from database import Board, Ban, Post

def create_post(board_id, post_data, db_session):
    """
    The order of checks matters for user experience.
    It should be this way:
    1. Schema check: preventing malformed requests.
    2. Ban check (all levels): goes BEFORE everything else. People shouldn't waste time.
    3. Requirements check (all levels).
    4. Captcha check: only when everything else is fine.
    """

    #checking for basic validity
    if not isinstance(post_data, dict): #should be a valid json dict
        return (False, "Unparseable post_data",)
    try:
        assert board_id #should be not null
        board_id = int(board_id) #should be an integer
    except:
        return (False, "Invalid board_id",)
    
    #is thread or post
    post_data['is_thread'] = not post_data.get('to_thread')
    
    #make sure you post to existing board
    board_result = db_session.query(Board.id).filter(Board.id == post_data['id_board']).all()
    if not len(board_result):
        return (False, "board_id does not exist",)
    elif len(board_result)>1:
        return (False, "Ambiguous board_id",)


    #make sure you post to existing thread
    #notice: we assume that the post index is global
    if not post_data.get('is_thread'):
        post_result = db_session.query(Post.id).filter(Post.id == post_data['to_thread']).all()
        if not len(post_result):
            return (False, "to_thread does not exist",)
        elif len(post_result)>1:
            return (False, "Ambiguous to_thread",)
    
    #not sure how efficient it is tho
    ban_result = db_session.query(Ban.id).filter(Ban.ip_address == post_data['IP'] )
    if db_session.exists(ban_result):
        if post_data['to_thread']:
            if db_session.exists(ban_result.filter(Ban.thread_id == post_data['to_thread'])):
                return (False, "Banned in the thread",)
        if db_session.exists(ban_result.filter(Ban.board_id == post_data['id_board'])):
            return (False, "Banned on the board",)


    #TODO: thread requirements check (if applicable)

    #board requirements check

    #TODO: captcha check
    
