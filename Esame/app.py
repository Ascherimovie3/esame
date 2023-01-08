from flask import Flask, render_template, url_for, redirect, request, flash, session
from datetime import date, datetime
import dao

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

app = Flask(__name__)
app.config['SECRET_KEY']='9OLWxND4o83j4K4iuopO'

login_manager=LoginManager()
login_manager.login_view='login'
login_manager.init_app(app)


@app.route('/', methods=['GET','POST'])
def home():
    episodes=dao.get_episodes()
    mostloved=dao.get_mostloved()
    followers=dao.get_followers()
    comments= dao.show_comments()

    categories={'Natura','Animali','Musica','Arte','Scienza','Viaggi','Sentimenti'}

    return render_template('home.html', episodes=episodes, mostloved=mostloved, followers=followers, comments=comments, categories=categories)


@app.route('/base')
def base():
    podcasts=dao.get_podcasts()

    return render_template('base.html', podcasts=podcasts)

@app.route('/profilo/<int:id>')
def profilo(id):
    user=dao.get_user_by_id(id)
    followed_podcasts=dao.get_followed_podcasts(id)
    my_podcasts=dao.get_my_podcasts(id)

    return render_template('profilo.html', user=user, followed_podcasts=followed_podcasts, my_podcasts=my_podcasts)


@app.route('/category/<cat>')
def category(cat):
    cat_podcasts=dao.get_podcast_by_category(cat)

    return render_template('category.html',  category=cat , cat_podcasts=cat_podcasts)


@app.route('/podcast/<int:pid>')
def podcast(pid):
    podcast=dao.get_podcast(pid)
    episodes=dao.get_episodes_by_pid(pid)
    comments=dao.get_comments_by_pid(pid)
    followers=dao.get_followers()

    return render_template('podcast.html', podcast=podcast, episodes=episodes, comments=comments, followers=followers)

@app.route('/podcasts/new', methods=['GET','POST'])
def new_podcast():
    if request.method == 'POST':
        if current_user.is_authenticated:

            podcast = request.form.to_dict()

            if podcast['title'] == '':
                app.logger.error('Il podcast non può non avere un titolo!')
                flash('Podcast non creato correttamente: il podcast non può non avere un titolo!', 'danger')
                return redirect(url_for('home'))

            if podcast['description'] == '':
                app.logger.error('Il podcast non può non avere una descrizione!')
                flash('Podcast non creato correttamente: il podcast non può non avere una descrizione!', 'danger')
                return redirect(url_for('home'))

            if podcast['category'] == '':
                app.logger.error('Il podcast non può non avere una categoria!')
                flash('Podcast non creato correttamente: il podcast non può non avere una categoria!', 'danger')
                return redirect(url_for('home'))

            podcast_image = request.files['podcastimg']
            if podcast_image:
                podcast_image.save('static/' + podcast_image.filename)
                podcast['podcastimg'] = podcast_image.filename
            
            id_utente=current_user.id
            podcast['creator']=id_utente

            success=dao.add_podcast(podcast)

            if success:
                flash('Podcast creato correttamente','success')
            else:
                flash('Errore nella creazione del podcast: riprova!','danger')
    
    else:
        flash('Podcast non creato correttamente', 'error')
    
    return redirect(url_for('home'))


@app.route('/episodes/new', methods=['POST'])
def new_episode():
    episode = request.form.to_dict()
    
    if episode['title'] == '':
        app.logger.error('L\'episodio non può non avere titolo!')
        flash('Episodio non creato correttamente: L\'episodio non può non avere titolo!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    if episode['description'] == '':
        app.logger.error('L\'episodio non può non avere descrizione!')
        flash('Episodio non creato correttamente: L\'episodio non può non avere descrizione!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    episode_audio = request.files['audio']
    if episode_audio:
        episode_audio.save('static/' + episode_audio.filename)
        episode['audio'] = episode_audio.filename

    if episode['data'] == '':
        app.logger.error('Devi selezionare una data')
        flash('Episodio non creato correttamente: devi selezionare una data!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    if datetime.strptime(episode['data'], '%Y-%m-%d').date() < date.today():
        app.logger.error('Data errata')
        flash('Episodio non creato correttamente: la data deve essere maggiore o uguale di quella corrente!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    id_utente = current_user.id
    success = dao.add_episode(episode, id_utente)

    if success:
        flash('Episodio aggiunto correttamente', 'success')
    else:
        flash('Errore nell\'aggiunta dell\'episodio: riprova!', 'danger')

    return redirect(url_for('podcast', pid=episode['podcast']))


@app.route('/comments/new', methods=['POST'])
def new_comment():
    comment = request.form.to_dict()
    
    if comment['text'] == '':
        app.logger.error('Il commento non può essere vuoto!')
        flash('Commento non creato correttamente: il commento non può essere vuoto!', 'danger')
        return redirect(url_for('podcast', pid=comment['podcast']))

    id_utente = current_user.id
    success = dao.add_comment(comment, id_utente)

    if success:
        flash('Commento creato correttamente', 'success')
    else:
        flash('Errore nella creazione del commento: riprova!', 'danger')

    return redirect(url_for('podcast', pid=comment['podcast']))


@login_manager.user_loader
def load_user(user_id):
    utente = dao.get_user_by_id(user_id)

    if utente is not None: 
        user = User(id=utente['id'], type=utente['type'], nickname=utente['nickname'], password=utente['password'], usrimg=utente['usrimg'])
    else:
        user = None
        
    return user


@app.route('/accedi')
def login():
    return render_template('login.html')

@app.route('/accedi', methods=['POST'])
def login_post():
    nickname = request.form.get('nickname')
    password = request.form.get('password')

    utente = dao.get_user_by_nickname(nickname)

    if not utente or not check_password_hash(utente['password'], password):
        flash('Credenziali non valide, riprovare', 'danger')
        return redirect(url_for('login'))
    else:
        new = User(id=utente['id'], type=utente['type'], nickname=utente['nickname'], password=utente['password'], usrimg=utente['usrimg'])
        login_user(new, True)

        return redirect(url_for('home'))

@app.route('/iscriviti')
def signup():
    return render_template('signup.html')


@app.route('/iscriviti', methods=['POST'])
def signup_post():
    type = request.form.get('type')
    nickname = request.form.get('nickname')
    password = request.form.get('password')

    user_in_db = dao.get_user_by_nickname(nickname)

    if user_in_db:
        flash('C\'è già un utente registrato con questo nickname', 'danger')
        return redirect(url_for('signup'))
    else:
        usr_image = request.files['usrimg']
        if usr_image:
            usr_image.save('static/' + nickname + ".jpeg")

        new_user = {
            "type": type,
            "nickname": nickname,
            "password": generate_password_hash(password, method='sha256'),
            "usrimg": nickname + ".jpeg"
        }

        success = dao.add_user(new_user)

        if success:
            flash('Utente creato correttamente', 'success')
            return redirect(url_for('home'))
        else:
            flash('Errore nella creazione del utente: riprova!', 'danger')

    return redirect(url_for('signup'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('home'))


@app.route('/follow/<int:pid>/<int:id>')
def follow(pid,id):
    success = dao.follow(pid,id)

    if success:
        flash('Ora segui il podcast!', 'success')
    else:
        flash('Errore nel tentativo di seguire il podcast: riprova!', 'danger')

    return redirect(url_for('podcast', pid=pid))


@app.route('/episodes/modified', methods=['POST'])
def modify_episode():
    episode = request.form.to_dict()
    
    if episode['title'] == '':
        app.logger.error('L\'episodio non può non avere titolo!')
        flash('Episodio non modificato correttamente: L\'episodio non può non avere titolo!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    if episode['description'] == '':
        app.logger.error('L\'episodio non può non avere descrizione!')
        flash('Episodio non modificato correttamente: L\'episodio non può non avere descrizione!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    episode_audio = request.files['audio']
    if episode_audio:
        episode_audio.save('static/' + episode_audio.filename)
        episode['audio'] = episode_audio.filename

    if episode['data'] == '':
        app.logger.error('Devi selezionare una data')
        flash('Episodio non modificato correttamente: devi selezionare una data!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    if datetime.strptime(episode['data'], '%Y-%m-%d').date() < date.today():
        app.logger.error('Data errata')
        flash('Episodio non modificato correttamente: la data deve essere maggiore o uguale di quella corrente!', 'danger')
        return redirect(url_for('podcast', pid=episode['podcast']))

    success = dao.modify_episode(episode)

    if success:
        flash('Episodio modificato correttamente', 'success')
    else:
        flash('Errore nella modifica dell\'episodio: riprova!', 'danger')

    return redirect(url_for('podcast', pid=episode['podcast']))


@app.route('/remove_episode/<int:eid>/<int:pid>')
def remove_episode(eid, pid):
    success = dao.remove_episode(eid)

    if success:
        flash('Episodio rimosso correttamente', 'success')
    else:
        flash('Errore nella rimozione dell\'episodio: riprova!', 'danger')

    return redirect(url_for('podcast', eid=eid, pid=pid))
      

@app.route('/podcasts/modified', methods=['POST'])
def modify_podcast():
    podcast = request.form.to_dict()

    if podcast['title'] == '':
        app.logger.error('Il podcast non può non avere un titolo!')
        flash('Podcast non modificato correttamente: il podcast non può non avere un titolo!', 'danger')
        return redirect(url_for('podcast', podcast['pid']))

    if podcast['description'] == '':
        app.logger.error('Il podcast non può non avere una descrizione!')
        flash('Podcast non modificato correttamente: il podcast non può non avere una descrizione!', 'danger')
        return redirect(url_for('podcast', podcast['pid']))

    if podcast['category'] == '':
        app.logger.error('Il podcast non può non avere una categoria!')
        flash('Podcast non modificato correttamente: il podcast non può non avere una categoria!', 'danger')
        return redirect(url_for('podcast', podcast['pid']))

    podcast_image = request.files['podcastimg']
    if podcast_image:
        podcast_image.save('static/' + podcast_image.filename)
        podcast['podcastimg'] = podcast_image.filename

    success=dao.modify_podcast(podcast)

    if success:
        flash('Podcast creato correttamente','success')
    else:
        flash('Errore nella creazione del podcast: riprova!','danger')

    return redirect(url_for('podcast', podcast['pid']))


@app.route('/remove_podcast/<int:pid>')
def remove_podcast(pid):
    success = dao.remove_podcast(pid)

    if success:
        flash('Podcast rimosso correttamente', 'success')
    else:
        flash('Errore nella rimozione del podcast: riprova!', 'danger')

    return redirect(url_for('podcast', pid=pid))


@app.route('/comments/modified', methods=['POST'])
def modify_comment():
    comment = request.form.to_dict()
    
    if comment['text'] == '':
        app.logger.error('Il commento non può non avere un testo!')
        flash('Commento non modificato correttamente: Il commento non può non avere un testo!', 'danger')
        return redirect(url_for('podcast', pid=comment['podcast']))

    success = dao.modify_comment(comment)

    if success:
        flash('Commento modificato correttamente', 'success')
    else:
        flash('Errore nella modifica del commento: riprova!', 'danger')

    return redirect(url_for('podcast', pid=comment['podcast']))


@app.route('/remove_comment/<int:cid>/<int:pid>')
def remove_comment(cid, pid):
    success = dao.remove_comment(cid)

    if success:
        flash('Commento rimosso correttamente', 'success')
    else:
        flash('Errore nella rimozione del commento: riprova!', 'danger')

    return redirect(url_for('podcast', pid=pid))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)