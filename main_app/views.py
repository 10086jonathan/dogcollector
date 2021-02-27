import uuid
import boto3

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Dog, Toy, Photo
from .forms import FeedingForm

# Create your views here.

S3_BASE_URL = 'https://s3.us-west-1.amazonaws.com/'
BUCKET = 'catcollector-ja'

def signup(request):
    error_message = ''

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dogs_index')
        else:
            error_message = 'invalid data for sign up'

    form = UserCreationForm()
    context = { 'form': form, 'error_message': error_message }

    return render(request, 'registration/signup.html', context)

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def dogs_index(request):
    dogs = Dog.objects.all()
    return render(request, 'dogs/index.html', { 'dogs': dogs })

@login_required
def dogs_detail(request, dog_id):
    dog = Dog.objects.get(id=dog_id)
    toys_dog_doesnt_have = Toy.objects.exclude(id__in = dog.toys.all().values_list('id'))
    feeding_form = FeedingForm()
    return render(request, 'dogs/detail.html', {
        'dog': dog,
        'feeding_form': feeding_form,
        'toys': toys_dog_doesnt_have
    })

class DogCreate(LoginRequiredMixin, CreateView):
    model = Dog
    fields = '__all__'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    success_url = '/dogs/'

class DogUpdate(LoginRequiredMixin, UpdateView):
    model = Dog
    fields = ['breed', 'description', 'age']

class DogDelete(LoginRequiredMixin, DeleteView):
    model = Dog
    success_url = '/dogs/'

class ToyList(LoginRequiredMixin, ListView):
    model = Toy

class ToyCreate(LoginRequiredMixin, ListView):
    model = Toy
    fields = '__all__'

class ToyUpdate(LoginRequiredMixin, UpdateView):
    model = Toy
    fields = '__all__'

class ToyDelete(LoginRequiredMixin, DeleteView):
    model = Toy
    success_url = '/toys/'

@login_required
def add_feeding(request, dog_id):
    form = FeedingForm(request.POST)
    if form.is_valid():
        new_feeding = form.save(commit=False)
        new_feeding.dog_id = dog_id
        new_feeding.save()
    return redirect('dogs_detail', dog_id=dog_id)

@login_required
def toys_index(request):
    toys = Toy.objects.all()
    return render(request, 'toys/index.html', {'toys': toys})

@login_required
def toys_detail(request, toy_id):
    toy = Toy.objects.get(id=toy_id)
    return render(request, 'toys/detail.html', {'toy': toy})

@login_required
def assoc_toy(request, dog_id, toy_id):
    Dog.objects.get(id=dog_id).toys.add(toy_id)
    return redirect('dogs_detail', dog_id=dog_id)

@login_required
def add_photo(request, dog_id):
    photo_file = request.FILES.get('photo_file', None)

    if photo_file:
        s3 = boto3.client('s3')
        index_of_last_period = photo_file.name.rfind('.')
        key = uuid.uuid4().hex[:6] + photo_file.name[index_of_last_period:]

        try:
            s3.upload_fileobj(photo_file, BUCKET, key)
            url = f"{S3_BASE_URL}{BUCKET}/{key}"
            photo = Photo(url=url, dog_id=dog_id)
            photo.save()
        except:
            print('an error occured uploading files to aws')

    return redirect('dogs_detail', dog_id=dog_id)