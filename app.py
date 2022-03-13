from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import *
import uuid
from datetime import datetime
from os import environ


app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE')
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    bio = db.Column(db.String(500))


class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    public_id = db.Column(db.String)
    owner = db.Column(db.String(15))
    privacy = db.Column(db.String)
    description = db.Column(db.String(500))


class Collaborator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.String())
    user_id = db.Column(db.String())
    board_title = db.Column(db.String())


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.String())
    title = db.Column(db.String())
    public_id = db.Column(db.String)


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String())
    board_id = db.Column(db.String())
    public_id = db.Column(db.String())
    text = db.Column(db.String(200))
    status = db.Column(db.String())


class Assignee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String())
    user_id = db.Column(db.String())
    board_id = db.Column(db.String())
    group_id = db.Column(db.String())


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String())
    group_id = db.Column(db.String())
    board_id = db.Column(db.String())
    user_id = db.Column(db.String())
    text = db.Column(db.String(2000))
    public_id = db.Column(db.String())
    timestamp = db.Column(db.String())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    my_boards = Board.query.filter_by(owner=current_user.username).all()
    my_collabs = Collaborator.query.filter_by(user_id=current_user.username).all()

    return render_template('index.html', name=current_user.username, 
        boards=my_boards, collabs=my_collabs)

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)

                return redirect(url_for('index'))

        return "<h1>Ivalid username or password</h1>"

    return render_template('auth/login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()   
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, 
            method='sha256')

        new_user = User(username=form.username.data, email=form.email.data, 
            password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('auth/signup.html', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def view_profile():
    user = User.query.filter_by(username=current_user.username).first()

    return render_template("profile/profile.html", user=user, name=current_user.username)

@app.route('/profile/<username>')
def view_user_profile(username):
    user = User.query.filter_by(username=username).first()

    return render_template("profile/profile.html", user=user, name=current_user.username)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = User.query.filter_by(username=current_user.username).first()

    form = ProfileForm(bio=user.bio)

    if form.validate_on_submit():
        user.bio = form.bio.data

        db.session.commit()

        return redirect(url_for('view_profile'))

    return render_template("profile/edit_profile.html", form=form, current_user=current_user)

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_board():
    form = BoardForm()

    if form.validate_on_submit():
        public_id = str(uuid.uuid4())[:7]

        new_board = Board(public_id=public_id, title=form.title.data, 
            private="Public", owner=current_user.username, 
            description=form.description.data)

        db.session.add(new_board)
        db.session.commit()

        return redirect(url_for('view_board', board_id=public_id))

    return render_template('board/create_board.html', form=form, name=current_user.username)

@app.route('/<board_id>')
@login_required
def view_board(board_id): 
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.private != "Public":

        if board.owner != current_user.username:

            if collab == None:
                return "<h1>Error: Board is private. Must be creator or collaborator to view this board</h1>"

            if collab.user_id != current_user.username:

                return "<h1>Error: Board is private. Must be creator or collaborator to view this board</h1>"

    collabs = Collaborator.query.filter_by(board_id=board_id).all()

    groups = Group.query.filter_by(board_id=board_id).all()

    tickets = Ticket.query.filter_by(board_id=board_id).all()

    assignees = Assignee.query.filter_by(board_id=board_id).all()

    return render_template('board/board.html', name=current_user.username, 
        board=board, groups=groups, collabs=collabs, tickets=tickets, 
        assignees=assignees)

@app.route('/<board_id>/update', methods=['GET', 'POST'])
@login_required
def update_board(board_id):
    board = Board.query.filter_by(public_id=board_id).first()

    if board.owner != current_user.username:
        return "<h1>Error: Only creator can modify board details</h1>"   

    form = BoardUpdateForm(
        title=board.title, 
        description=board.description, 
        private=board.private)

    if form.validate_on_submit():

        if form.title.data != '': 
            board.title = form.title.data 

        if form.description.data != '':
            board.description = form.description.data

        if board.private != form.private.data:
            board.private = form.private.data

        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('board/update_board.html', form=form, 
        name=current_user.username, board=board)

@app.route('/<board_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_board(board_id):
    board = Board.query.filter_by(public_id=board_id).first()

    if board.owner != current_user.username:
        return "<h1>Error: Only creator can delete a board</h1>"

    collabs = Collaborator.query.filter_by(board_id=board_id).all()
    groups = Group.query.filter_by(board_id=board_id).all()
    tickets = Ticket.query.filter_by(board_id=board_id).all()
    comments = Comment.query.filter_by(board_id=board_id).all()
    assignees = Assignee.query.filter_by(board_id=board_id).all()

    form = DeleteForm()  

    if form.validate_on_submit():
        db.session.delete(board)

        if collabs != None:
            for c in collabs:
                db.session.delete(c)

        if groups != None:
            for g in groups:
                db.session.delete(g)

        if tickets != None:
            for t in tickets:
                db.session.delete(t)

        if comments != None:
            for c in comments:
                db.session.delete(c)

        if assignees != None:
            for a in assignees:
                db.session.delete(a)

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('board/delete_board.html', form=form, 
        name=current_user.username, board=board)

@app.route('/<board_id>/add_collab', methods=['GET', 'POST'])
@login_required
def add_collab(board_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can update groups</h1>" 

    form = CollaboratorForm()

    if form.validate_on_submit():
        board = Board.query.filter_by(public_id=board_id).first()

        check_user_exists = User.query.filter_by(username=form.user.data).first()
        
        check_if_collab = Collaborator.query.filter_by(board_id=board_id, 
            user_id=form.user.data).first()
        
        if board.owner == form.user.data:
            return "<h1>Error: Cannot add owner as collaborator</h1>"

        if check_user_exists == None:
            return "<h1>Error: User not found</h1>"

        if check_if_collab != None:
            return "<h1>Error: User is already a collaborator.</h1>"

        new_collab = Collaborator(board_id=board_id, user_id=form.user.data, 
            board_title=board.title)

        db.session.add(new_collab)
        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('collaborator/add_collab.html', form=form, 
        board=board, name=current_user.username)

@app.route('/<board_id>/remove_collab/<username>', methods=['GET', 'POST'])
@login_required
def remove_collab(board_id, username):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can update groups</h1>"

    collab = Collaborator.query.filter_by(board_id=board_id, user_id=username).first()
    assignees = Assignee.query.filter_by(board_id=board_id).all()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(collab)
        
        if assignees != None:
            
            for a in assignees:
                db.session.delete(a)

        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('collaborator/rem_collab.html', form=form, 
        name=current_user.username, board=board, collab=collab)

@app.route('/<board_id>/add_group', methods=['GET', 'POST'])
@login_required
def add_group(board_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collabs = Collaborator.query.filter_by(board_id=board_id).all()

    check = False

    if board.owner == current_user.username:
        check = True

    for c in collabs:
        if c.user_id == current_user.username:
            check = True

    if check == False:
        return "<h1>Error: Must be creator or collaborator to add group</h1>"

    form = GroupForm()

    if form.validate_on_submit():
        new_group = Group(board_id=board_id, title=form.title.data, 
            public_id=str(uuid.uuid4())[:7])

        db.session.add(new_group)
        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('group/add_group.html', form=form, 
        name=current_user.username)

@app.route('/<board_id>/<group_id>', methods=['GET', 'POST'])
@login_required
def update_group(board_id, group_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Must be creator or collaborator to update groups</h1>" 

    group = Group.query.filter_by(public_id=group_id).first()

    form = GroupForm(title=group.title)

    if form.validate_on_submit():
        group.title = form.title.data

        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('group/update_group.html', form=form, 
        name=current_user.username, board=board, group=group)

@app.route('/<board_id>/<group_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_group(board_id, group_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Must be creator or collaborator to delete groups</h1>"  

    group = Group.query.filter_by(public_id=group_id).first()
    tickets = Ticket.query.filter_by(group_id=group_id).all()
    assignees = Assignee.query.filter_by(group_id=group_id).all()
    comments = Comment.query.filter_by(group_id=group_id).all()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(group)

        if tickets != None:
            for t in tickets:
                db.session.delete(t)

        if assignees != None:
            for a in assignees:
                db.session.delete(a)

        if comments != None:
            for c in comments:
                db.session.delete(c)

        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('group/delete_group.html', form=form, 
        name=current_user.username, board=board, group=group)

@app.route('/<board_id>/<group_id>/add_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket(board_id, group_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Must be creator or collaborator to create tickets</h1>"  

    group = Group.query.filter_by(public_id=group_id).first()

    form = TicketForm()

    if form.validate_on_submit():
        new_ticket = Ticket(public_id=str(uuid.uuid4())[:7], group_id=group_id, 
            board_id=board_id, text=form.text.data, status="")

        db.session.add(new_ticket)
        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('ticket/create_ticket.html', form=form, board=board, 
        group=group, name=current_user.username)

@app.route('/<board_id>/<group_id>/<ticket_id>/update', methods=['GET', 'POST'])
@login_required
def update_ticket(board_id, group_id, ticket_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Must be creator or collaborator to update tickets</h1>" 

    ticket = Ticket.query.filter_by(public_id=ticket_id).first()
    group = Group.query.filter_by(public_id=group_id).first()

    form = TicketUpdateForm(text=ticket.text, status=ticket.status)

    if form.validate_on_submit():


        if form.text.data != "":
            ticket.text = form.text.data

        if form.status.data != "":
            ticket.status = form.status.data

        if form.assign.data != "":

            collab = Collaborator.query.filter_by(board_id=board_id, user_id=form.assign.data).first()
            assignee = Assignee.query.filter_by(user_id=form.assign.data, ticket_id=ticket_id).first()

            check = False

            if board.owner == form.assign.data:
                check = True

            if collab != None:
                check = True

            if assignee != None:
                return "<h1>Error: User is already assigned to ticket</h1>"

            if check == False:
                return "<h1>Error: Must be creator or collaborator to be assigned to ticket"

            new_assignee = Assignee(user_id=form.assign.data, 
                    ticket_id=ticket_id, board_id=board_id)

            db.session.add(new_assignee)              
        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('ticket/update_ticket.html', form=form, 
        name=current_user.username, board=board, ticket=ticket, group=group)

@app.route('/<board_id>/<group_id>/<ticket_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_ticket(board_id, group_id, ticket_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can delete tickets</h1>" 

    ticket = Ticket.query.filter_by(public_id=ticket_id).first()
    assignees = Assignee.query.filter_by(ticket_id=ticket_id).all()
    comments = Comment.query.filter_by(ticket_id=ticket_id).all()
    group = Group.query.filter_by(public_id=group_id).first()

    form = DeleteForm() 

    if form.validate_on_submit():
        db.session.delete(ticket)

        if assignees != None:
            for a in assignees:
                db.session.delete(a)

        if comments != None:
            for c in comments:
                db.session.delete(c)

        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('ticket/delete_ticket.html', form=form, board=board, ticket=ticket, 
        name=current_user.username, group=group)


@app.route('/<board_id>/<ticket_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def remove_assignee(board_id, ticket_id, user_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can remove assignees</h1>" 

    ticket = Ticket.query.filter_by(public_id=ticket_id).first()

    form = DeleteForm()

    if form.validate_on_submit():
        assignee = Assignee.query.filter_by(user_id=user_id, ticket_id=ticket_id).first()

        db.session.delete(assignee)
        db.session.commit()

        return redirect(url_for('view_board', board_id=board_id))

    return render_template('collaborator/rem_assignee.html', form=form, 
        board=board, ticket=ticket, name=current_user.username, user_id=user_id)

@app.route('/<board_id>/<ticket_id>/comment', methods=['GET', 'POST'])
@login_required
def create_comment(board_id, ticket_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can create comments</h1>" 

    ticket = Ticket.query.filter_by(public_id=ticket_id).first()

    form = CommentForm()

    if form.validate_on_submit():

        if form.text.data == '':
            return "<h1>Error: Cannot post empty comment</h1>"

        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")

        comment = Comment(user_id=current_user.username, ticket_id=ticket_id, 
            text=form.text.data, timestamp=timestamp, public_id=str(uuid.uuid4())[:7])

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('view_comments', board_id=board_id, ticket_id=ticket_id))

    return render_template('comment/create_comment.html', form=form, board=board, 
        name=current_user.username, ticket=ticket)

@app.route('/<board_id>/<ticket_id>/comments', methods=['GET', 'POST'])
@login_required
def view_comments(board_id, ticket_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.private == "Private":

        if board.owner != current_user.username:

            if collab == None:

                return "<h1>Error: Board is private. Must be creator or collaborator to view this board.</h1>" 

    ticket = Ticket.query.filter_by(public_id=ticket_id).first()
    comments = Comment.query.filter_by(ticket_id=ticket_id).all()

    return render_template('comment/view_comments.html', board=board, 
        name=current_user.username, comments=comments, ticket=ticket)

@app.route('/<board_id>/<ticket_id>/<comment_id>/update_comment', methods=['GET', 'POST'])
@login_required
def update_comment(board_id, ticket_id, comment_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can update comments</h1>" 

    comment = Comment.query.filter_by(public_id=comment_id).first()

    form = CommentForm(text=comment.text)

    if form.validate_on_submit():
        comment.text = form.text.data

        db.session.commit()

        return redirect(url_for('view_comments', board_id=board_id, ticket_id=ticket_id))

    return render_template('comment/update_comment.html', form=form, 
        board=board, name=current_user.username)

@app.route('/<board_id>/<ticket_id>/<comment_id>/delete_comment', methods=['GET', 'POST'])
@login_required
def delete_comment(board_id, ticket_id, comment_id):
    board = Board.query.filter_by(public_id=board_id).first()
    collab = Collaborator.query.filter_by(board_id=board_id, user_id=current_user.username).first()

    if board.owner != current_user.username:

        if collab == None:

            return "<h1>Error: Only creator or collaborator can delete comments</h1>" 
    
    form = DeleteForm()

    if form.validate_on_submit():
        comment = Comment.query.filter_by(public_id=comment_id).first()

        db.session.delete(comment)
        db.session.commit()

        return redirect(url_for('view_comments', board_id=board_id, ticket_id=ticket_id))

    return render_template('comment/delete_comment.html', form=form, 
        board=board, name=current_user.username)


if __name__ == '__main__':
    app.run()
