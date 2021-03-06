import math
import re

from library_search_app.models import *
from .forms import BoardsForm
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView

from django.utils import timezone
from datetime import datetime
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
import random
import string
import threading


def main(request):
    return render(request, 'main.html')


def introduce(request):
    return render(request, 'introduce.html')


def login(request):
    if request.method == "POST":
        user_id = request.POST["user_id"]
        password = request.POST["password"]
        user = auth.authenticate(request, user_id=user_id, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('main')
        else:
            args = {}
            args.update({"msg": "가입하지 않은 아이디이거나, 잘못된 패스워드입니다."})
            print(args["msg"])
            return render(request, 'login.html', args)
    return render(request, 'login.html')


def logout(request):
    auth.logout(request)
    return redirect('main')


def forgot_password(request):
    print(request.method)
    if request.method == "POST":
        user_id = request.POST["user_id"]
        email = request.POST["email"]

        # email체크
        try:
            user = User.objects.get(user_id=user_id, email=email)

            # 임시패스워드 생성
            tmp_password = ""
            for i in range(8):
                tmp_password += random.choice(string.ascii_lowercase)
            tmp_password += str(random.randint(1000, 9999))

            title = user_id+"님의 LIBIND 임시패스워드"
            content = "임시패스워드 : " + tmp_password

            # 패스워드 변경
            user.set_password(tmp_password)
            user.save()

            email = EmailMessage(title, content, to=[email])
            # 전송시 속도가 느려짐으로 쓰레드로 돌림
            threading.Thread(target=email.send).start()
            return redirect('main')
        except:
            return render(request, 'forgot_password.html', {"error_msg": "ID와 Email이 일치하지 않습니다."})

    return render(request, 'forgot_password.html')


def user_register(request):
    return render(request, 'user_register.html')


def user_register_idcheck(reuqest):
    if reuqest.method == "POST":
        user_id = reuqest.POST['user_id']
    else:
        user_id = ''

    try:
        user = User.objects.get(user_id=user_id)
    except:
        user = None
    if user is None:
        overlap = "pass"
    else:
        overlap = "fail"
    context = {'overlap': overlap}
    return JsonResponse(context)


def user_register_result(request):
    if request.method == "POST":

        user_id = request.POST['user_id']
        password = request.POST['password']
        last_name = request.POST['last_name']
        phone = request.POST['phone_number']
        email = request.POST['email']
        # 생년월일 기입여부 체크
        if request.POST['birth_year'] != '' and request.POST['birth_month'] != '' and request.POST['birth_day'] != '':
            birth_year = int(request.POST['birth_year'])
            birth_month = int(request.POST['birth_month'])
            birth_day = int(request.POST['birth_day'])

        # 생년월일 미기입시 None으로 기입
        try:
            date_of_birth = datetime(birth_year, birth_month, birth_day)
        except:
            date_of_birth = None

        p = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
        # data 길이 체크
        if len(user_id) < 4 or len(password) < 8 or len(last_name) < 2:
            return redirect('error')
        # email 형식체크
        elif not p.match(email):
            return redirect('error')
        # ID중복여부 체크
        elif user_id and User.objects.filter(user_id=user_id).count() == 0:
            user = User.objects.create_user(
                user_id, password, last_name, email, phone, date_of_birth
            )
            auth.login(request, user)
            return redirect('/library_search/user_register_done')
        else:
            return redirect('error')
    return render(request, 'user_register.html')


def user_register_done(request):
    return render(request,  'user_register_done.html')


@ login_required
def profil(request):
    user = request.user
    args = {}

    # 프로필 출력시 생년월일여부 체크 및 년월일로 나누어 변환
    if user.date_of_birth != None:
        date_birth = datetime.strptime(str(user.date_of_birth)[
            :-6], '%Y-%m-%d %H:%M:%S')
        args.update({"birth_year": date_birth.year})
        args.update({"birth_month": date_birth.month})
        args.update({"birth_day": date_birth.day})

    return render(request, 'profil.html', args)


@ login_required
def password_change(request):

    if request.method == "POST":
        current_password = request.POST["old_password"]
        new_password = request.POST.get("new_password1")
        password_confirm = request.POST.get("new_password2")
        user = request.user

        # 새로운패스워드 길이 체크
        if len(new_password) < 8:
            return redirect('error')
        # 새로운 패스워드와 패스워드 확인이 같은지 체크
        elif new_password != password_confirm:
            return redirect('error')
        # 현재 패스워드 일치여부 체크
        elif check_password(current_password, user.password):
            user.set_password(new_password)
            user.save()
            auth.login(request, user)
            url = "/library_search/"
            resp_body = '<script>alert("패스워드 변경이 완료되었습니다.");window.location="%s"</script>' % url
            return HttpResponse(resp_body)
        else:
            return redirect('error')

    return render(request, 'password_change.html')


@login_required
def board_write(request, category=''):
    boards_form = BoardsForm()
    args = {}
    args.update({"form": boards_form})
    args.update({"category": category})

    if request.method == "POST":
        try:
            category_obj = BoardCategories.objects.get(
                category_name=request.POST['category_name'])
        except:
            return redirect('error')
        board_type = request.POST['board_type']
        user = request.user
        title = request.POST['title']
        content = request.POST['content']

        if category_obj and board_type and user and title and content:
            board = Boards.objects.create(
                category=category_obj, board_type=board_type, user=user, title=title, content=content)
            return redirect('/library_search/board_view/'+category+'/'+str(board.id))
        else:
            return redirect('error')

    return render(request, "board_write.html", args)


@ login_required
def board_update(request, category='', pk=''):
    try:
        board = Boards.objects.get(id=pk)
    except:
        return redirect('error')

    boards_form = BoardsForm(initial={'content': board.content})
    args = {}
    args.update({"form": boards_form})
    args.update({"board": board})

    if request.method == "POST":
        board_type = request.POST['board_type']
        user = request.user
        title = request.POST['title']
        content = request.POST['content']

        board.board_type = board_type
        board.user = user
        board.title = title
        board.content = content
        board.last_update_date = timezone.now()
        board.save()
        return redirect('/library_search/board_view/'+category+'/'+str(pk))

    return render(request, "board_update.html", args)


@ login_required
def board_delete(request, category='', pk=''):
    try:
        board = Boards.objects.get(id=pk)
        board.delete()
        return redirect('/library_search/board_view/'+category)
    except:
        return redirect('error')


class BoardView(DetailView):
    model = Boards
    template_name = 'board_view.html'

    def dispatch(self, request, category='', pk=''):
        obj = self.get_object()
        if request.user != obj.user:
            obj.view_count = obj.view_count + 1
            obj.save()

        replies = BoardReplies.objects.filter(article__id=pk)
        like = BoardLikes.objects.filter(article__id=pk, user=request.user)
        like_length = BoardLikes.objects.filter(article__id=pk).count()
        args = {}
        args.update({"object": obj})
        args.update({"pk": pk})
        args.update({"category": category})
        args.update({"replies": replies})
        args.update({"like_length": like_length})
        if like.count() != 0:
            args.update({"like": "true"})

        return render(request, self.template_name, args)


def board_list(request, category=''):

    if category:
        board_category = BoardCategories.objects.get(category_name=category)
        articles = Boards.objects.filter(
            category__category_name=category).order_by('-id')
    else:
        return redirect('error')

    paginator = Paginator(articles, board_category.list_count)

    try:
        page = int(request.GET['page'])
    except:
        page = 1
    articles = paginator.get_page(page)

    page_count = 10
    page_list = []
    first_page = (math.ceil(page/page_count)-1)*page_count+1
    last_page = min([math.ceil(page/page_count) *
                     page_count, paginator.num_pages])
    for i in range(first_page, last_page+1):
        page_list.append(i)

    args = {}
    args.update({"articles": articles})
    args.update({"category": category})
    # args.update({"search_text": search_text})
    args.update({"page_list": page_list})
    return render(request, "board_list.html", args)


def reply_write(request, category, pk):
    if request.method == 'POST':
        article = Boards.objects.get(id=pk)
        user = request.user
        level = request.POST['level']
        content = request.POST['content']
        BoardReplies.objects.create(
            article=article, user=user, level=level, content=content)
    return redirect('/library_search/board_view/'+category+'/'+str(pk))


def board_like(request):
    try:
        user = User.objects.get(id=request.POST['user_id'])
        article = Boards.objects.get(id=request.POST['article_id'])
        like = BoardLikes.objects.filter(article=article, user=user)
        print(user, article, like)
        if like.count() == 0:
            BoardLikes.objects.create(article=article, user=user)
            like_condition = "like"
        else:
            like[0].delete()
            like_condition = "unlike"
        return JsonResponse({'like': like_condition})
    except:
        return JsonResponse('')


def error(request):
    return render(request, 'error.html')
