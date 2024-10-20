from django.urls import path
from .views import custom_login, register, success_login, success_register, comments_view, delete_comment_view, logout_view, audit_log_view
urlpatterns = [
    path('login/', custom_login, name='login'),
    path('register/', register, name='register'),
    path('success-login/', success_login, name='success_login'),
    path('success-register/', success_register, name='success_register'),
    path('comments/', comments_view, name='comments'),
    path('logout/', logout_view, name='logout'),
    path('delete-comment/<int:comment_id>/', delete_comment_view, name='delete_comment'),
    path('audit-log/', audit_log_view, name='audit_log'),

]
