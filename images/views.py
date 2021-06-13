from django.shortcuts import render , redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from .models import Image
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from common.decorators import ajax_required
from django.core.paginator import Paginator , EmptyPage , PageNotAnInteger
from django.http import HttpResponse
from actions.utils import create_action
import redis
from django.conf import settings


#connection to redis
r = redis.Redis(host=settings.REDIS_HOST,port=settings.REDIS_PORT,db=settings.REDIS_DB)



@login_required
def image_create(request):
    if request.method == "POST":
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.save()
            create_action(request.user,"upload image",new_item)
            messages.success(request,'Image is added!')

            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)
    return render(request,'images/image/create.html',{"form":form})

def image_detail(request,id,slug):
    image = get_object_or_404(Image,id=id,slug=slug)
    total_view = r.incr(f'image:{image.id}:views')
    r.zincrby('image_rankig', 1, image.id)
    return render(request, 'images/image/detail.html',{'image':image,'total_view':total_view})

@login_required
def image_rankig(request):
    image_rankig = r.zrange('image_rankig', 0, -1, desc=True)[:10]
    image_rankig_ids = [int(id) for id in image_rankig]
    most_view = list(Image.objects.filter(id__in=image_rankig_ids))
    most_view.sort(key=lambda x : image_rankig_ids.index(x.id))
    return render(request, "images/image/ranking.html",{
        "most_view":most_view,
    })

@ajax_required
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            users_liked = image.user_like.all()
            users = []
            for i in users_liked:
                users.append(i.username)
            users_liked = str(users)
            if action == "like":
                image.user_like.add(request.user)
                create_action(request.user,'likes',image)
            else:
                image.user_like.remove(request.user)
            return JsonResponse({'status':'ok','users_liked':users_liked})
        except:
            pass
    return JsonResponse({'status':'error'})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 4)
    page = request.GET.get('page') #2
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse("")
        images = paginator.page(paginator.num_pages)
    if request.is_ajax():
        return render(request,'images/image/list_ajax.html',{"images":images})
    return render(request,'images/image/list.html',{"images":images})
