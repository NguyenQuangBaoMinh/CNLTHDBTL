from .models import User, Post, Comment, Reaction


class UserDAO:
    @classmethod
    def get_user_by_id(cls, user_id):
        return User.objects.get(id=user_id)

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        return User.objects.create_user(username=username, email=email, password=password, **kwargs)


class PostDAO:
    @classmethod
    def get_posts(cls, author=None, post_type=None):
        posts = Post.objects.all()
        if author:
            posts = posts.filter(author=author)
        if post_type:
            posts = posts.filter(post_type=post_type)
        return posts

    @classmethod
    def create_post(cls, author, content, post_type, image=None):
        return Post.objects.create(author=author, content=content, post_type=post_type, image=image)


class CommentDAO:
    @classmethod
    def get_comments_for_post(cls, post):
        return Comment.objects.filter(post=post)

    @classmethod
    def create_comment(cls, post, author, content):
        return Comment.objects.create(post=post, author=author, content=content)


class ReactionDAO:
    @classmethod
    def get_reactions_for_post(cls, post):
        return Reaction.objects.filter(post=post)

    @classmethod
    def create_reaction(cls, post, author, reaction_type):
        return Reaction.objects.create(post=post, author=author, reaction_type=reaction_type)