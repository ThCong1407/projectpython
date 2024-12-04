from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CommentForm, GroupCommentForm, GroupForm, GroupPostForm, UserRegisterForm, ProfileEditForm, CustomPasswordChangeForm, PostForm, UserEditForm, ProfileAttributesForm, UserSearchForm
from .models import CommentLike, FriendRequest, Group, GroupComment, GroupPost, Like, Membership, Profile, Post, Comment
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse



def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

def profile_view(request, user_id=None):  
    # Check if user_id matches the logged-in user to avoid self-redirects
    if user_id and user_id == request.user.id:
        return redirect('profile_view')  # Redirect to their own profile without fetching again
    
    # Get the user based on the provided ID, or default to the current user
    user = get_object_or_404(User, id=user_id) if user_id else request.user
    posts = Post.objects.filter(author=user).order_by('-created_at')
    
    user_profile = user.profile
    
    # Get the number of friends and followers
    num_friends = user_profile.friends.count()
    num_followers = user_profile.followers.count()
    num_following = user_profile.following.count()
    
    context = {
        'user_profile': user_profile,
        'num_friends': num_friends,
        'num_followers': num_followers,
        'num_following': num_following,
        'posts': posts,
    }
    return render(request, 'core/profile_view.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        u_form = UserEditForm(request.POST, instance=request.user)
        p_form = ProfileEditForm(request.POST, instance=request.user.profile)
        p_attr_form = ProfileAttributesForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid() and p_attr_form.is_valid():
            u_form.save()
            p_form.save()
            p_attr_form.save()
            return redirect('profile_view')
    else:
        u_form = UserEditForm(instance=request.user)
        p_form = ProfileEditForm(instance=request.user.profile)
        p_attr_form = ProfileAttributesForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'p_attr_form': p_attr_form,
    }
    return render(request, 'core/profile_edit.html', context)

def user_login(request):
    # Check if the user is redirected to login due to `@login_required`
    if 'next' in request.GET:
        messages.info(request, "Please log in to access this page.")

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to the original page or 'feed' if there's no next parameter
            next_url = request.GET.get('next', 'feed')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'core/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Đảm bảo người dùng không bị đăng xuất
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'core/change_password.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('feed')
    else:
        form = PostForm()
    return render(request, 'core/create_post.html', {'form': form})

def feed(request):
    posts = Post.objects.filter(group__isnull=True).order_by('-created_at')
    return render(request, 'core/feed.html', {'posts': posts})

def user_search(request):
    form = UserSearchForm(request.GET or None)
    results = []
    query = ""

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            # Use Q objects to search by first_name or last_name or both
            results = User.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query)
            )

    context = {
        'form': form,
        'results': results,
        'query': query,
    }
    return render(request, 'core/user_search.html', context)

def profile_search_view(request, user_id):
    searched_user = get_object_or_404(User, id=user_id)
    
    # Check if the searched user is the same as the logged-in user
    if searched_user == request.user:
        # Render profile_view directly without redirect
        posts = Post.objects.filter(author=request.user).order_by('-created_at')
        return render(request, 'core/profile_view.html', {'user': request.user, 'posts': posts})
    
    # Fetch posts by the searched user if it’s not the current user
    posts = Post.objects.filter(author=searched_user).order_by('-created_at')

    # Get the profile of the searched user
    user_profile = searched_user.profile

    # Get the number of friends, followers, and following
    num_friends = user_profile.friends.count()
    num_followers = user_profile.followers.count()
    num_following = user_profile.following.count()

    context = {
        'searched_user': searched_user,
        'num_friends': num_friends,
        'num_followers': num_followers,
        'num_following': num_following,
        'posts': posts,
    }
    return render(request, 'core/profile_search.html', context)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)  # Ensure user owns the post
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('profile_view')
    else:
        form = PostForm(instance=post)
    return render(request, 'core/edit_post.html', {'form': form})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)  # Ensure user owns the post
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('profile_view')
    return render(request, 'core/delete_post.html', {'post': post})


@login_required
def delete_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    friend_request.delete()
    messages.success(request, "Friend request deleted.")
    return redirect('friend_requests')

@login_required
def remove_friend(request, user_id):
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Retrieve the logged-in user's profile
    request_profile = request.user.profile
    
    # Check if the user to remove is actually a friend
    if request_profile.friends.filter(id=user_to_remove.id).exists():
        request_profile.friends.remove(user_to_remove)
        # Assuming friendship is bidirectional
        user_to_remove.profile.friends.remove(request.user)
        messages.success(request, f"You have unfriended {user_to_remove.username}")
    else:
        messages.info(request, f"{user_to_remove.username} is not in your friends list.")
    
    return redirect('friends_list')



@login_required
def friends_list(request):
    # Retrieve the logged-in user's friends
    friends = request.user.profile.friends.all()  # Assuming `friends` is a M2M field in Profile
    return render(request, 'core/friends_list.html', {'friends': friends})


@login_required
def friend_requests(request):
    requests = FriendRequest.objects.filter(receiver=request.user)
    return render(request, 'core/friend_requests.html', {'requests': requests})

@login_required
def non_friends(request):
    # Get the logged-in user's profile
    user_profile = request.user.profile

    # Retrieve all users who are friends with the logged-in user (bidirectional)
    friend_ids = user_profile.friends.values_list('id', flat=True)
    reverse_friend_ids = User.objects.filter(profile__friends__id=request.user.id).values_list('id', flat=True)

    # Combine both sets of friends (uniquely)
    all_friend_ids = set(friend_ids) | set(reverse_friend_ids)

    # Get all users who are not friends, exclude the current user, and exclude admin users
    non_friends = User.objects.exclude(id__in=all_friend_ids).exclude(id=request.user.id).exclude(is_staff=True)

    return render(request, 'core/non_friends.html', {'non_friends': non_friends})

@login_required
def send_friend_request(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    
    # Prevent self-friend request
    if receiver == request.user:
        messages.error(request, "You cannot send a friend request to yourself.")
        return redirect('profile_view')

    # Create friend request if not already sent
    friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    if created:
        messages.success(request, f"Friend request sent to {receiver.username}")
    else:
        messages.info(request, "Friend request already sent.")
    
    # Redirect to the receiver's profile search view
    return redirect('non_friends')


@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, receiver=request.user)
    
    # Add the sender (User) to the receiver's (request.user) friends list
    request.user.profile.friends.add(friend_request.sender)
    
    # Add the receiver (request.user) to the sender's friends list
    friend_request.sender.profile.friends.add(request.user)
    
    # Delete the friend request after accepting it
    friend_request.delete()
    
    messages.success(request, f"You are now friends with {friend_request.sender.username}")
    return redirect('friend_requests')

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()  # Unlike the post if it was already liked

    return JsonResponse({'like_count': post.like_count(), 'liked': created})

@login_required
def add_comment(request, post_id, parent_id=None):
    post = get_object_or_404(Post, id=post_id)
    parent_comment = None

    # If a parent ID is provided, fetch the parent comment
    if parent_id:
        parent_comment = get_object_or_404(Comment, id=parent_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user  # Correctly assign the logged-in user
            comment.post = post
            comment.parent = parent_comment  # Set parent comment if it's a reply
            comment.save()
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()

    return render(request, 'core/post_detail.html', {'post': post, 'form': form})

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Comment updated successfully!")
            return redirect('post_detail', post_id=comment.post.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'core/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post_id = comment.post.id
    comment.delete()
    messages.success(request, "Comment deleted successfully!")
    return redirect('post_detail', post_id=post_id)

@login_required
def toggle_comment_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)

    if not created:
        # If a like already exists, remove it (unlike)
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        'like_count': comment.likes.count(),
        'liked': liked
    })

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    # Retrieve only root comments (parent is null)
    root_comments = post.comments.filter(parent__isnull=True).select_related('user')
    return render(request, 'core/post_detail.html', {
        'post': post,
        'form': form,
        'root_comments': root_comments  # Pass root comments to the template
    })

def group_post_detail(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    form = GroupCommentForm()
    # Retrieve only root comments (parent is null)
    comments = GroupComment.objects.filter(post=post).select_related('author')
    
    # Add a flag to the post indicating if the current user has liked it
    post.is_liked = post.likes.filter(id=request.user.id).exists()
    
    return render(request, 'core/group_post_detail.html', {
        'post': post,
        'form': form,
        'comments': comments,  # Pass comments to the template
    })

@login_required
def block_friend(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)
    request_user_profile = request.user.profile

    # Kiểm tra xem người dùng có đang cố gắng block chính họ không
    if user_to_block == request.user:
        messages.error(request, "You cannot block yourself.")
    elif user_to_block in request_user_profile.blocked_users.all():
        messages.info(request, f"{user_to_block.username} is already blocked.")
    else:
        # Thêm người dùng vào danh sách blocked
        request_user_profile.blocked_users.add(user_to_block.profile)
        
        # Loại bỏ người dùng khỏi danh sách bạn bè
        request_user_profile.friends.remove(user_to_block)  # Chú ý là xóa user_to_block (không phải profile)
        
        messages.success(request, f"You have blocked {user_to_block.username}.")

    return redirect('friends_list')  # Redirect to an appropriate page

@login_required
def list_blocked_friends(request):
    blocked_users = request.user.profile.blocked_users.all()
    return render(request, 'core/blocked_friends_list.html', {'blocked_users': blocked_users})

@login_required
def unblock_friend(request, user_id):
    user_to_unblock = get_object_or_404(User, id=user_id)
    request_user_profile = request.user.profile
    user_to_unblock_profile = get_object_or_404(Profile, user=user_to_unblock)

    # Kiểm tra xem người dùng có bị block không
    if user_to_unblock_profile in request_user_profile.blocked_users.all():
        # Thực hiện unblock
        request_user_profile.blocked_users.remove(user_to_unblock_profile)
        messages.success(request, f"You have unblocked {user_to_unblock.username}.")
    else:
        # Thông báo nếu người dùng không nằm trong danh sách block
        messages.error(request, f"{user_to_unblock.username} is not in your blocked list.")

    return redirect('list_blocked_friends')  # Điều hướng lại danh sách blocked users

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request_user_profile = request.user.profile

    if user_to_follow == request.user:
        messages.error(request, "You cannot follow yourself.")
    elif user_to_follow.profile in request_user_profile.following.all():
        messages.info(request, f"You are already following {user_to_follow.username}.")
    else:
        request_user_profile.following.add(user_to_follow.profile)
        user_to_follow.profile.followers.add(request.user.profile)
        messages.success(request, f"You are now following {user_to_follow.username}.")

    return redirect('profile_search_view', user_id=user_to_follow.id)

@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request_user_profile = request.user.profile

    if user_to_unfollow.profile in request_user_profile.following.all():
        request_user_profile.following.remove(user_to_unfollow.profile)
        user_to_unfollow.profile.followers.remove(request.user.profile)
        messages.success(request, f"You have unfollowed {user_to_unfollow.username}.")
    else:
        messages.info(request, f"You are not following {user_to_unfollow.username}.")

    return redirect('profile_search_view', user_id=user_to_unfollow.id)

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect(reverse('list_groups')) 

@login_required
def update_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.name = request.POST.get('name')
    group.description = request.POST.get('description')
    group.save()
    return redirect(reverse('group_detail', args=[group_id]))    
# Hiển thị danh sách tất cả các nhóm
def list_groups(request):
    try:
        groups = Group.objects.all()
        return render(request, 'core/group_list.html', {'groups': groups})
    except UnicodeDecodeError as e:
        return HttpResponse(f"Lỗi mã hóa: {e}", status=500)


@login_required
def join_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership, created = Membership.objects.get_or_create(user=request.user, group=group)
    membership.approved = False  # This field should match the model definition
    membership.save()
    return redirect("list_groups")

@login_required
def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            messages.success(request, "Group created successfully!")
            return redirect("list_groups")  # Redirect to the list of groups after creation
    else:
        form = GroupForm()
    return render(request, "core/create_group.html", {"form": form})


@login_required
def toggle_post_permission(request, group_id, member_id):
    group = get_object_or_404(Group, id=group_id)
    member = get_object_or_404(Membership, id=member_id, group=group)

    if request.user == group.creator:  # Chỉ admin mới có quyền thay đổi
        # Đảo ngược giá trị của can_post
        member.can_post = not member.can_post
        member.save()

    return redirect(reverse('view_group_members', args=[group.id]))



def toggle_membership(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    
    # Kiểm tra nếu người dùng đã là thành viên của nhóm
    if request.user in group.members.all():
        # Nếu là thành viên, xóa họ khỏi nhóm (hủy tham gia)
        group.members.remove(request.user)
        action = 'left'
    else:
        # Nếu không phải thành viên, thêm họ vào nhóm (tham gia)
        group.members.add(request.user)
        action = 'joined'
    
    # Nếu bạn muốn trả về JSON và vẫn chuyển hướng, bạn có thể làm như sau:
    # Trả về phản hồi JSON với trạng thái
    response_data = {'status': 'success', 'action': action}
    
    # Chuyển hướng về group_list
    return redirect(reverse('list_groups')) 


@login_required
def view_members(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = Membership.objects.filter(group=group, approved=True)

    return render(request, 'core/view_members.html', {
        'group': group,
        'members': members,
    })
# Hiển thị trang chi tiết nhóm với các bài viết ngẫu nhiên


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    # Check if the user is a member and has been approved
    can_post = Membership.objects.filter(group=group, user=request.user, approved=True).exists()
    # Get all posts associated with this group
    group_posts = GroupPost.objects.filter(group=group)
    
    # Add a flag to each post indicating if the current user has liked it
    for post in group_posts:
        post.is_liked = post.likes.filter(id=request.user.id).exists()
    
    return render(request, 'core/group_detail.html', {
        'group': group,
        'can_post': can_post,
        'posts': group_posts,  # Display group posts
    })
# Gửi yêu cầu tham gia nhóm
@login_required
def join_group_request(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership, created = Membership.objects.get_or_create(user=request.user, group=group)
    if created:
        messages.success(request, "Yêu cầu tham gia đã được gửi!")
    else:
        messages.warning(request, "Bạn đã gửi yêu cầu hoặc là thành viên của nhóm này!")
    return redirect('group_detail', group_id=group_id)

# Quản lý yêu cầu tham gia nhóm của admin
@login_required
def manage_requests(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.user != group.creator:
        messages.error(request, "Bạn không phải admin của nhóm này!")
        return redirect('list_groups')
    
    requests = Membership.objects.filter(group=group, approved=False)
    return render(request, 'core/manage_requests.html', {'group': group, 'requests': requests})

# Chấp nhận hoặc từ chối yêu cầu
@login_required
def approve_request(request, membership_id, action):
    membership = get_object_or_404(Membership, id=membership_id)
    if request.user != membership.group.creator:
        messages.error(request, "Bạn không có quyền thực hiện thao tác này!")
        return redirect('manage_requests', group_id=membership.group.id)

    if action == 'approve':
        membership.approved = True
        membership.save()
        messages.success(request, f"Đã chấp nhận yêu cầu từ {membership.user.username}.")
    elif action == 'deny':
        membership.delete()
        messages.success(request, f"Đã từ chối yêu cầu từ {membership.user.username}.")
    
    return redirect('manage_requests', group_id=membership.group.id)


def remove_member(request, group_id, member_id):
    # Kiểm tra nếu người dùng có quyền xóa thành viên
    membership = get_object_or_404(Membership, id=member_id, group_id=group_id)
    membership.delete()
    return redirect('view_group_members', group_id=group_id)

@login_required
def create_group_post(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == "POST":
        form = GroupPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.group = group
            post.author = request.user
            post.save()
            messages.success(request, "Post created successfully!")
            return redirect('group_detail', group_id=group.id)
    else:
        form = GroupPostForm()
    return render(request, 'core/create_group_post.html', {'form': form, 'group': group})

@login_required
def group_post_add_comment(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    if request.method == "POST":
        form = GroupCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    else:
        form = GroupCommentForm()

    return render(request, 'core/group_post_detail.html', {'post': post, 'form': form})

@login_required
def group_post_edit_comment(request, comment_id):
    comment = get_object_or_404(GroupComment, id=comment_id)
    if request.user != comment.author:
        return redirect('group_post_detail', post_id=comment.post.id)

    if request.method == "POST":
        form = GroupCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('group_post_detail', post_id=comment.post.id)
    else:
        form = GroupCommentForm(instance=comment)

    return render(request, 'core/edit_group_comment.html', {'form': form, 'comment': comment})

@login_required
def group_post_delete_comment(request, comment_id):
    comment = get_object_or_404(GroupComment, id=comment_id)
    if request.user != comment.author:
        return redirect('group_post_detail', post_id=comment.post.id)

    if request.method == "POST":
        post_id = comment.post.id
        comment.delete()
        return redirect('group_post_detail', post_id=post_id)

    return render(request, 'core/delete_group_comment.html', {'comment': comment})

@login_required
def toggle_like_group_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('group_post_detail', post_id=post.id)

@login_required
def edit_group_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    if request.user != post.author:
        return redirect('group_post_detail', post_id=post.id)

    if request.method == "POST":
        form = GroupPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect('group_post_detail', post_id=post.id)
    else:
        form = GroupPostForm(instance=post)

    return render(request, 'core/edit_group_post.html', {'form': form, 'post': post})

@login_required
def delete_group_post(request, post_id):
    post = get_object_or_404(GroupPost, id=post_id)
    if request.user != post.author:
        return redirect('group_post_detail', post_id=post.id)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully!")
        return redirect('group_detail', group_id=post.group.id)

    return render(request, 'core/delete_group_post.html', {'post': post})

@login_required
def leave_group(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    membership = get_object_or_404(Membership, user=request.user, group=group)

    if request.method == "POST":
        membership.delete() 
        messages.success(request, f"You have left the group {group.name}.")
        return redirect('list_groups')

    return render(request, 'core/leave_group.html', {'group': group})