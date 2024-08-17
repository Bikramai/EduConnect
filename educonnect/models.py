from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey

from educonnect import db, lm


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class CourseEnrolment(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(80))
    username = Column(String(80), unique=True)
    password = Column(String(80))

    is_teacher = Column(Boolean, default=False)


class DiscussionForm(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"))

    started_by = db.relationship("User", backref="discussion_form")

    def get_comment_count(self):
        return len(self.comments)


class Comments(db.Model):
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("user.id"))
    discussion_form_id = Column(Integer, ForeignKey("discussion_form.id"))

    commented_by = db.relationship("User", backref="comments")
    discussion_form = db.relationship("DiscussionForm", backref="comments")


class Courses(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))

    enrolled_students = db.relationship("User", secondary="course_enrolment", backref="enrolled_courses")


class VideoLectures(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    youtube_link = Column(Text)
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = db.relationship("Courses", backref="video_lectures")

class QuizAssignment(db.Model):
    id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    is_solved = Column(Boolean, default=False)

    quiz = db.relationship("Quiz", backref="quiz_assignment")
    user = db.relationship("User", backref="quiz_assignment")
    course = db.relationship("Courses", backref="quiz_assignment")


class Quiz(db.Model):
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    course_id = Column(Integer, ForeignKey("courses.id"))

    course = db.relationship("Courses", backref="quizzes")
    assigned_to = db.relationship("User", secondary="quiz_assignment", backref="solved_quizzes")


class Questions(db.Model):
    id = Column(Integer, primary_key=True)
    question = Column(String(255))
    quiz_id = Column(Integer, ForeignKey("quiz.id"))

    quiz = db.relationship("Quiz", backref="questions")


class Answers(db.Model):
    id = Column(Integer, primary_key=True)
    answer = Column(String(255))
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

    question = db.relationship("Questions", backref="answers")
    solved_by = db.relationship("User", backref="answers")
