from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Author(models.Model):
    rating_author = models.IntegerField(default=0)

    user_one_to_one = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author')

    def update_rating(self):
        posts_rating = sum(post.rating_post * 3 for post in self.post_set.all())
        comments_rating = sum(comment.rating_comment for post in self.post_set.all() for comment in post.comment_set.all())
        author_comments_rating = sum(comment.rating_comment for comment in Comment.objects.filter(user_one_to_many=self.user_one_to_one))

        self.rating_author = posts_rating + comments_rating + author_comments_rating
        self.save()

    # Определяет то, как будет выведена информация
    def __str__(self):
         return f'{self.user_one_to_one.username}'

class Category(models.Model):
    name_category = models.CharField(max_length=50, unique=True)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return f'{self.name_category}'


class CategoryUser(models.Model):
    user_one_to_many = models.ForeignKey(User, on_delete=models.CASCADE)
    category_one_to_many = models.ForeignKey(Category, on_delete=models.CASCADE)


class Post(models.Model):
    add_post = models.DateTimeField(auto_now_add=True)
    title_post = models.CharField(max_length=100)
    text_post = models.TextField()
    rating_post = models.IntegerField(default=0)

    post_choice_type = [
        ('post', 'post'),
        ('news', 'news')
    ]

    post_choice = models.CharField(choices=post_choice_type, max_length=10)

    author_one_to_many = models.ForeignKey(Author, on_delete=models.CASCADE)
    category_many_to_many = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.rating_post += 1
        self.save()

    def dislike(self):
        self.rating_post -= 1
        self.save()

    def preview(self):
        if len(self.text_post) > 124:
            return self.text_post[:124] + '...'
        else:
            return self.text_post

    def __str__(self):
        return f'{self.add_post}+{self.text_post}+{self.text_post}+{self.rating_post}+{self.post_choice}'

    def get_absolute_url(self):
        return reverse('news_detail', args=[str(self.pk)])


class PostCategory(models.Model):
    post_oto_to_many = models.ForeignKey(Post, on_delete=models.CASCADE)
    category_ote_to_many = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_text = models.TextField()
    comment_datatime = models.DateTimeField(auto_now_add=True)
    rating_comment = models.IntegerField(default=0)

    post_one_to_many = models.ForeignKey(Post, on_delete=models.CASCADE)
    user_one_to_many = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating_comment += 1
        self.save()

    def dislike(self):
        self.rating_comment -= 1
        self.save()

    def __str__(self):
        return f'{self.comment_text}+{self.comment_datatime}+{self.rating_comment}'


class Appointment(models.Model):
    appointment_date = models.DateTimeField(auto_now_add=True)
    appointment_name = models.CharField(max_length=100)
    appointment_message = models.TextField()

    def __str__(self):
        return f'{self.appointment_name}: {self.appointment_message}'