from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

from ..models import Post

print('Inside template tags')

@register.simple_tag
def total_posts():
    print('Inside total_posts method >>>>')
    return Post.draft.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.draft.order_by('-publish')[:count]
    return {'latest_posts' : latest_posts}


@register.assignment_tag
def get_most_commented_posts(count=5):
    return Post.draft.annotate(
        total_comments=Count('comments')
        ).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

