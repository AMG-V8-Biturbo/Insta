from django.db import models
from imagekit.models import ProcessedImageField
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

'''
User Table
column: username, email, profile_pic
method: get_connections, get_followers, etc.

Connection Table
column: creator, following, timestamp

Post table
column: author, title, image
method: get_likes_count, get_comments_count

Comment table
column: user(author), post, comment, timestamp

Like table
column: user(author), post
'''

# Create your models here.
class InstaUser(AbstractUser):
    profile_pic = ProcessedImageField(
        upload_to="static/images/profiles",
        format='JPEG',
        options={'quality':100},
        blank=True,
        null=True
    )

    def get_connections(self):
        # fetch all connections starts from current InstaUser.
        connections = UserConnection.objects.filter(creator=self)
        return connections

    def get_followers(self):
        # fetch all connection sends at current InstaUser.
        followers = UserConnection.objects.filter(following=self)
        return followers

    def is_followed_by(self, user):
        # check if the passed in user follows this current InstaUser
        followers = UserConnection.objects.filter(following=self)
        return followers.filter(creator=user).exists()

    def get_absolute_url(self):
        # direct to path 'profile' defined in urls.py
        # This url path is passed to UserProfile view
        return reverse('profile', args=[str(self.id)])

    def __str__(self):
        return self.username

class UserConnection(models.Model):
    '''
    why we still need 'related_name' after 'get_connections' and 'get_followers' in InstaUser class?
    '''
    created = models.DateTimeField(auto_now_add=True, editable=False)
    creator = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="my_followings") # friendship_creator_set, connections starts from current InstaUser.
    following = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name="my_followers") # friend_set, connections ends at current InstaUser.

    def __str__(self):
        return self.creator.username + ' follows ' + self.following.username

class Post(models.Model):
    author = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE, # delete this author will delete all his posts
        related_name='my_posts' # we can use author.posts to get all posts belong to this user
    )
    title = models.TextField(blank=True, null=True)
    image = ProcessedImageField(
        upload_to="static/images/posts",
        format='JPEG',
        options={'quality':100},
        blank=True,
        null=True
    )
    created = models.DateTimeField(auto_now_add=True, editable=False)
    
    def get_absolute_url(self):
        return reverse("post", args=[str(self.id)])

    def get_like_count(self):
        return self.likes.count()

    def get_comment_count(self):
        return self.comments.count()

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    comment = models.CharField(max_length=100)
    posted_on = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.comment

class Like(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        InstaUser,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    class Meta:
        unique_together = ('post', 'user')
    def __str__(self):
        return 'Like: ' + self.user.username + ' ' + self.post.title
