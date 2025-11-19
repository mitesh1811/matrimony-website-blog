from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from models import db, Admin,Blog
from forms import LoginForm
from config import Config
import os
from models import Profile
from werkzeug.utils import secure_filename
from sqlalchemy import case, asc
from flask import current_app

app = Flask(__name__)
app.config.from_object(Config)

UPLOAD_FOLDER = 'static/blog_images'


db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))





@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/news')
def news():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template('news.html', blogs=blogs)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin)
            return redirect(url_for('dashboard'))
        flash('Invalid login')
    return render_template('login.html', form=form)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
@app.route('/add_blog', methods=['GET', 'POST'])
@login_required
def add_blog():
    if not current_user.is_master:
        flash("Access denied. Master admin only.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')
        image_filename = None

        if image and allowed_file(image.filename):

            filename = secure_filename(image.filename)
            upload_folder = current_app.config['BLOG_IMAGE_UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            image_filename = filename

        new_blog = Blog(title=title, content=content, image_filename=image_filename)
        db.session.add(new_blog)
        db.session.commit()
        flash("Blog posted successfully!")
        return redirect(url_for('dashboard'))

    return render_template('add_blog.html')
@app.route('/manage_blogs')
@login_required
def manage_blogs():
    if not current_user.is_master:
        flash("Access denied. Master admin only.")
        return redirect(url_for('dashboard'))

    blogs = Blog.query.order_by(Blog.id.desc()).all()
    print(blogs)
    return render_template('manage_blogs.html', blogs=blogs)

@app.route('/delete_blog/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    if not current_user.is_master:
        flash("Access denied. Master admin only.")
        return redirect(url_for('dashboard'))

    blog = Blog.query.get_or_404(blog_id)
    
    # Delete image file if exists
    if blog.image_filename:
        image_path = os.path.join(current_app.config['BLOG_IMAGE_UPLOAD_FOLDER'], blog.image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(blog)
    db.session.commit()
    flash("Blog deleted successfully!")
    return redirect(url_for('manage_blogs'))

@app.route('/edit_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    if not current_user.is_master:
        flash("Access denied. Master admin only.")
        return redirect(url_for('dashboard'))

    blog = Blog.query.get_or_404(blog_id)

    if request.method == 'POST':
        blog.title = request.form['title']
        blog.content = request.form['content']

        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['BLOG_IMAGE_UPLOAD_FOLDER'], filename)
            image.save(image_path)
            blog.image_filename = filename

        db.session.commit()
        flash("Blog updated successfully!")
        return redirect(url_for('manage_blogs'))

    return render_template('edit_blog.html', blog=blog)


@app.route('/dashboard')
@login_required
def dashboard():
    query = request.args.get('query', '').strip()
    
    if query:
        profiles = Profile.query.filter(
            (Profile.full_name.ilike(f'%{query}%')) |
            (Profile.phone == query)
        ).all()
    else:
        profiles = Profile.query.all()

    return render_template('dashboard.html', profiles=profiles, is_master=current_user.is_master)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

# Create admin (only for master admin)
@app.route('/admin/create', methods=['GET', 'POST'])
@login_required
def create_admin():
    if not current_user.is_master:
        return "Unauthorized", 403
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_admin = Admin(username=username, password=password, is_master='is_master' in request.form)
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin Created!')
        return redirect(url_for('dashboard'))
    return render_template('create_admin.html')


# Add Profile
@app.route('/add_profile', methods=['GET', 'POST'])
@login_required
def add_profile():
    if request.method == 'POST':
        full_name = request.form['name']  # assuming form input name="name"
        age = int(request.form['age'])
        caste = request.form['caste']
        gender = request.form['gender']
        location = request.form.get('location', '')  # optional

        photo_file = request.files['photo']
        filename = secure_filename(photo_file.filename)
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo_file.save(photo_path)

        profile = Profile(
            full_name=full_name,
            age=age,
            caste=caste,
            gender=gender,
            religion=request.form.get('religion'),
            mother_tongue=request.form.get('mother_tongue'),
            education=request.form.get('education'),
            occupation=request.form.get('occupation'),
            income=request.form.get('income'),
            diet=request.form.get('diet'),
            smoking=request.form.get('smoking'),
            drinking=request.form.get('drinking'),
            location=location,
            city=request.form.get('city'),
            state=request.form.get('state'),
            country=request.form.get('country'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            photo_filename=filename
        )

        db.session.add(profile)
        db.session.commit()
        flash('Profile added successfully!')
        return redirect(url_for('dashboard'))

    return render_template('add_profile.html')

@app.route('/edit_profiles', methods=['GET', 'POST'])
@login_required
def edit_profiles():
    search_name = ''
    search_phone = ''
    query = Profile.query

    if request.method == 'POST':
        search_name = request.form.get('search_name', '').strip()
        search_phone = request.form.get('search_phone', '').strip()

        if search_name:
            query = query.filter(Profile.full_name.ilike(f"%{search_name}%"))
        if search_phone:
            query = query.filter(Profile.phone == search_phone)

    profiles = query.all()

    return render_template('edit_profiles.html', profiles=profiles, search_name=search_name, search_phone=search_phone)


@app.route('/edit_profile/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    
    if request.method == 'POST':
        profile.full_name = request.form['full_name']
        profile.age = int(request.form['age'])
        profile.gender = request.form['gender']
        profile.caste = request.form.get('caste')
        profile.religion = request.form.get('religion')
        profile.mother_tongue = request.form.get('mother_tongue')
        profile.education = request.form.get('education')
        profile.occupation = request.form.get('occupation')
        profile.income = request.form.get('income')
        profile.diet = request.form.get('diet')
        profile.smoking = request.form.get('smoking')
        profile.drinking = request.form.get('drinking')
        profile.location = request.form.get('location')
        profile.city = request.form.get('city')
        profile.state = request.form.get('state')
        profile.country = request.form.get('country')
        profile.phone = request.form.get('phone')
        profile.email = request.form.get('email')

        # Optional photo update
        photo = request.files.get('photo')
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.static_folder, 'uploads', filename))
            profile.photo_filename = filename
        
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('edit_profiles'))

    return render_template('edit_profile.html', profile=profile)


@app.route('/profile/<int:profile_id>')
@login_required
def view_profile(profile_id):
    profile = Profile.query.get_or_404(profile_id)
    return render_template('view_profile.html', profile=profile)



@app.route('/search_profiles', methods=['GET', 'POST'])
@login_required
def search_profiles():
    results = []
    if request.method == 'POST':
        query = Profile.query

        # Get all form values
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        caste = request.form.get('caste')
        religion = request.form.get('religion')
        gender = request.form.get('gender')
        occupation = request.form.get('occupation')
        min_income = request.form.get('min_income')
        max_income = request.form.get('max_income')
        diet = request.form.get('diet')
        drinking = request.form.get('drinking')
        smoking = request.form.get('smoking')
        city = request.form.get('city')
        min_age = request.form.get('min_age')
        max_age = request.form.get('max_age')

        # Dynamically add filters if fields are filled
        if full_name:
            query = query.filter(Profile.full_name.ilike(f"%{full_name}%"))
        if phone:
            query = query.filter(Profile.phone.ilike(f"%{phone}%"))
        if caste:
            query = query.filter(Profile.caste == caste)
        if religion:
            query = query.filter(Profile.religion == religion)
        if gender:
            query = query.filter(Profile.gender == gender)
        if occupation:
            query = query.filter(Profile.occupation == occupation)
        if min_income:
            query = query.filter(Profile.income >= min_income)
        if max_income:
            query = query.filter(Profile.income <= max_income)
        if diet:
            query = query.filter(Profile.diet == diet)
        if drinking:
            query = query.filter(Profile.drinking == drinking)
        if smoking:
            query = query.filter(Profile.smoking == smoking)
        if city:
            query = query.filter(Profile.city == city)
        if min_age:
            query = query.filter(Profile.age >= int(min_age))
        if max_age:
            query = query.filter(Profile.age <= int(max_age))

        results = query.all()

    return render_template('search_profiles.html', results=results)


@app.route('/find_match/<int:profile_id>', methods=['GET', 'POST'])
@login_required
def find_match(profile_id):
    base_profile = Profile.query.get_or_404(profile_id)
    results = []

    # Defaults
    caste = base_profile.caste
    min_age = base_profile.age - 3
    max_age = base_profile.age + 3
    religion = occupation = diet = drinking = smoking = city = ""
    min_income = max_income = ""
    use_filters = False

    if request.method == 'POST':
        use_filters = 'use_filters' in request.form
        caste = request.form.get('caste', '').strip()
        religion = request.form.get('religion', '').strip()
        occupation = request.form.get('occupation', '').strip()
        diet = request.form.get('diet', '').strip()
        drinking = request.form.get('drinking', '').strip()
        smoking = request.form.get('smoking', '').strip()
        city = request.form.get('city', '').strip()

        min_age = int(request.form.get('min_age') or min_age)
        max_age = int(request.form.get('max_age') or max_age)
        min_income = request.form.get('min_income', '').strip()
        max_income = request.form.get('max_income', '').strip()

    query = Profile.query.filter(
        Profile.id != base_profile.id,
        Profile.gender != base_profile.gender
    )

    if use_filters:
        if caste:
            query = query.filter(Profile.caste == caste)
        if religion:
            query = query.filter(Profile.religion == religion)
        if occupation:
            query = query.filter(Profile.occupation == occupation)
        if diet:
            query = query.filter(Profile.diet == diet)
        if drinking:
            query = query.filter(Profile.drinking == drinking)
        if smoking:
            query = query.filter(Profile.smoking == smoking)
        if city:
            query = query.filter(Profile.city == city)
        if min_income.isdigit():
            query = query.filter(db.cast(Profile.income, db.Integer) >= int(min_income))
        if max_income.isdigit():
            query = query.filter(db.cast(Profile.income, db.Integer) <= int(max_income))
        query = query.filter(Profile.age >= min_age, Profile.age <= max_age)

    # Order: caste match, occupation match, then age diff
    query = query.order_by(
        case((Profile.caste == base_profile.caste, 0), else_=1),
        case((Profile.occupation == base_profile.occupation, 0), else_=1),
        db.func.abs(Profile.age - base_profile.age)
    )

    profiles = query.all()

    for profile in profiles:
        profile.match_caste = profile.caste == base_profile.caste
        profile.match_occupation = profile.occupation == base_profile.occupation
        profile.age_diff = abs(profile.age - base_profile.age)

    return render_template(
        'find_match.html',
        base=base_profile,
        results=profiles,
        caste=caste,
        religion=religion,
        occupation=occupation,
        diet=diet,
        drinking=drinking,
        smoking=smoking,
        city=city,
        min_income=min_income,
        max_income=max_income,
        min_age=min_age,
        max_age=max_age,
        use_filters=use_filters
    )

if __name__ == '__main__':
    app.run(debug=True)