from django.shortcuts import render
from django.http import Http404
from .models import Post, Author, subscribe, Contact, Comment, SubComment
import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.models import auth
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required


def index(request):
	if request.method == 'GET':
		email = request.GET.get('email')
		if email:
			subscribe(email=email).save()
	week_ago = datetime.date.today() - datetime.timedelta(days = 7)
	trends = Post.objects.filter(time_upload__gte = week_ago).order_by('-read')
	TopAuthors =Author.objects.order_by('-rate')[:2]
	AuthorsPost = [Post.objects.filter(auther = author).first() for author in TopAuthors]

	all_post = Paginator(Post.objects.filter(publish = True),7)
	page = request.GET.get('page')
	try:
		posts = all_post.page(page)
	except PageNotAnInteger:
		posts = all_post.page(1)
	except EmptyPage:
		posts = all_post.page(all_post.num_pages)

	parms = {
		'posts': posts,
		'trends': trends[:2],
		'author_post':AuthorsPost,
		'pop_post': Post.objects.order_by('-read')[:2],
		'recent_post' : Post.objects.order_by('-time_upload')[:2],
	}
	return render(request, 'index.html', parms)


@login_required
def profile(request):
	user = request.user
	if user is None:
		return redirect('login')
	else:
		parms = {
            'user':user,
			'recent_post' : Post.objects.order_by('-time_upload')[:2]
        }
	return render(request, 'profile.html',parms)


def about(request):
	parms = {
		'title': 'About | Gyanism',
		'pop_post': Post.objects.order_by('-read')[:2],
        'recent_post' : Post.objects.order_by('-time_upload')[:2],
		}
	return render(request, 'about.html', parms)


def post(request, id, slug):
    try:
        post = Post.objects.get(pk=id, slug=slug)
    except:
        raise Http404("Post Does Not Exist")

    post.read += 1
    post.save()

    if request.method == 'POST':
        comm = request.POST.get('comm')
        comm_id = request.POST.get('comm_id')  # None

        if comm_id:
            SubComment(post=post,
                       user=request.user,
                       comm=comm,
                       comment=Comment.objects.get(id=int(comm_id))
                       ).save()
        else:
            Comment(post=post, user=request.user, comm=comm).save()

    comments = []
    for c in Comment.objects.filter(post=post):
        comments.append([c, SubComment.objects.filter(comment=c)])

    post_author = post.auther
    if str(post_author) == 'palak':
        post_para = 'Hello fellas , Im Palak Shivlani.A tech enthusiast and developer always open to exploring new fields.A person who believes truth always prevails.'
        author_image = '/static/images/Palak.jpg'
    elif str(post_author) == 'Parmeshwar':
        post_para = "It’s me Parmeshwar Kumar Sahu.A tech learner, analyzer and a code freak.As, Student is more important than a teacher likewise learner learning is important than teaching."
        author_image = '/static/images/Parmeshwar.jpg'
    else:
        post_para = 'Sorry, I like to stay anonymous. Read the blog and enjoy'
        author_image = '/static/images/profile.png'

    parms = {
        'comments': comments,
        'post_author': post_author,
        'post': post,
        'post_para': post_para,
        'author_image': author_image,
        'pop_post': Post.objects.order_by('-read')[:2],
        'recent_post' : Post.objects.order_by('-time_upload')[:2]
    }
    return render(request, 'blog-single.html', parms)



def contact(request):
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')
		mob = request.POST.get('mob')
		mess = request.POST.get('mess','default')
		Contact(name=name,email=email,mob=mob,mess=mess).save()
	parms = {
		'title': 'Contact | Gyanism',
		'pop_post': Post.objects.order_by('-read')[:2],
		'recent_post' : Post.objects.order_by('time_upload')[:2]
		}
	return render(request, 'contact.html', parms)


def search(request):
	q = request.GET.get('q')
	if q is None:
		q = ' '
	posts = Post.objects.filter(
		Q(title__icontains = q) |
		Q(overview__icontains = q) 
		).distinct()

	parms = {
		'posts':posts,
		'title':'Search Results',
        'recent_post' : Post.objects.order_by('-time_upload')[:2]
		}

	return render(request, 'search.html', parms)


