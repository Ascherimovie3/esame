import sqlite3
import datetime


def get_episodes():
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT EPISODE.eid, EPISODE.audio, EPISODE.title, EPISODE.description, EPISODE.data, EPISODE.podcast, USER.nickname, PODCAST.podcastimg\
            FROM EPISODE\
            JOIN USER ON EPISODE.creator=USER.id\
            JOIN PODCAST ON EPISODE.podcast=PODCAST.pid\
            ORDER BY EPISODE.data DESC'
    cursor.execute(sql)
    episodes = cursor.fetchall()

    cursor.close()
    conn.close()

    return episodes

def get_mostloved():
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT PODCAST.pid, PODCAST.title, PODCAST.podcastimg, USER.nickname\
            FROM PODCAST, FOLLOW, USER\
            WHERE PODCAST.pid=FOLLOW.podcast AND PODCAST.creator=USER.id\
            GROUP BY PODCAST.pid\
            HAVING COUNT(*)=(SELECT MAX(followers)\
                              FROM (SELECT podcast, COUNT(*) AS followers\
                                      FROM FOLLOW\
                                      GROUP BY podcast) AS NUM)'
    cursor.execute(sql)
    mostloved = cursor.fetchone()

    cursor.close()
    conn.close()

    return mostloved

def get_followers():
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT *\
            FROM FOLLOW'
    cursor.execute(sql)
    followers = cursor.fetchall()

    cursor.close()
    conn.close()

    return followers

def show_comments():
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT COMMENT.text, COMMENT.episode, COMMENT.data, USER.nickname\
            FROM COMMENT, USER\
            WHERE COMMENT.user=USER.id'
    cursor.execute(sql)
    comments = cursor.fetchall()

    cursor.close()
    conn.close()

    return comments

def get_podcast_by_category(cat):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT PODCAST.title, PODCAST.podcastimg, PODCAST.pid, PODCAST.category\
            FROM PODCAST\
            WHERE PODCAST.category=?'
    cursor.execute(sql, (cat,))
    cat_podcasts = cursor.fetchall()

    cursor.close()
    conn.close()

    return cat_podcasts

def get_podcasts():
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT PODCAST.pid, PODCAST.title\
            FROM PODCAST'
    cursor.execute(sql)
    podcasts = cursor.fetchall()

    cursor.close()
    conn.close()

    return podcasts

def get_podcast(pid):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT PODCAST.title, PODCAST.description, PODCAST.pid, PODCAST.podcastimg, PODCAST.creator, USER.nickname\
            FROM PODCAST, USER\
            WHERE PODCAST.creator=USER.id AND PODCAST.pid=?'
    cursor.execute(sql, (pid,))
    podcast = cursor.fetchone()

    cursor.close()
    conn.close()

    return podcast

def get_episodes_by_pid(pid):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT *\
            FROM EPISODE\
            WHERE EPISODE.podcast=?'
    cursor.execute(sql, (pid,))
    episodes = cursor.fetchall()

    cursor.close()
    conn.close()

    return episodes

def get_comments_by_pid(pid):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT COMMENT.text, COMMENT.data, COMMENT.user, COMMENT.cid, USER.nickname\
            FROM COMMENT, USER\
            WHERE COMMENT.user=USER.id AND COMMENT.podcast=?'
    cursor.execute(sql, (pid,))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()

    return comments

def add_podcast(podcast):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success=False
    if 'podcastimg' in podcast:
        sql = 'INSERT INTO PODCAST(title,description,category,podcastimg,creator) VALUES(?,?,?,?,?)'
        cursor.execute(sql, (podcast['title'], podcast['description'], podcast['category'], podcast['podcastimg'], podcast['creator']))
    else:
        sql = 'INSERT INTO PODCAST(title,description,category,creator) VALUES(?,?,?,?)'
        cursor.execute(sql, (podcast['title'], podcast['description'], podcast['category'], podcast['creator']))
    try:
        conn.commit()
        success=True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def add_episode(episode, id_utente):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success=False

    sql = 'INSERT INTO EPISODE(audio,title,description,data,podcast,creator) VALUES(?,?,?,?,?,?)'
    cursor.execute(sql, (episode['audio'], episode['title'], episode['description'], episode['data'], episode['podcast'], id_utente))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def add_comment(comment, id_utente):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success=False
    x = datetime.datetime.now()

    sql = 'INSERT INTO COMMENT(text,data,user,episode,podcast) VALUES(?,?,?,?,?)'
    cursor.execute(sql, (comment['text'], x.strftime("%Y-%m-%d"), id_utente, comment['episode'], comment['podcast']))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def get_followed_podcasts(id):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT PODCAST.podcastimg, PODCAST.title, PODCAST.pid, USER.nickname\
            FROM PODCAST, USER, FOLLOW\
            WHERE FOLLOW.podcast=PODCAST.pid AND PODCAST.creator=USER.id AND FOLLOW.user=?'
    cursor.execute(sql, (id,))
    followed_podcasts = cursor.fetchall()

    cursor.close()
    conn.close()

    return followed_podcasts

def get_my_podcasts(id):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT PODCAST.podcastimg, PODCAST.title, PODCAST.pid\
            FROM PODCAST\
            WHERE PODCAST.creator=?'
    cursor.execute(sql, (id,))
    my_podcasts = cursor.fetchall()

    cursor.close()
    conn.close()

    return my_podcasts

def get_user_by_id(user_id):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT *\
            FROM USER\
            WHERE USER.id=?'
    cursor.execute(sql, (user_id,))
    utente = cursor.fetchone()

    cursor.close()
    conn.close()

    return utente

def get_user_by_nickname(nickname):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT *\
            FROM USER\
            WHERE USER.nickname=?'
    cursor.execute(sql, (nickname,))
    utente = cursor.fetchone()

    cursor.close()
    conn.close()

    return utente

def add_user(new_user):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO USER(type, nickname, password, usrimg) VALUES(?,?,?,?)'

    try:
        cursor.execute(sql, (new_user['type'], new_user['nickname'], new_user['password'], new_user['usrimg']))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def follow(pid,id):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False

    sql = 'INSERT INTO FOLLOW(podcast,user) VALUES(?,?)'
    cursor.execute(sql, (pid,id,))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modify_episode(episode):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success=False

    sql = 'UPDATE EPISODE\
            SET audio=?, title=?, description=?, data=?\
            WHERE eid=?'
    cursor.execute(sql, (episode['audio'], episode['title'], episode['description'], episode['data'], episode['eid'],))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def remove_episode(eid):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()

    success = False
    sql = 'DELETE FROM EPISODE\
            WHERE eid=?'

    try:
        cursor.execute(sql, (eid,))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modify_podcast(podcast):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success=False

    sql = 'UPDATE PODCAST\
            SET title=?, description=?, category=?, podcastimg=?\
            WHERE pid=?'
    cursor.execute(sql, (podcast['title'], podcast['description'], podcast['category'], podcast['podcastimg'], podcast['pid'],))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def remove_podcast(pid):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()

    success = False
    sql = 'DELETE FROM PODCAST\
            WHERE pid=?'

    try:
        cursor.execute(sql, (pid,))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def modify_comment(comment):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    x = datetime.datetime.now()

    sql = 'UPDATE COMMENT\
            SET text=?, data=?\
            WHERE cid=?'
    cursor.execute(sql, (comment['text'], x.strftime("%Y-%m-%d"), comment['cid'],))
    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def remove_comment(cid):
    conn = sqlite3.connect('database/esame.db')
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = 1')
    cursor = conn.cursor()

    success = False
    sql = 'DELETE FROM COMMENT\
            WHERE cid=?'

    try:
        cursor.execute(sql, (cid,))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success