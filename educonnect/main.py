from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user

from educonnect import db
from educonnect.models import DiscussionForm, Comments, Courses, Quiz, Answers, Questions, QuizAssignment

main = Blueprint('main', __name__)


@main.before_request
def check_login():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.signin'))


@main.get("/home")
def index():

    pending_quizzes = QuizAssignment.query.filter_by(user_id=current_user.id, is_solved=False).all()

    return render_template("index.html"
                           , pending_quizzes=pending_quizzes)


@main.route("/discussion", methods=['GET', 'POST'])
def discussion():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        new_discussion = DiscussionForm(title=title, content=content)

        current_user.discussion_form.append(new_discussion)

        db.session.commit()
        flash('Your discussion has been created!', 'success')
        return redirect(url_for('main.discussion'))

    discussions = DiscussionForm.query.order_by(DiscussionForm.id.desc()).all()

    return render_template("discussions.html"
                           , discussions=discussions)


@main.route("/discussion/<int:discussion_id>")
def discussion_detail(discussion_id):
    discussion = DiscussionForm.query.get_or_404(discussion_id)
    return render_template("discussion_detail.html", discussion=discussion)


@main.route("/delete_discussion/<int:discussion_id>")
def delete_discussion(discussion_id):
    discussion = DiscussionForm.query.get_or_404(discussion_id)

    if discussion.started_by != current_user:
        return redirect(url_for('main.discussion'))

    db.session.delete(discussion)
    db.session.commit()
    flash('Your discussion has been deleted!', 'danger')
    return redirect(url_for('main.discussion'))


@main.route("/add_comment/<int:discussion_id>", methods=['POST'])
def add_comment(discussion_id):
    comment = request.form.get('content')
    discussion = DiscussionForm.query.get_or_404(discussion_id)

    new_comment = Comments(content=comment)
    new_comment.commented_by = current_user

    discussion.comments.append(new_comment)

    db.session.commit()

    flash('Your comment has been added!', 'success')
    return redirect(url_for('main.discussion_detail', discussion_id=discussion_id))


@main.route("/courses", methods=['GET', 'POST'])
def courses():
    if request.method == 'POST':
        course_id = request.form.get('course_id')

        course = Courses.query.get_or_404(course_id)

        if course in current_user.enrolled_courses:
            flash('You have already enrolled in this course!', 'danger')
            return redirect(url_for('main.courses'))

        current_user.enrolled_courses.append(course)

        db.session.commit()
        flash('You have been enrolled in a new course!', 'success')
        return redirect(url_for('main.courses'))

    available_courses = Courses.query.all()
    return render_template("courses.html"
                           , available_courses=available_courses)


@main.route("/attempt/<int:quiz_id>", methods=['GET', 'POST'])
def attempt(quiz_id):

    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        answers = request.form.to_dict()
        for key, value in answers.items():
            question_id = key.split('-')[1]

            question = Questions.query.get_or_404(question_id)
            answer = Answers(answer=value, question=question, solved_by=current_user)

            db.session.add(answer)

        quiz_assignment = QuizAssignment.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
        quiz_assignment.is_solved = True

        db.session.commit()
        flash("Quiz Submitted Successfully!", 'success')

        return redirect(url_for('main.index'))

    return render_template("attempt.html", quiz=quiz)


@main.route("/view_lectures/<int:course_id>")
def view_lectures(course_id):
    course = Courses.query.get_or_404(course_id)
    return render_template("view_lectures.html", course=course)