from django.urls import path
from .views import *

urlpatterns = [
    path('', NewsPost.as_view(), name='post_list'),
    path('<int:pk>', NewsDetail.as_view(), name='news_detail'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('news/create/', PostCreate.as_view(), name='post_create'),
    path('news/<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('post/create/', PostCreate.as_view(), name='post_create'),
    path('post/<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
]