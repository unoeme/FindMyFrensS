from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from .models import Message, Comment, User, Follow
from django.contrib import messages
import bcrypt
from django.core import serializers
from django.utils import timezone
from django.db.models import Count
import os





# Create your views here.
def index(request):
   
    context = {
        'users': User.objects.all().annotate(num_followers=Count('followings')).order_by('-num_followers') [:15],
        'current': User.objects.get(id = request.session['id'])
    }
    return render(request,'user/users.html', context)

def createuser(request):
    if request.method == "POST":
        errors = User.objects.reg(request.POST)
        email = request.POST['email']
        first = request.POST['first_name']
        current = request.POST['current']
        backup = request.POST['backup']
        passw= request.POST['password']
        level= request.POST['user_level']
        if email or first:
            request.session['email'] = email
            request.session['first_name'] = first
        if len(errors):
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return redirect('/users/create')
        else:
            pw_hash = bcrypt.hashpw(passw.encode(), bcrypt.gensalt())  
            a = User(first_name=first, current = current,backup = backup, email = email, password = pw_hash, user_level = level)
            a.save()
            return redirect('/users/')
    else:
        return redirect('/users/create')
def create(request):
    if 'id' not in request.session:
        return redirect('/')
    if User.objects.get(id=request.session['id']).user_level < 1:
        return redirect('/')
    return render(request,'user/usercreate.html')

def user(request, number):
    context = {
        'user': User.objects.get(id=number),
        'range': [1,2,3,4,5],
        'mymessages': reversed(Message.objects.filter(page= number)),
        'comments': Comment.objects.filter(page= number),
        'followers' : Follow.objects.filter(following = number).count(),
        'followings' : Follow.objects.filter(follower = number).count(),
        'isfollowing' : Follow.objects.filter(follower=request.session['id']).filter(following=number),
    }
    return render(request,'user/user.html', context)

def edit(request, number):
    if 'id' not in request.session:
        return redirect('/')
    if request.session['id'] != int(number): 
        if User.objects.get(id=request.session['id']).user_level < 1: 
            return redirect('/users/'+number)
    context = {
        'user': User.objects.get(id=number),
        'current': User.objects.get(id = request.session['id'])
    }
    return render(request,'user/useredit.html', context)

def update(request, number):
    errors = User.objects.update(request.POST, number)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/users/'+number+'/edit')
    if request.method == "POST":
        b = User.objects.get(id=number)
        b.first_name=request.POST['first_name']
        if b.current != request.POST['current']:
            text = b.first_name+" "+b.current+" changed their @ to "+request.POST['current']
            Message.objects.create(text=text,poster=User.objects.get(id=request.session['id']), page = User.objects.get(id=number))
        b.current=request.POST['current']
        if b.backup != request.POST['backup']:
            text = b.first_name+" "+b.current+" changed their backup @ to "+request.POST['backup']
            Message.objects.create(text=text,poster=User.objects.get(id=request.session['id']), page = User.objects.get(id=number))
        b.backup=request.POST['backup']
        b.email=request.POST['email']
        b.description = request.POST['description']
        b.updated_at = datetime.now()
        b.save()
        return redirect('/users/'+number)
    else:
        return redirect('/')

def makeadmin(request,number):
    if request.method == "POST":
        b = User.objects.get(id=number)
        b.user_level = request.POST['user_level']
        b.save()
        return redirect('/users/'+number)
    else:
        return redirect('/')

def verify(request,number):
    if request.method == "POST":
        b = User.objects.get(id=number)
        b.verified = request.POST['verified']
        b.save()
        return redirect('/users/'+number)
    else:
        return redirect('/')
    
def verifyme(request, number):
    if 'id' not in request.session:
        return redirect('/')
    if request.session['id'] != int(number): 
        if User.objects.get(id=request.session['id']).user_level < 1: 
            return redirect('/users/'+number)
    context = {
        'user': User.objects.get(id=number),
        'current': User.objects.get(id = request.session['id'])
    }
    return render(request,'user/verify.html', context)

def verifytest(request,number):
    # if request.method == "POST":
    #     url = request.POST["tweet"]
    #     values = {'s':'basics','submit':'search'}
    #     data = urllib.parse.urlencode(values)
    #     data = data.encode('utf-8')
    #     req = urllib.request.Request(url,data)
    #     resp = urllib.request.urlopen(req)
    #     respData = resp.read()
    #     # print(respData)
    #     paragraphs = re.findall(r'<p(.*?)</p>',str(respData))
    #     for p in paragraphs:
    #         print(p)
    #     b = User.objects.get(id=number)
    #     b.verified = 1
    #     b.save()

    #     driver = webdriver.Firefox()
    #     driver.get(url)
    #     time.sleep(5)
    #     htmlSource = driver.page_source
    #     return redirect('/users/'+number)
    return

def updatepassword(request, number):
    errors = User.objects.updatepassword(request.POST)
    if len(errors):
        for key, value in errors.items():
            messages.error(request, value, extra_tags=key)
        return redirect('/users/create')
    if request.method == "POST":
        pw_hash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())  
        b = User.objects.get(id=number)
        b.password=pw_hash
        b.updated_at = datetime.now()
        b.save()
        return redirect('/users/'+number)
    else:
        return redirect('/')
def delete(request, number):
    b = User.objects.get(id=number)
    b.delete()
    if User.objects.get(id=request.session['id']).user_level >0:
        return redirect('/users')
    request.session.clear()
    return redirect('/')


def message(request, number):
    if request.method == 'POST':
        errors = Message.objects.message(request.POST)
        if len(errors):
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return HttpResponse("")
        else:
            Message.objects.create(text=request.POST['messagebox'],poster=User.objects.get(id=request.session['id']), page = User.objects.get(id=number))
            context = {
                'newmessage': Message.objects.last(),
                'user': User.objects.get(id = number)
            }
        return render(request,'user/partials/message.html', context)
    else:
        return redirect('/users/'+number)

def deletemessage(request, number):
    a = Message.objects.get(id=int(request.POST['message_id']))
    b = a.id
    a.delete()
    return HttpResponse(b)

def comment(request, number):
    if request.method == 'POST':
        errors = Comment.objects.comment(request.POST)
        if len(errors):
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return HttpResponse("")
        else:
            Comment.objects.create(text=request.POST['commentbox'],poster=User.objects.get(id=request.session['id']), message = Message.objects.get(id=request.POST['message_id']), page = User.objects.get(id=number))
            this_message = Message.objects.get(id = request.POST['message_id'])
            this_message.updated_at = datetime.now()
            this_message.save()
            context = {
                'comment': Comment.objects.last(),
                'user': User.objects.get(id = number)
            }
        return render(request,'user/partials/comment.html', context)
    else :
        return redirect('/users/'+number)

def deletecomment(request,number):
    a = Comment.objects.get(id=int(request.POST['comment_id']))
    b = 'c'+str(a.id)
    a.delete()
    return HttpResponse(b)

def dashboard(request): 
    allfollowings = [request.session['id']]
    followings = Follow.objects.filter(follower=request.session['id'])
    for i in followings:
        allfollowings.append(i.following.id)
    context = {
        'mymessages': Message.objects.filter(page__in=allfollowings).order_by('-updated_at') [:15],
        'comments': Comment.objects.filter(page__in=allfollowings),
        'isfollowing': Follow.objects.filter(follower= request.session['id']),
        'range': [1,2,3,4,5]
    }
    return render(request,'user/dashboard.html', context)

def follow(request,number):
    this_user = User.objects.get(id= request.session['id'])
    that_user = User.objects.get(id = number)
    Follow.objects.create(following = that_user, follower = this_user)
    return redirect('/users/'+number)

def followers(request,number):
    context = {
        'followers' : Follow.objects.filter(following = number),
    }
    return render(request,'user/follows.html',context)
def followings(request,number):
    context = {
        'followings' : Follow.objects.filter(follower = number),
    }
    return render(request,'user/follows.html',context)

def getuser(request):
    if 'id' not in request.session:
        return redirect('/')
    context = {
        'users': (User.objects.filter(first_name__contains=request.POST['search']) | User.objects.filter(current__contains=request.POST['search'])  | User.objects.filter(email__contains=request.POST['search'])).annotate(num_followers=Count('followings')).order_by('-num_followers').distinct() [:15],
        'current': User.objects.get(id = request.session['id'])
    }
    return render(request,'user/partials/users.html', context)

def updatedashboard(request):
    lastmessage = Message.objects.get(id=request.POST['lastmessage']).updated_at
    allfollowings = [request.session['id']]
    followings = Follow.objects.filter(follower=request.session['id'])
    for i in followings:
        allfollowings.append(i.following.id)
    context = {
        'mymessages': Message.objects.filter(page__in=allfollowings).filter(updated_at__gt=lastmessage).order_by('-updated_at'),
        'comments': Comment.objects.filter(page__in=allfollowings).filter(updated_at__gt=lastmessage),
        'range' : [1,2,3,4,5]
    }
    return render(request, 'user/partials/newmessages.html', context)
def moredashboard(request):
    lastmessage = Message.objects.get(id=request.POST['lastmessage']).updated_at
    allfollowings = [request.session['id']]
    followings = Follow.objects.filter(follower=request.session['id'])
    for i in followings:
        allfollowings.append(i.following.id)
    context = {
        'mymessages': Message.objects.filter(page__in=allfollowings).filter(updated_at__lt=lastmessage).order_by('-updated_at') [:15],
        'comments': Comment.objects.filter(page__in=allfollowings).filter(updated_at__lt=lastmessage),
        'range' : [1,2,3,4,5]
    }

    return render(request, 'user/partials/newmessages.html', context)

def unfollow(request,number):
    this_user = User.objects.get(id= request.session['id'])
    that_user = User.objects.get(id = number)
    follow = Follow.objects.get(following = that_user, follower = this_user)
    follow.delete()
    return redirect('/users/'+number)

def changepic(request):
    this_user = User.objects.get(id= request.session['id'])
    if len(request.FILES) != 0:
        if str(this_user.image) != "none.jpg":
            _delete_file("media/"+str(this_user.image))
        handle_uploaded_file(request.FILES['newimg'], this_user.email+".jpg")
        this_user.image = this_user.email+".jpg"
        this_user.save()
    return redirect('/users/'+str(request.session['id']))



def handle_uploaded_file(file, filename):
    with open('media/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def _delete_file(path):
    if os.path.isfile(path):
        os.remove(path)