from django.shortcuts import render, redirect
from .mongodb import notes_collection
from bson.objectid import ObjectId
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
import random
from django.core.mail import send_mail
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache


@login_required
def notes_list(request):

    search_query = request.GET.get('search')

    if search_query:

        notes = list(
            notes_collection.find({
                'username': request.user.username,
                'title': {
                    '$regex': search_query,
                    '$options': 'i'
                }
            })
        )

    else:

        notes = list(
            notes_collection.find(
                {'username': request.user.username}
            )
        )

    for note in notes:
        note['id'] = str(note['_id'])

    total_notes = len(notes)

    return render(
        request,
        'notes_list.html',
        {
            'notes': notes,
            'total_notes': total_notes
        }
    )
@login_required
def add_note(request):
    if request.method == 'POST':

        title = request.POST['title']
        content = request.POST['content']

        notes_collection.insert_one({
    'title': title,
    'content': content,
    'username': request.user.username,
    'created_at': datetime.now()
})

        return redirect('notes_list')

    return render(request, 'add_note.html')
@login_required
def update_note(request, note_id):

    note = notes_collection.find_one(
        {'_id': ObjectId(note_id)}
    )

    if request.method == 'POST':

        title = request.POST['title']
        content = request.POST['content']

        notes_collection.update_one(
            {'_id': ObjectId(note_id)},
            {
                '$set': {
                    'title': title,
                    'content': content
                }
            }
        )

        return redirect('notes_list')

    return render(
        request,
        'update_note.html',
        {'note': note}
    )
@login_required
def delete_note(request, note_id):
    notes_collection.delete_one(
        {'_id': ObjectId(note_id)}
    )

    return redirect('notes_list')
def register(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Username check
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'register.html')

        # Email check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'register.html')

        # OTP send code
        otp = random.randint(100000, 999999)

        request.session['otp'] = str(otp)
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password

        send_mail(
            'NotesHub OTP Verification',
            f'Your OTP is {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        return redirect('verify_otp')

    return render(request, 'register.html')
def user_logout(request):

    logout(request)

    return redirect('login')
@login_required
def profile(request):

    total_notes = notes_collection.count_documents(
        {'username': request.user.username}
    )

    context = {
        'username': request.user.username,
        'email': request.user.email,
        'date_joined': request.user.date_joined,
        'total_notes': total_notes
    }

    return render(
        request,
        'profile.html',
        context
    )
def verify_otp(request):

    if request.method == 'POST':

        entered_otp = request.POST['otp'].strip()

        if entered_otp == request.session.get('otp'):

            User.objects.create_user(
                username=request.session['username'],
                email=request.session['email'],
                password=request.session['password']
            )

            request.session.flush()

            return redirect('login')

        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'verify_otp.html')

@ensure_csrf_cookie
@never_cache
def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        action = request.POST.get('action')

        if not username:
            return render(
                request,
                'login.html',
                {'error': 'Username is required'}
            )

        if action == 'password':
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('notes_list')

            return render(
                request,
                'login.html',
                {'error': 'Invalid username or password'}
            )

        if action == 'otp':
            try:
                user = User.objects.get(username=username)

                otp = str(random.randint(100000, 999999))

                request.session['login_otp'] = otp
                request.session['login_user_id'] = user.id

                send_mail(
                    'Login OTP',
                    f'Your OTP is {otp}',
                    None,
                    [user.email],
                    fail_silently=False
                )

                return redirect('verify_login_otp')

            except User.DoesNotExist:
                return render(
                    request,
                    'login.html',
                    {'error': 'Username not registered'}
                )

        return render(
            request,
            'login.html',
            {'error': 'Please choose a login method'}
        )

    return render(request, 'login.html')
def forgot_password(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        try:

            # Check user exists
            user = User.objects.get(email=email)

            # Generate OTP
            otp = str(random.randint(100000, 999999))

            # Save OTP and Email in Session
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp

            # Send OTP Email
            send_mail(
                subject='Password Reset OTP',
                message=f'Your OTP is: {otp}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )

            return redirect('verify_reset_otp')

        except User.DoesNotExist:

            return render(
                request,
                'forgot_password.html',
                {
                    'error': 'Email not found'
                }
            )

    return render(
        request,
        'forgot_password.html'
    )
def verify_reset_otp(request):

    if request.method == 'POST':

        otp = request.POST['otp']

        if otp == request.session.get('reset_otp'):

            return redirect('reset_password')

        return render(
            request,
            'verify_reset_otp.html',
            {
                'error': 'Invalid OTP'
            }
        )

    return render(
        request,
        'verify_reset_otp.html'
    )


def reset_password(request):

    if request.method == 'POST':

        new_password = request.POST['password']

        user = User.objects.get(
            email=request.session['reset_email']
        )

        user.set_password(new_password)
        user.save()

        request.session.pop('reset_email', None)
        request.session.pop('reset_otp', None)

        return redirect('login')

    return render(
        request,
        'reset_password.html'
    )
@ensure_csrf_cookie
@never_cache
def verify_login_otp(request):

    if request.method == 'POST':

        otp = request.POST['otp']

        if otp == request.session.get('login_otp'):

            user = User.objects.get(
                id=request.session['login_user_id']
            )

            login(request, user)

            request.session.pop('login_otp', None)
            request.session.pop('login_user_id', None)

            return redirect('notes_list')

        return render(
            request,
            'verify_login_otp.html',
            {'error': 'Invalid OTP'}
        )

    return render(request, 'verify_login_otp.html')