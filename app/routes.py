from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Course, Enrollment, User

main = Blueprint('main', __name__)


# HOME PAGE
@main.route('/')
def home():
    courses = Course.query.all()
    return render_template('home.html', courses=courses)


# COURSES PAGE
@main.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)


# SINGLE COURSE PAGE
@main.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_detail.html', course=course)


# ENROLL IN COURSE
@main.route('/enroll/<int:course_id>')
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)

    # Check if already enrolled
    existing = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()

    if existing:
        flash('You are already enrolled!', 'info')
    else:
        enrollment = Enrollment(
            user_id=current_user.id,
            course_id=course_id
        )
        db.session.add(enrollment)
        db.session.commit()
        flash('Successfully enrolled!', 'success')

    return redirect(url_for('main.course_detail', course_id=course_id))


# STUDENT DASHBOARD
@main.route('/dashboard')
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(
        user_id=current_user.id
    ).all()
    return render_template('dashboard.html', enrollments=enrollments)


# ADMIN DASHBOARD
@main.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.home'))

    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    courses = Course.query.all()
    users = User.query.all()

    return render_template('admin.html',
                           total_users=total_users,
                           total_courses=total_courses,
                           total_enrollments=total_enrollments,
                           courses=courses,
                           users=users
                           )


# ADD COURSE (ADMIN ONLY)
@main.route('/admin/add-course', methods=['GET', 'POST'])
@login_required
def add_course():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        video_url = request.form.get('video_url')

        course = Course(
            title=title,
            description=description,
            video_url=video_url
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('add_course.html')


# DELETE COURSE (ADMIN ONLY)
@main.route('/admin/delete-course/<int:course_id>')
@login_required
def delete_course(course_id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('main.home'))

    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted!', 'success')
    return redirect(url_for('main.admin_dashboard'))