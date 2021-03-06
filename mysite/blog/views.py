from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.db.models import Count

from .forms import EmailPostForm, CommentForm, SearchForm
from .models import Post, Comment

from haystack.query import SearchQuerySet

# Search option

def post_search(request):
    form = SearchForm()
    cd,results,total_results = ('','','')
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data
            results = SearchQuerySet().models(Post)\
                      .filter(content=cd['query']).load_all()
            # count total results
            total_results = results.count()
    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'cd' : cd,
                   'results' : results,
                   'total_results' : total_results})

# Create your views here.
# The below code has been commented in order to use Class PostListView and can be seen from urls.py file
def post_list(request, tag_slug=None):
    print('<<<<<<<<<<<<<<<<  Inside post_list >>>>>>>>>>>>>>>>>>>>>>>>>>')
    object_list = Post.draft.all()
    #posts = Post.draft.all()
    print(Post.draft.all())
    paginator = Paginator(object_list,3)
    page = request.GET.get('page')

    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
        
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'page' : page,
                   'tag' : tag,})

def post_share(request,post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='draft')
    sent = False
    toemail = ''

    if request.method == 'POST':
        #Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            #Form field passed validation
            cd = form.cleaned_data
            # ... send email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recomends you reading "{}"'.format(cd['name'],cd['email'],post.title)
            message =  'Read "{}" at {}\n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            toemail = cd['to']
            #send_mail(subject,message,'fromsomebody@myblog.com',[cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post' : post,
                                                    'form' : form,
                                                    'sent' : sent,
                                                    'toemail' : toemail,})

def post_detail(request, year, month, day, post):
    print('<<<@@@@ Inside @@@@>>>>')
    print('year' + year + 'month' + month + 'day' + day + 'post' + post)
    post = get_object_or_404(Post, slug=post,
                                   status ='draft',
                                   publish__year = year,
                                   publish__month = month,
                                   publish__day = day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.draft.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]

    if request.method=='POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()                     
    
    return render(request,
                  'blog/post/detail.html',
                  {'post':post,
                  'comments': comments,
                  'comment_form':comment_form,
                  'similar_posts':similar_posts,})


class PostListView(ListView):
    queryset = Post.draft.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'




