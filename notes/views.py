from django.shortcuts import render, redirect
from .mongodb import notes_collection
from bson.objectid import ObjectId
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

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
            'username': request.user.username
        })
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
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect('login')

    return render(request, 'register.html')


def user_login(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('notes_list')

    return render(request, 'login.html')


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