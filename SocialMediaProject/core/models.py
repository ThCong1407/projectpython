from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='default.jpg', upload_to='profile_pics')
    cover_photo = models.ImageField(default='cover_default.jpg', upload_to='cover_photos')
    bio = models.TextField(blank=True, max_length=500)
    status = models.CharField(blank=True, max_length=100)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)
    blocked_users = models.ManyToManyField('self', blank=True, related_name='blocked_by', symmetrical=False)
    following = models.ManyToManyField('self', blank=True, related_name='followers', symmetrical=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Profile"

class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='groups_admin')
    members = models.ManyToManyField(User, through='Membership', related_name='groups_member')

    def __str__(self):
        return self.name
    
class Post(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='posts', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=2000)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def __str__(self):
        return f"Post by {self.author.first_name} {self.author.last_name} on {self.created_at.strftime('%d-%m-%Y')}"
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} likes post by {self.post.author.first_name} {self.post.author.last_name}"
    
class FriendRequest(models.Model):
    sender = models.ForeignKey(User, related_name="sent_friend_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_friend_requests", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Friend request from {self.sender.first_name} {self.sender.last_name} to {self.receiver.first_name} {self.receiver.last_name}"
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return f"Comment by {self.user.first_name} {self.user.last_name} on post by {self.post.author.first_name} {self.post.author.last_name}"




class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} likes comment by {self.comment.user.first_name} {self.comment.user.last_name}"



class Membership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('manager', 'Manager'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name} - {self.role}"
    
class GroupPost(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to='group_posts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_group_posts', blank=True)

    def __str__(self):
        return f"Post by {self.author.username} in {self.group.name}"

    def like_count(self):
        return self.likes.count()

    def is_liked_by_user(self, user):
        return self.likes.filter(id=user.id).exists()

class GroupComment(models.Model):
    post = models.ForeignKey(GroupPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.id}"