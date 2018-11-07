from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from taggit.managers import TaggableManager

# Create your models here.

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager,self).get_queryset()\
                                           .filter(status='published')
class DraftManager(models.Manager):
    def get_queryset(self):
        return super(DraftManager,self).get_queryset().filter(status='draft')

class DraftQuerySet(models.QuerySet):
    def drafts(self):
        return self.filter(status='draft')
       
class Post(models.Model):
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published','Published'),
        )
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                          unique_for_date='publish')
    author = models.ForeignKey(User, related_name='blog_posts')

    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length = 10,
                              choices=STATUS_CHOICES,default='draft')

    tags = TaggableManager()

    objects = models.Manager() # The default manager
    #published = PublishedManager() # our custom manager
    draft=DraftManager()
    #draft = DraftQuerySet().as_manager()

    class Meta:
        ordering = ('-publish', )

    def get_absolute_url(self):
        print('<<<<<<<<<    inside get absolute url     >>>>>>>>>>>>>>> ')
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.strftime('%m'),
                             self.publish.strftime('%d'),
                             self.slug])

    def __str__(self):
        return self.title

class Comment(models.Model):
   post = models.ForeignKey(Post, related_name='comments')
   name = models.CharField(max_length=80)
   email = models.EmailField()
   body = models.TextField()
   created = models.DateTimeField(auto_now_add=True)
   updated = models.DateTimeField(auto_now_add=True)
   active = models.BooleanField(default=True)

   class Meta:
       ordering = ('created',)

   def __str__(self):
       return 'comment by {} on {}'.format(self.name, self.post)
