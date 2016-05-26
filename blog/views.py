 # -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from blog.models import DjangoBoard
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from blog.pagingHelper import pagingHelper

rowsPerPage = 2
# Create your views here.
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})
@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html',{'posts': posts})
@login_required
def post_publish(request,pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('blog.views.post_detail', pk=pk)
@login_required
def post_remove(request,pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('blog.views.post_list')
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('blog.views.post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})
@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('blog.views.post_detail', pk=comment.post.pk)
@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment, pk=pk)
    post.pk = comment.post.pk
    comment.delete()
    return redirect('blog.views.post_detail', pk=post.pk)
def home(request):       # using model, extract two datas by id reversely without any additional SQL
    boardList = DjangoBoard.objects.order_by('-id')[0:2]
    current_page =1

    # using model, extract the number of all datas.
    totalCnt = DjangoBoard.objects.all().count()

    # helper class to paging
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)
    print ('totalPageList', totalPageList)

    # return info to the template -> static template + dynamin data
    # call listSpecificPage.html to see first view.
    # send information to the dictionary
    return render_to_response('blog/listSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt,
    'current_page':current_page ,'totalPageList':totalPageList} )
def write_form(request):
    return render_to_response('blog/writeBoard.html')
@csrf_exempt
def DoWriteBoard(request):
    br = DjangoBoard (subject = request.POST['subject'],
                      name = request.POST['name'],
                      mail = request.POST['email'],
                      memo = request.POST['memo'],
                      created_date = timezone.now(),
                      hits = 0
                     )
    br.save()

    # 저장을 했으니, 다시 조회해서 보여준다.
    url = ('listSpecificPageWork\?current_page=1')
    return HttpResponseRedirect(url)
def listSpecificPageWork(request):
    current_page = request.GET['current_page']
    totalCnt = DjangoBoard.objects.all().count()

    print ('current_page=', current_page)

    # 페이지를 가지고 범위 데이터를 조회한다 => raw SQL 사용함
    boardList = DjangoBoard.objects.raw('SELECT Z.* FROM(SELECT X.*, ceil( rownum / %s ) as page FROM ( SELECT ID,SUBJECT,NAME, CREATED_DATE, MAIL,MEMO,HITS \
                                        FROM SAMPLE_BOARD_DJANGOBOARD  ORDER BY ID DESC ) X ) Z WHERE page = %s', [rowsPerPage, current_page])

    print ('boardList=',boardList, 'count()=', totalCnt)

    # 전체 페이지를 구해서 전달...
    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)

    print ('totalPageList', totalPageList)

    return render_to_response('blog/listSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt,
                                                        'current_page':int(current_page) ,'totalPageList':totalPageList} )
def viewWork(request):
    pk= request.GET['memo_id']
    boardData = DjangoBoard.objects.get(id=pk)


    # 조회수를 늘린다.
    DjangoBoard.objects.filter(id=pk).update(hits = boardData.hits + 1)


    return render_to_response('blog/viewMemo.html', {'memo_id': request.GET['memo_id'],
                                                'current_page':request.GET['current_page'],
                                                'searchStr': request.GET['searchStr'],
                                                'boardData': boardData } )
def listSearchedSpecificPageWork(request):
    searchStr = request.GET['searchStr']
    pageForView = request.GET['pageForView']

    # 다음은 테이블에서 subject 항목에 대해 LIKE SQL을 수행한다.
    totalCnt = DjangoBoard.objects.filter(subject__contains=searchStr).count()

    pagingHelperIns = pagingHelper();
    totalPageList = pagingHelperIns.getTotalPageList( totalCnt, rowsPerPage)

    # Raw SQL에 like 구문 적용방법.. 이 방법 찾다가 삽질 좀 했다.
    boardList = DjangoBoard.objects.raw("""SELECT Z.* FROM ( SELECT X.*, ceil(rownum / %s) as page \
        FROM ( SELECT ID,SUBJECT,NAME, CREATED_DATE, MAIL,MEMO,HITS FROM SAMPLE_BOARD_DJANGOBOARD \
        WHERE SUBJECT LIKE '%%'||%s||'%%' ORDER BY ID DESC) X ) Z WHERE page = %s""", [rowsPerPage, searchStr, pageForView])

    return render_to_response('blog/listSearchedSpecificPage.html', {'boardList': boardList, 'totalCnt': totalCnt,
                                                        'pageForView':int(pageForView) ,'searchStr':searchStr, 'totalPageList':totalPageList} )
