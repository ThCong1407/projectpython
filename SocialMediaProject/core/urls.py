from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('create_post/', views.create_post, name='create_post'),
    path('post/edit/<int:post_id>/', views.edit_post, name='edit_post'),
    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/toggle-like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/add-comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/add-comment/<int:parent_id>/', views.add_comment, name='add_comment_reply'),

    # registration 
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Comment Management URLs
    path('comment/edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('comment/toggle-like/<int:comment_id>/', views.toggle_comment_like, name='toggle_comment_like'),

    # profile URLs
    path('profile/', views.profile_view, name='profile_view'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/search/<int:user_id>/', views.profile_search_view, name='profile_search_view'),
    # Password Change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='core/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='core/password_change_done.html'), name='password_change_done'),
    # Password Reset URLs (with email link or OTP functionality)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='core/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='core/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),

    # search URLS
    path('search/', views.user_search, name='user_search'),

    path('friend/request/send/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('friend/request/accept/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('friend/request/delete/<int:request_id>/', views.delete_friend_request, name='delete_friend_request'),
    path('friend/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('friends/', views.friends_list, name='friends_list'),
    path('friend_requests/', views.friend_requests, name='friend_requests'),
    path('non_friends/', views.non_friends, name='non_friends'),

    path('friend/block/<int:user_id>/', views.block_friend, name='block_friend'),
    path('friend/blocked/', views.list_blocked_friends, name='list_blocked_friends'),
    path('friend/unblock/<int:user_id>/', views.unblock_friend, name='unblock_friend'),

    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

    path('groups/', views.list_groups, name='list_groups'),
    path('groupdetail/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group_request, name='join_group_request'),
    path('group/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/manage_requests/', views.manage_requests, name='manage_requests'),
    path('approve_request/<int:membership_id>/<str:action>/', views.approve_request, name='approve_request'),
    path("create/", views.create_group, name="create_group"),
    path("groups/join/<int:group_id>/", views.join_group, name="join_group"),  
    path('groups/<int:group_id>/remove_member/<int:member_id>/', views.remove_member, name='remove_member'),
    path('group/<int:group_id>/update/', views.update_group, name='update_group'),
    path('group/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('group/<int:group_id>/toggle_membership/', views.toggle_membership, name='toggle_membership'),
    path('group/<int:group_id>/toggle_post_permission/<int:member_id>/', views.toggle_post_permission, name='toggle'),
    path('group/<int:group_id>/view_members/', views.view_members, name='view_group_members'),
    path('groups/<int:group_id>/create_post/', views.create_group_post, name='create_group_post'),
    path('group_post/<int:post_id>/', views.group_post_detail, name='group_post_detail'),
    path('group_post/<int:post_id>/add_comment/', views.group_post_add_comment, name='group_post_add_comment'),
    path('group_post/comment/<int:comment_id>/edit/', views.group_post_edit_comment, name='group_post_edit_comment'),
    path('group_post/comment/<int:comment_id>/delete/', views.group_post_delete_comment, name='group_post_delete_comment'),
    path('group_post/<int:post_id>/toggle_like/', views.toggle_like_group_post, name='toggle_like_group_post'),
    path('group_post/<int:post_id>/edit/', views.edit_group_post, name='edit_group_post'),
    path('group_post/<int:post_id>/delete/', views.delete_group_post, name='delete_group_post'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
