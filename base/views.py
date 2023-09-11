import openpyxl
from pytz import timezone


from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout

from django.contrib import messages
from . import models
from . import forms


from django.http import HttpResponse
from django.shortcuts import render, redirect


def loginPage(request):
    page='login'
    if(request.user.is_authenticated):
        return HttpResponse("You are already login")
    if(request.method=="POST"):
        username=request.POST.get("username")
        password=request.POST.get("password")
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,"No user found")
        # print(username)
        # print(password)

        user=authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect("home")
        else:
            context={
                'page':page
            }
            return render(request,'base/login_register.html',context)

    context={
        'page':page
    }
    return render(request,'base/login_register.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page='register'
    if(request.method == "POST"):
        form=forms.UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.save()
            login(request,user)
            return redirect("home")
        else:
            messages.error(request,"Error during registration")


            
    context={
        'page':page,
        'form':forms.UserCreationForm()
    }
    return render(request,'base/login_register.html',context)

def UserProfile(request,pk):
    user=models.User.objects.get(id=pk)
    rooms=user.room_set.all()
    messages=user.message_set.all().order_by("-created")
    topics=models.Topic.objects.all()
    context={
        'user':user,
        'rooms':rooms,
        'room_message':messages,
        'topics':topics,
    }
    return render(request,'base/profile.html',context)

def home(request):
    q=request.GET.get('q') if request.GET.get('q')!=None else ' '
    topics=models.Room.objects.all()
    rooms=models.Room.objects.filter(topic__name__icontains=q)
    topics =models.Topic.objects.all()
    room_count=rooms.count()
    room_message=models.Message.objects.filter(room__topic__name__icontains=q).order_by("-created")

    context={
        'rooms':rooms,
        'topics':topics,
        'room_count':room_count,
        'room_message':room_message,
        }
    return render(request,'base/home.html',context)



def room(request, pk):
    room = models.Room.objects.get(id=pk)
    messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    # Check if the user is a participant or has a pending request
    is_participant = request.user in participants
    has_pending_request = models.MembershipRequest.objects.filter(user=request.user, room=room, status='pending').exists()

    if not is_participant and not has_pending_request:
        # User is neither a participant nor has a pending request
        can_send_request = True
    else:
        can_send_request = False

    if request.method == "POST":
        if can_send_request:
            # User can send a membership request
            models.MembershipRequest.objects.create(user=request.user, room=room, status='pending')
            return redirect('room', pk=room.id)
        else:
            # User is a participant or already has a pending request
            return HttpResponse("You are not allowed to send a request.")

    context = {
        'room': room,
        'messages': messages,
        'participants': participants,
        'can_send_request': can_send_request,
    }

    return render(request, 'base/room.html', context)

        
    

@login_required(login_url='login')
def createRoom(request):
    form = forms.Roomform()

    if request.method == 'POST':
        form = forms.Roomform(request.POST)
        if form.is_valid():
            form.save()
            print("Room created successfully")
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request,pk):
    room=models.Room.objects.get(id=pk)
    form=forms.Roomform(instance=room)

    if(request.user != room.host):
        return HttpResponse("You are not alllowed")
    if(request.method=='POST'):
        form=forms.Roomform(request.POST,instance=room)
        if form.is_valid():
            form.save()
            print("Details updated successfully")
            return redirect("home")

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request,pk):
    room=models.Room.objects.get(id=pk)
    if(request.method=="POST"):
        room.delete()
        return redirect('home')
    
    context = {'room':room}
    return render(request, 'base/delete_room.html', context)

@login_required(login_url='login')

def delete_message(request,pk):
    message=models.Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowwed to Delete")
    if(request.method=="POST"):
        message.delete()
        return redirect('home')
    context = {'room':message}
    print(context)
    return render(request, 'base/delete_room.html', context)
    


def export_comments(request, pk):
    comments = models.Message.objects.filter(room_id=pk)
    wb = openpyxl.Workbook()
    ws = wb.active

    ws.append(["User", "Timestamp", "Message"])

    for comment in comments:
        # Convert the datetime to the same datetime but with tzinfo set to None
        created_local = comment.created.replace(tzinfo=None)
        
        ws.append([comment.user.username, created_local, comment.body])

    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = f"attachment; filename=room_{pk}_comments.xlsx"
    wb.save(response)

    return response




@login_required(login_url='login')
def accept_membership_request(request, request_id):
    if request.method == "POST":
        membership_request = models.MembershipRequest.objects.get(pk=request_id)
        # Check if the user performing the action is the host/admin of the room
        if request.user == membership_request.room.host:
            membership_request.status = 'accepted'
            membership_request.save()
            # Optionally, you can add the user to the room's participants here.
            return redirect('room', pk=membership_request.room.id)
    return HttpResponse("Permission denied")

@login_required(login_url='login')
def reject_membership_request(request, request_id):
    if request.method == "POST":
        membership_request = models.MembershipRequest.objects.get(pk=request_id)
        if request.user == membership_request.room.host:
            membership_request.status = 'rejected'
            membership_request.save()
            return redirect('room', pk=membership_request.room.id)
    return HttpResponse("Permission denied")

