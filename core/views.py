from django.shortcuts import render,redirect
from django.views import generic
from django.views.generic import View
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from .forms import UserForm,UpdateUserForm,UpdateProfileForm,CreatePost,CreateComment
from django.http import HttpResponse 
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import User,Following,Follower,Post,Profile
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.hashers import make_password
import itertools
import re





def validate_pass(password: str):

    # Regex pattern for password at least 8 charapters, one uppercase, one lower case, one digit

    pattern = r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$"

    # se if the password has this pattern
    match = re.match(pattern, password)

    # return True if the password matches the pattern, False otherwise
    return bool(match)

def verify_input_fields(username,password):
	error = []
	if len(username) < 4:
		error.append('Username Should At Least Be 4 Character Long')

	elif validate_pass(password) == False:
		error.append('Password match the following pattern \n at least 8 charapters \n at least 1 uppercase \n at least 1 lowercase \n at least one digit')
	else:
		print('OK')

	return error
	


def register_user(request):

	#get the values from the registration form if the method is post
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']

		#make the password more secure
		hashed_password = make_password(password)

		#verify the autheticity of the username and password
		error = verify_input_fields(username,password)

		#check if there are errors
		if len(error) != 0:
			error = error[0]
			print(error)
			return render(request, 'registration_form.html', {'error': error})
		else:
			#save user data
			a = User(username=username, email=email, password=hashed_password)
			if a.DoesNotExist():
				a.save()
			else:
				messages.error("Account already exists")
				error.append("Account already exists")
				return render(request, 'registration_form.html', {'error': error})

			user = User.objects.get(username=username)
			user_id = User.objects.values_list('id', flat=True).filter( username = user)
			print('User id',user_id)
			Profile.objects.create(user_id=user_id)
			messages.success(request, 'Account Was Created Successfully')
			return redirect('register')
	else:
		return render(request, 'registration_form.html')

@login_required(login_url='/')
def logout(request):
    auth.logout(request)
    return redirect('login')

def login(request):
	#get the values from the registration form if the method is post
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		
		#authenticate
		user = authenticate(request, username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request,user)
			return redirect('welcome')
		else:
			messages.info(request, 'Invalid Username or Password')
			return redirect('login')
	else:
		return render(request, 'login.html')


@login_required(login_url='/')
def feed(request):
	try:
		#order posts by creatin date
		post_all = Post.objects.all().order_by('created_at')
		print(post_all)
	except Exception as e:
		print(e)

	#get commments
	comment_form = CreateComment()
	username = request.user.username


	context = {
	'post_all': post_all,
	'comment_form': comment_form,
	'username': username,
	}

	return render(request, 'feed.html', context)


@login_required(login_url='/')
def follow(request, username):
	#check if the user we are viewing is different from the current one
	if request.user.username != username:
		if request.method == 'POST':
			#get the data of the user that is currently logged in
			follower = User.objects.get(username=request.user.username)

			#get the data of the user that we are currently viewing
			target = User.objects.get(username=username)
			
			#add the the datatabase the followed
			target.follower_set.create(follower_user = follower)

			#add the the datatabase the followi
			follower.following_set.create(following_user = target)
			url = reverse('profile', kwargs = {'username' : username})
			return redirect(url)



@login_required(login_url='/')
def unfollow(request, username):
	if request.method == 'POST':
		#get the data of the users
		follower = User.objects.get(username=request.user.username)
		target = User.objects.get(username=username)
		
		#delete from the database the followed
		target.follower_set.get(follower_user = follower).delete()
		follower.following_set.get(following_user = target).delete()
		url = reverse('profile', kwargs = {'username' : username})
		return redirect(url)

@login_required(login_url='/')
def post(request, username):
	if request.method == 'POST':
		#create a new post form with the data from request
		post_form = CreatePost(request.POST, request.FILES)

		#check if the data is valid
		if post_form.is_valid():

			
			post_text = post_form.cleaned_data['post_text']
			post_picture = post_form.cleaned_data['post_picture']
			request.user.post_set.create(post_text=post_text, post_picture=post_picture)
			messages.success(request, f'{username}Post was created with success!!!!!')

	url = reverse('profile', kwargs={'username':username})
	return redirect(url)


@login_required(login_url='/')
def comment(request, username, post_id):
	if request.method == 'POST':
		#get the comment data
		comment_form = CreateComment(request.POST)
		
		#check if its valid
		if comment_form.is_valid():
			comment_text = comment_form.cleaned_data['comment_text']

			user =User.objects.get(username=username)
			post = user.post_set.get(pk=post_id)

			#add comment data to database
			post.comment_set.create(user=request.user, comment_text=comment_text)
			messages.success(request, f'{user} Comment was created successfully!!!!')

	url = reverse('profile', kwargs={'username':username})
	return redirect(url)
	
#returns a dictionary of validated form input fields and their values, where string primary keys are returned as objects


@login_required(login_url='/')
def search(request):
  
    query = request.GET['q']
    print(query)
    data = query

    count = {}
    results = {}
    results['posts']= User.objects.none()

    queries = data.split()
    for query in queries:
        results['posts'] = results['posts'] | User.objects.filter(username__icontains=query)
        count['posts'] = results['posts'].count()


    # count2 = {}
    # queries2 = data.split()
    # results2 = {}
    # results2['posts'] = User.objects.none()
    # queries2 = data.split()
    # for query2 in queries:
    #     results2['posts'] = results2['posts'] | User.objects.filter(first_name__icontains=query2)
    #     count2['posts'] = results2['posts'].count()


    # count3 = {}
    # queries3 = data.split()
    # results3 = {}
    # results3['posts'] = User.objects.none()
    # queries3 = data.split()
    # for query3 in queries:
    #     results3['posts'] = results3['posts'] | User.objects.filter(last_name__icontains=query3)
    #     count3['posts'] = results3['posts'].count()
        

    files = results['posts']
    result = []
    for i in files:
        if i not in result:
            result.append(i)    

    paginate_by=2
    username = request.user.username
    print('current user',username)
    person = User.objects.get(username = username)
    print('person',person)
	
    context={ 'files':result }
	
    return render(request,'search.html',context)




@login_required(login_url='/')
def profile(request, username):
	
	if request.method == 'POST':
		#form of an external profile
		u_form = UpdateUserForm(request.POST,instance=request.user)
		#form of the current profile
		p_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)
		

		
		if u_form.is_valid() and p_form.is_valid():

			#save the data that has been sent
			u_form.save()
			p_form.save()
			

			messages.success(request,f'{username} Profile has been updated!')
			url = reverse('profile', kwargs = {'username' : username})
			return redirect(url)

	else:
		
		if username == request.user.username:
			u_form = UpdateUserForm(instance=request.user)
			p_form = UpdateProfileForm(instance=request.user.profile)
			post_form = CreatePost()
			person = User.objects.get(username = username)

			context = {
					'u_form':u_form,
					'p_form':p_form,
					'post_form':post_form,
					'person':person,
					
			}	
		else:
			person = User.objects.get(username = username)
			already_a_follower=0
			for followers in person.follower_set.all():
				if (followers.follower_user ==  request.user.username):
					already_a_follower=1
					break

			if already_a_follower==1:
				context = {
						'person':person,
					}
			else:
				context = {
						'person':person,
						'f':1,
					}
		comment_form = CreateComment()
		context.update({'comment_form':comment_form})

	return render(request, 'profile.html', context)



@login_required(login_url='/')
def welcome(request):
	url = reverse('profile', kwargs = {'username' : request.user.username})
	return redirect(url)

