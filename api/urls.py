from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    test_api, 
    RegisterView, 
    ProtectedTestView, 
    AnalyzePromptView,
    GeminiChatView,
    PromptLogListView,
    AdminDashboardView,
)

urlpatterns = [
    # Existing Routes
    path('test/', test_api, name='test_api'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected-test/', ProtectedTestView.as_view(), name='protected_test'),
    path('analyze/', AnalyzePromptView.as_view(), name='analyze_prompt'),
    path('chat/', GeminiChatView.as_view(), name='gemini_chat'),
    path('register/', RegisterView.as_view(), name='register'),
    # New Logs Route
    path('logs/', PromptLogListView.as_view(), name='prompt_logs'),

    # admin 
    path('dashboard/',AdminDashboardView.as_view(),name='admin_dashboard'),
] 