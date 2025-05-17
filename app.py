from flask import Flask,render_template,redirect,flash,url_for,request
from flask_migrate import Migrate 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin,LoginManager,login_user,login_required,logout_user,current_user
from form import myForm,loginform,image_saveform,Userprofile_pic
from datetime import timedelta,datetime
import os



app=Flask(__name__)



app.config['SECRET_KEY']='AMAZON'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
#database pic save
#save in image folder
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), 'static/image'))
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#save in user_product folder
USER_PRODUCT_FOLDER = os.path.join('static','user_product')
app.config['USER_PRODUCT_FOLDER'] = os.path.abspath(USER_PRODUCT_FOLDER)
#user profile_pic
app.config['USER_PIC_FOLDER']=os.path.join("static","profile pic")
# FOR COOKIE
app.config['REMEMBER_COOKIE_DURATION']=timedelta(days=30)
#allowed extentions
app.config['ALLOWED_EXTENSTIONS']=set(['png','jpg','jpeg','gif'])
login_manger=LoginManager(app)

login_manger.login_view='login'
db=SQLAlchemy(app)
migrate=Migrate(app,db)




class user(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email=db.Column(db.String(200),nullable=False)
    password=db.Column(db.String(200),nullable=False)
    product=db.relationship('user_product',backref='product',lazy=True)
    faild_login_attempt=db.Column(db.Integer,nullable=True,default=0)
    login_lock=db.Column(db.DateTime,nullable=True)

    
    def __repr__(self):
     return f"User('{self.name}', '{self.email}')"
    

class image_save(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    image = db.Column(db.String(200), default='default.jpg')

class user_product(db.Model):
    __tablename__ = 'user_product'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_price=db.Column(db.String(200),nullable=False)
    product_name=db.Column(db.String(200),nullable=False)
    product_pic = db.Column(db.String(200), default='default.jpg')



class cartitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_price=db.Column(db.String(200),nullable=False)
    product_name=db.Column(db.String(200),nullable=False)
    product_pic = db.Column(db.String(200), default='default.jpg')
    quantity = db.Column(db.Integer, default=1)

class Profile_pic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profile_pic = db.Column(db.String(200), default='default.jpg')


with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in app.config['ALLOWED_EXTENSTIONS']



@login_manger.user_loader
def user_load(user_id):
    return user.query.get(user_id)

@app.route('/')
def index():
    return redirect('/login')



@app.route('/register',methods=['GET','POST'])
def register():
    form = myForm() 
   
    if form.validate_on_submit():
        if user.query.filter_by(email=form.email.data).first():
            flash('Email already taken!')
        else:
          hashed_password = generate_password_hash(form.password.data)
          new_user=user(email=form.email.data,name=form.name.data,password=hashed_password)
        
          db.session.add(new_user)
          db.session.commit()
          return redirect('/login')
    return render_template('register.html',form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform()

    if form.validate_on_submit():
        user_instance = user.query.filter_by(email=form.login_email.data).first()

        if user_instance:
            # Account lock check
            if user_instance.login_lock and datetime.utcnow() < user_instance.login_lock:
                flash('Your account is locked. Please try again later.', 'danger')
                return redirect(url_for('login'))

            # Correct password
            if check_password_hash(user_instance.password, form.login_password.data):
                user_instance.faild_login_attempt = 0
                user_instance.login_lock = None  # clear lock if it was set
                db.session.commit()
                login_user(user_instance, remember=True)
                return redirect(url_for('dashboard', id=user_instance.id))
            else:
                # Wrong password
                if user_instance.faild_login_attempt is None:
                    user_instance.faild_login_attempt = 0

                user_instance.faild_login_attempt += 1

                if user_instance.faild_login_attempt >= 3:
                    user_instance.login_lock = datetime.utcnow() + timedelta(minutes=5)
                    flash('Your account is locked for 5 minutes.', 'danger')
                else:
                    flash('Incorrect password. Please try again.', 'warning')

                db.session.commit()
                return redirect(url_for('login'))

        else:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')

        file = request.files.get('product_pic')
        if file and allowed_file(file.filename):
            filename = file.filename
        

            if not os.path.exists(app.config['USER_PRODUCT_FOLDER']):
                os.makedirs(app.config['USER_PRODUCT_FOLDER'])

            file_path = os.path.join(app.config['USER_PRODUCT_FOLDER'], filename)
            file.save(file_path)

            product_image = user_product(
                user_id=current_user.id,
                product_name=product_name,
                product_price=product_price,
                product_pic=filename 
            )
            db.session.add(product_image)
            db.session.commit()
        else:
            flash('only png,jpg,jpeg,gif,file alowed')
 
    products = user_product.query.filter_by().order_by(user_product.id.desc()).all()
    return render_template('dashboard.html', user=current_user, products=products)



@app.route('/search')
def search():
    query = request.args.get('query', '')

    results = user_product.query.filter(user_product.product_name.ilike(f"%{query}%")).all()

    return render_template('search_results.html', results=results, query=query)




@app.route('/Profile', methods=['POST', 'GET'])
@login_required
def Profile():
    image_form=image_saveform()
    userprofile_pic_form=Userprofile_pic()
    if image_form.validate_on_submit():
        if image_form and allowed_file(image_form.product_pic.data.filename):
            filename=image_form.product_pic.data.filename 
            filepath=os.path.join(app.config['USER_PRODUCT_FOLDER'],filename)
            image_form.product_pic.data.save(filepath)

            product_image = user_product(
                user_id=current_user.id,
                product_name=image_form.product_name.data,
                product_price=image_form.product_price.data,
                product_pic = filename 
            )
            
            db.session.add(product_image)
            db.session.commit()

    


    picture=Profile_pic.query.filter_by(user_id=current_user.id).order_by(Profile_pic.id.desc()).first()
    user_image = image_save.query.filter_by(user_id=current_user.id).order_by(image_save.id.desc()).first()
    user_product_pic=user_product.query.filter_by(user_id=current_user.id).order_by(user_product.id.desc()).all()
    
    return render_template('Profile.html',
                              user=current_user,
                              user_image=user_image,
                              form=image_form,
                              picture=picture,
                              profile_pic_form=userprofile_pic_form,
                              user_product_pic=user_product_pic
                              )






@app.route('/addprofilepic', methods=['POST', 'GET'])
@login_required
def addprofilepic():
    userprofile_pic_form = Userprofile_pic()

    if userprofile_pic_form.validate_on_submit():
        file = userprofile_pic_form.userprofile_pic.data
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['USER_PIC_FOLDER'], filename)

           
            existingpics = Profile_pic.query.filter_by(profile_pic=filename).all()

            for pic in existingpics:
                oldpath = os.path.join(app.config['USER_PIC_FOLDER'], pic.profile_pic)
                print("Trying to delete:", oldpath)

                if os.path.exists(oldpath):
                    os.remove(oldpath)
                    print("Deleted:", oldpath)
                else:
                    print("Not found:", oldpath)

                db.session.delete(pic)

            db.session.commit()

           
            file.save(filepath)
            new_pic = Profile_pic(user_id=current_user.id, profile_pic=filename)
            db.session.add(new_pic)
            db.session.commit()

    return redirect('/Profile')



@app.route('/EditProfile/<int:id>/edit',methods=['GET','POST'])
@login_required
def EditProfile(id):
    new_user=user.query.get(id)
    form =myForm(object=new_user)
    if form.validate_on_submit():
        new_user.name=form.name.data
        db.session.commit()
        return redirect('/Profile')

    return render_template('EditProfile.html',form=form,new_user=new_user)
 



@app.route('/add_to_cart/<int:id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(id):
    

    product = user_product.query.get(id)
    if product:
      existing_item=cartitem.query.filter_by(user_id=current_user.id,product_name=product.product_name).first()
      if existing_item:
      
       existing_item.quantity += 1 
       db.session.commit() 
      else:
       new_add_to_cart=cartitem(user_id=current_user.id,
                                
                                product_name=product.product_name,
                                product_price=product.product_price,
                                product_pic=product.product_pic
                                ) 
       db.session.add(new_add_to_cart)
       db.session.commit()

    return '', 204




@app.route('/cart', methods=['GET'])
@login_required
def cart():
    
    
    cart_item=cartitem.query.filter_by(user_id=current_user.id).all()
    

    return render_template('cart.html', cart_items=cart_item)


@app.route('/update_cart_item/<int:item_id>',methods=['POST','GET'])
def update_cart_item(item_id):
    action= request.form.get('action')
    item =cartitem.query.get_or_404(item_id)
    if action == 'decrease':
        item.quantity -=1
        print(item.quantity)
        
    elif action == 'increase':
        item.quantity +=1
    
    db.session.commit()    

    return '',204







@app.route('/remove_from_cart<int:item_id>',methods=['POST','GET'])
def remove_from_cart(item_id):
    remove_item=cartitem.query.get(item_id)
    if remove_item:
        db.session.delete(remove_item)
        db.session.commit()
    
    return '',204




@app.route('/checkout',methods=['POST','GET'])
@login_required
def checkout():
    cart_item=cartitem.query.filter_by(user_id=current_user.id).all()
    total=0
    if not cart_item:
        flash('noting in cart')
    else:
        total=sum(float(item.product_price) * item.quantity for item in cart_item)
    return render_template('checkout.html',total=total)  







@app.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404















if __name__ == '__main__':
    app.run(debug=True)