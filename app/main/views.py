from flask import render_template,redirect,url_for,abort,flash,request
from .. import db
from . import main
from flask_login import login_required,current_user
from ..models import User,Blog,Comment,Quote
from .forms import UpdateProfileForm,CommentForm,PostForm
from ..picture_handler import add_profile_pic
from ..request import get_quotes


#views
@main.route('/')
def index():
    '''
    view root function that returns index page and its data
    '''
    posts=BlogPost.get_posts()
    # qquote=get_quotes()
    # quote=reloadapi()
    quote=get_quotes()
    return render_template('index.html',title='Home of the brave',posts=posts,user=current_user,quote=quote)



@main.route('/user/<uname>')
def profile(uname):
    '''
    view function to see a single user profile
    '''
    user=User.query.filter_by(username=uname).first()

    if user is None:
        abort(404)

    return render_template('profile/profile.html',user=user)

    
@main.route('/user/<uname>/profile_update',methods=['GET','POST'])
@login_required
def profile_update(uname):
    '''
    view function to updtae a user profile
    '''
    user=User.query.filter_by(username=uname).first()
    if user is None:
        abort(404)
    
    print(user)    

    
    form=UpdateProfileForm()

    if form.validate_on_submit():
        
        if form.pictures.data:
            pic=add_profile_pic(form.pictures.data,user.username)
            current_user.profile_image=pic
        user.username=form.username.data
        user.email=form.email.data

        db.session.add(user) 
        db.session.commit() 

        return redirect(url_for('main.profile',uname=user.username)) 

    elif request.method=='GET':
        #user is not submitting anything
        #set form field to the current users details
        form.username.data=current_user.username
        form.email.data=current_user.email
    
    #fetch the current profile image from the static folder and inject to the template    
    profile_image=url_for('static',filename='photos/'+user.profile_image)  
    return render_template('profile/update_profile.html',profile_image=profile_image,form=form)  


@main.route('/<uname>/blogposts')
def user_posts(uname):
    '''
    View function that displays all blog posts for a single user
    '''
    #cycle through user posts using pages e.g if user has 40 posts we dont display all in one page
    page=request.args.get('page',1,type=int)

    #grab user if he/she exists or return 404
    user=User.query.filter_by(username=uname).first_or_404()

    #grab posts by the specified user 
    blogs=Blog.get_user_posts(user ,page)

    title=f'{uname}-blogs'
    return render_template('user_blogs.html',blogs=blogs,user=user,title=title)


@main.route('/create',methods=['GET','POST'])
@login_required
def create_post():
    '''
    View function to create a blog post
    '''
    form=PostForm()

    if form.validate_on_submit():
        post=Blog(title=form.title.data,text=form.text.data,user_id=current_user.id)

        post.save_post()
        flash('Blog Post Created')
        return redirect(url_for('main.index'))

    return render_template('create_post.html',form=form)

@main.route('/post/<int:blog_post_id>')
def single_blogpost(blog_post_id):
    '''
    View function to view one blog post
    '''
    blog_post=BlogPost.query.get_or_404(blog_post_id)
    comments=Comment.get_comments(blog_post_id)
    return render_template('blogpost.html',title=blog_post.title,blog_post=blog_post,comments=comments)    



@main.route('/post/<int:blog_post_id>/update',methods=['GET','POST'])
@login_required
def update_post(blog_post_id):
    '''
    View function to update a blogpost
    '''
    blog_post=BlogPost.query.get_or_404(blog_post_id)

    if blog_post.author !=current_user:
        #if the viewer is not the owner of the post
        #dont allow
        abort(403)
    
    form=PostForm()
    if form.validate_on_submit():
        blog_post.title=form.title.data
        blog_post.text=form.text.data

        db.session.commit()
        flash('Blog Updated')
        return redirect(url_for('main.single_blogpost',blog_post_id=blog_post.id))

    elif request.method=='GET':

        #fill the form with the post details if user has not editted 
        form.title.data=blog_post.title
        form.text.data=blog_post.text

    return render_template('create_post.html',title='Update Post',form=form)    


@main.route('/post/<int:blog_post_id>/delete',methods=['GET','POST'])
@login_required
def delete_post(blog_post_id):
    '''
    View function to delete a post
    '''
    blog_post=BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
        
    db.session.delete(blog_post)
    db.session.commit()
    flash('Blog Deleted')
    
    return redirect(url_for('main.index'))


@main.route('/blog/comment/new/<int:blog_post_id>',methods=['GET','POST'])
@login_required
def new_comment(blog_post_id):
    '''
    View function that returns a form to create a comment post
    ''' 
    post=BlogPost.query.filter_by(id=blog_post_id)
    form=CommentForm()

    if form.validate_on_submit():
        comment_content=form.comment_content.data
        new_comment=Comment(comment_content=comment_content,post_id=blog_post_id,user_id=current_user.id)

        new_comment.save_comment()
        return redirect(url_for('main.single_blogpost',blog_post_id=blog_post_id))

    return render_template('new_comment.html',title='New Comment',form=form)   


@main.route('/<int:blog_post_id>/comment/<int:comment_id>/delete',methods=['GET','POST'])
@login_required
def delete_comment(blog_post_id,comment_id):
    '''
    View function to delete a post
    '''
    comment=Comment.query.get(comment_id)
    blog_post=BlogPost.query.get_or_404(blog_post_id)
    if blog_post.author != current_user:
        abort(403)
        
    db.session.delete(comment)
    db.session.commit()
    
    return redirect(url_for('main.single_blogpost',blog_post_id=blog_post_id))    
