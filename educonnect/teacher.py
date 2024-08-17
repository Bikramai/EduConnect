from flask import Blueprint, redirect, url_for, render_template, request, flash
from flask_login import current_user

from educonnect import db
from educonnect.models import Courses, Quiz, Questions, QuizAssignment, Answers, VideoLectures

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')


@teacher.before_request
def check_login():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.signin'))

    if not current_user.is_teacher:
        return redirect(url_for('auth.signin'))


@teacher.route("/")
def index():
    courses = Courses.query.all()

    return render_template("teacher_home.html"
                           , courses=courses)


@teacher.route("/course/<int:course_id>")
def course(course_id):

    course = Courses.query.get_or_404(course_id)

    return render_template("teacher_course.html"
                           , course=course)


@teacher.route("/create_quiz/<int:course_id>", methods=["GET", "POST"])
def create_quiz(course_id):
    course = Courses.query.get_or_404(course_id)

    if request.method == "POST":
        title = request.form.get("title")
        questions = request.form.getlist("questions")

        new_quiz = Quiz(title=title, course=course)
        for question in questions:
            new_quiz.questions.append(Questions(question=question))

        course.quizzes.append(new_quiz)

        for student in course.enrolled_students:
            student.solved_quizzes.append(new_quiz)

        db.session.commit()

        flash("Quiz created successfully!", "success")
        return redirect(url_for("teacher.course", course_id=course_id))

    return render_template("teacher_quiz.html"
                           , course=course)


@teacher.route("/view_answers/<int:quiz_id>/<int:student_id>")
def view_answers(quiz_id, student_id):
    quiz = QuizAssignment.query.filter_by(quiz_id=quiz_id, user_id=student_id).first()

    questions_and_answers = db.session.query(Questions, Answers) \
        .join(Quiz, Questions.quiz_id == Quiz.id) \
        .join(Answers, Questions.id == Answers.question_id) \
        .filter(Questions.quiz_id == quiz_id, Answers.user_id == student_id) \
        .all()

    return render_template("view_answers.html"
                           , quiz=quiz
                           , solution=questions_and_answers)


@teacher.route("/add_video/<int:course_id>", methods=["GET", "POST"])
def add_video(course_id):
    course = Courses.query.get_or_404(course_id)

    if request.method == "POST":
        title = request.form.get("title")
        youtube_link = request.form.get("youtube_link")

        new_video = VideoLectures(title=title, youtube_link=youtube_link, course=course)
        course.video_lectures.append(new_video)

        db.session.commit()

        flash("Video added successfully!", "success")
        return redirect(url_for("teacher.course", course_id=course_id))

    return render_template("add_video.html"
                           , course=course)