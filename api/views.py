
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import PromptLog
from .serializers import RegisterSerializer, UserSerializer, PromptLogSerializer
from .security import analyze_prompt_security, redact_pii,guard_ai_output
from .gemini import generate_gemini_response
from .models import PromptLog


# Test API
@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    return Response({
        "status": "success",
        "message": "PromptArmor API is working"
    })


# User Registration
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "User registered successfully",
                    "user": UserSerializer(user).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


# Protected Test Endpoint
class ProtectedTestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "status": "success",
                "message": "Authenticated successfully!",
                "user": request.user.username,
                "email": request.user.email
            },
            status=status.HTTP_200_OK
        )


# Prompt Security Analysis
class AnalyzePromptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt", "")

        if not prompt or not isinstance(prompt, str):
            return Response(
                {
                    "error": "Field 'prompt' is required and must be a string."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        # Analyze prompt security
        analysis_result = analyze_prompt_security(prompt)

        # Save scan log in database
        PromptLog.objects.create(
            user=request.user,
            prompt=prompt,
            decision=analysis_result["status"],
            risk_score=analysis_result["risk_score"],
            triggers=analysis_result["triggers"]
        )

        return Response(
            {
                "status": "success",
                "analysis": analysis_result
            },
            status=status.HTTP_200_OK
        )

class GeminiChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt", "")

        if not prompt or not isinstance(prompt, str):
            return Response(
                {
                    "error": "Field 'prompt' is required and must be a string."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Analyze the original prompt for security risks
        security_analysis = analyze_prompt_security(prompt)

        # 2. Save security log in database
        PromptLog.objects.create(
            user=request.user,
            prompt=prompt,
            decision=security_analysis["status"],
            risk_score=security_analysis["risk_score"],
            triggers=security_analysis["triggers"]
        )

        # 3. Block malicious prompts immediately
        if security_analysis["status"] == "BLOCK":
            return Response(
                {
                    "status": "blocked",
                    "message": "Prompt blocked due to security risk.",
                    "security_analysis": security_analysis,
                    "pii_redaction": {
                        "detected": [],
                        "redacted": False
                    },
                    "ai_response": None
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # 4. Detect and redact PII from the input prompt
        pii_result = redact_pii(prompt)
        safe_prompt = pii_result["sanitized_text"]

        # 5. Send the sanitized prompt to Gemini API
        gemini_result = generate_gemini_response(safe_prompt)

        # 6. Handle AI API errors gracefully
        if not gemini_result["success"]:
            return Response(
                {
                    "status": "error",
                    "message": "AI service is temporarily unavailable.",
                    "security_analysis": security_analysis,
                    "pii_redaction": {
                        "detected": pii_result["pii_detected"],
                        "redacted": bool(pii_result["pii_detected"])
                    }
                },
                status=status.HTTP_502_BAD_GATEWAY
            )

        # 7. Check AI generated output for sensitive data using Output Guard
        output_result = guard_ai_output(gemini_result["text"])

        # 8. Return the final successful response with all security details
        return Response(
            {
                "status": "success",
                "security_analysis": security_analysis,
                "pii_redaction": {
                    "detected": pii_result["pii_detected"],
                    "redacted": bool(pii_result["pii_detected"])
                },
                "ai_output_guard": {
                    "pii_detected": output_result["pii_detected"],
                    "output_modified": output_result["output_modified"]
                },
                "ai_response": output_result["safe_output"]
            },
            status=status.HTTP_200_OK
        )
# View Logs for the Logged-in User Only
class PromptLogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = PromptLog.objects.filter(
            user=request.user
        ).order_by('-timestamp')

        serializer = PromptLogSerializer(logs, many=True)

        return Response(
            {
                "status": "success",
                "count": logs.count(),
                "logs": serializer.data
            },
            status=status.HTTP_200_OK
        )
# Admin dashboard api

class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access required."},
                status=status.HTTP_403_FORBIDDEN
            )

        total_requests = PromptLog.objects.count()
        safe_requests = PromptLog.objects.filter(decision="SAFE").count()
        blocked_requests = PromptLog.objects.filter(decision="BLOCK").count()

        return Response({
            "status": "success",
            "dashboard": {
                "total_requests": total_requests,
                "safe_requests": safe_requests,
                "blocked_requests": blocked_requests,
                "security_incidents": blocked_requests
            }
        }, status=status.HTTP_200_OK)
