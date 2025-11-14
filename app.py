from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
# small improvements: sqlite file, secret for flash messages, and small SQLAlchemy tuning
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'replace-this-with-a-secure-random-key'  # change for production

db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(200), nullable=False, unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200))

    # Using table name 'enrollments' as secondary keeps compatibility with your current DB
    courses = db.relationship(
        'Course',
        backref='students',
        lazy='dynamic',
        secondary='enrollments'
    )


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(200), nullable=False, unique=True)
    course_name = db.Column(db.String(200), nullable=False)
    course_description = db.Column(db.String(200))


class Enrollment(db.Model):
    """
    Keeps the same table name 'enrollments' so the DB stays compatible.
    This class name is singular (conventional) but __tablename__ remains 'enrollments'.
    """
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)


with app.app_context():
    db.create_all()


# ---------------------------
# Helpers
# ---------------------------
def get_student_or_404(student_id):
    student = db.session.get(Student, student_id)
    if student is None:
        abort(404)
    return student


def get_course_or_404(course_id):
    course = db.session.get(Course, course_id)
    if course is None:
        abort(404)
    return course


# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    students = Student.query.all()
    return render_template('index.html', students=students)


@app.route('/student/create/', methods=['GET', 'POST'])
def create_student():
    if request.method == 'GET':
        return render_template('student_create.html')

    # POST
    roll_number = request.form.get('roll', '').strip()
    first_name = request.form.get('f_name', '').strip()
    last_name = request.form.get('l_name', '').strip()

    # basic validation: ensure required fields supplied
    if not roll_number or not first_name:
        flash('Roll number and first name are required.', 'error')
        return render_template('student_create.html'), 400

    exist_student = Student.query.filter_by(roll_number=roll_number).first()
    if exist_student:
        # keep existing behaviour (render an "already exists" page), but also flash
        flash('Student with this roll number already exists.', 'warning')
        return render_template('student_already_exists.html')

    student = Student(roll_number=roll_number, first_name=first_name, last_name=last_name)
    db.session.add(student)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Database error when creating student. Possibly duplicate roll.', 'error')
        return render_template('student_already_exists.html'), 500

    # use url_for for maintainability
    return redirect(url_for('index'))


# provide an endpoint alias 'student_detail' so templates that call url_for('student_detail', ...)
# work even if the function name is different.
@app.route("/student/<int:student_id>/", endpoint='student_detail')
def student_details(student_id):
    student = get_student_or_404(student_id)
    # courses can be accessed in template via student.courses (relationship)
    return render_template('student_details.html', student=student)


@app.route('/student/<int:student_id>/withdraw/<int:course_id>/')
def withdraw_course(student_id, course_id):
    student = get_student_or_404(student_id)
    enrollment = Enrollment.query.filter_by(estudent_id=student.student_id, ecourse_id=course_id).first()
    if not enrollment:
        flash('Enrollment not found.', 'warning')
        return redirect(url_for('index'))

    db.session.delete(enrollment)
    db.session.commit()
    flash('Student withdrawn from course.', 'success')
    return redirect(url_for('index'))


@app.route("/student/<int:student_id>/update/", methods=['GET', 'POST'])
def update_student(student_id):
    student = get_student_or_404(student_id)
    courses = Course.query.all()

    if request.method == 'GET':
        return render_template('student_update.html', student=student, courses=courses)

    # POST - update name and optionally enroll in a new course
    first_name = request.form.get('f_name', '').strip()
    last_name = request.form.get('l_name', '').strip()

    if not first_name:
        flash('First name cannot be empty.', 'error')
        return redirect(url_for('student_detail', student_id=student.student_id))

    student.first_name = first_name
    student.last_name = last_name

    new_course_id_raw = request.form.get('course', '').strip()
    if new_course_id_raw:
        try:
            new_course_id = int(new_course_id_raw)
        except ValueError:
            flash('Invalid course selected.', 'error')
            return redirect(url_for('student_detail', student_id=student.student_id))
        # check course exists
        course = db.session.get(Course, new_course_id)
        if not course:
            flash('Selected course does not exist.', 'error')
            return redirect(url_for('student_detail', student_id=student.student_id))

        # check if already enrolled
        already = Enrollment.query.filter_by(estudent_id=student.student_id, ecourse_id=new_course_id).first()
        if already:
            flash('Student already enrolled in that course.', 'info')
            db.session.commit()
            return redirect(url_for('student_detail', student_id=student.student_id))

        new_enrollment = Enrollment(estudent_id=student.student_id, ecourse_id=new_course_id)
        db.session.add(new_enrollment)

    db.session.commit()
    flash('Student updated successfully.', 'success')
    return redirect(url_for('student_detail', student_id=student.student_id))


@app.route("/student/<int:student_id>/delete/", methods=['GET'])
def delete_student(student_id):
    student = get_student_or_404(student_id)
    enrollments = Enrollment.query.filter_by(estudent_id=student.student_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('index'))


@app.route('/courses/')
def courses():
    all_courses = Course.query.all()
    return render_template('course_list.html', courses=all_courses)


@app.route('/course/create/', methods=['GET', 'POST'])
def create_course():
    if request.method == 'GET':
        return render_template('course_create.html')

    course_code = request.form.get('code', '').strip()
    course_name = request.form.get('c_name', '').strip()
    course_description = request.form.get('desc', '').strip()

    if not course_code or not course_name:
        flash('Course code and name are required.', 'error')
        return render_template('course_create.html'), 400

    existing_course = Course.query.filter_by(course_code=course_code).first()
    if existing_course:
        flash('Course with this code already exists.', 'warning')
        return render_template('course_exists.html')

    course = Course(course_code=course_code, course_name=course_name, course_description=course_description)
    db.session.add(course)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash('Database error when creating course. Possibly duplicate code.', 'error')
        return render_template('course_exists.html'), 500

    return redirect(url_for('courses'))


# alias for course detail endpoint: 'course_detail' (in case templates use that)
@app.route("/course/<int:course_id>/", endpoint='course_detail')
def course_details(course_id):
    course = get_course_or_404(course_id)
    return render_template('course_details.html', course=course)


@app.route("/course/<int:course_id>/update/", methods=["GET", "POST"])
def update_course(course_id):
    course = get_course_or_404(course_id)
    if request.method == 'GET':
        return render_template('course_update.html', course=course)

    course_name = request.form.get('c_name', '').strip()
    course_description = request.form.get('desc', '').strip()

    if not course_name:
        flash('Course name cannot be empty.', 'error')
        return redirect(url_for('course_detail', course_id=course.course_id))

    course.course_name = course_name
    course.course_description = course_description
    db.session.commit()
    flash('Course updated.', 'success')
    return redirect(url_for('courses'))


@app.route("/course/<int:course_id>/delete/", methods=["GET"])
def delete_course(course_id):
    course = get_course_or_404(course_id)
    enrollments = Enrollment.query.filter_by(ecourse_id=course_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('courses'))


if __name__ == '__main__':
    app.run(debug=True)
