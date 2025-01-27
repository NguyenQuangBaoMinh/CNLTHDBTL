from .models import UserProfile

class AutoCreateUserProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Kiểm tra nếu user đã đăng nhập và chưa có profile
        if request.user.is_authenticated:
            UserProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'bio': '',
                    'graduation_year': None,
                    'company': '',
                    'position': '',
                    'location': ''
                }
            )
        return None