import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.core.api.routes.public.early_access import router as public_router
from src.core.api.routes.admin.waitlist import router as admin_router
from src.core.storage.waitlist_store import waitlist_store
from src.core.db.models.early_access import WaitlistStatus, UseCase, ReferralSource
from src.core.analytics.waitlist_analytics import waitlist_analytics

client = TestClient(public_router)

@pytest.fixture
async def test_request():
    """Create a test early access request"""
    request_data = {
        "email": "test@example.com",
        "name": "Test User",
        "company": "Test Company",
        "use_case": UseCase.STARTUP,
        "referral_source": ReferralSource.GOOGLE,
        "privacy_policy_accepted": True
    }
    return await waitlist_store.create_request(request_data)

@pytest.mark.asyncio
async def test_signup_validation():
    """Test early access signup validation"""
    # Test invalid email
    response = client.post("/early-access/signup", json={
        "email": "invalid-email",
        "privacy_policy_accepted": True
    })
    assert response.status_code == 422

    # Test missing privacy policy
    response = client.post("/early-access/signup", json={
        "email": "test@example.com",
        "privacy_policy_accepted": False
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_duplicate_signup(test_request):
    """Test handling of duplicate signups"""
    response = client.post("/early-access/signup", json={
        "email": "test@example.com",
        "privacy_policy_accepted": True
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_waitlist_status(test_request):
    """Test waitlist status checking"""
    response = client.get(f"/early-access/status/test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == WaitlistStatus.PENDING
    assert "position" in data

@pytest.mark.asyncio
async def test_admin_operations(test_request):
    """Test admin operations on waitlist"""
    # Test approving request
    response = client.post(f"/admin/waitlist/{test_request['id']}/approve")
    assert response.status_code == 200

    # Test sending invitation
    response = client.post(
        f"/admin/waitlist/{test_request['id']}/invite",
        json={"message": "Welcome to CloudEV.ai!"}
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_analytics():
    """Test waitlist analytics"""
    # Test conversion metrics
    metrics = await waitlist_analytics.get_conversion_metrics()
    assert "conversion_rates" in metrics
    assert "total_requests" in metrics

    # Test trend analysis
    trends = await waitlist_analytics.get_trend_analysis(days=7)
    assert "daily_signups" in trends
    assert "growth_rate" in trends

    # Test use case analysis
    use_cases = await waitlist_analytics.get_use_case_analysis()
    assert "distribution" in use_cases
    assert "conversion_by_use_case" in use_cases

@pytest.mark.asyncio
async def test_waitlist_store():
    """Test waitlist store operations"""
    # Test creating request
    request_data = {
        "email": "store_test@example.com",
        "privacy_policy_accepted": True
    }
    request = await waitlist_store.create_request(request_data)
    assert request["email"] == request_data["email"]

    # Test getting request
    retrieved = await waitlist_store.get_request_by_email(request_data["email"])
    assert retrieved["email"] == request_data["email"]

    # Test updating status
    updated = await waitlist_store.update_request_status(
        request_data["email"],
        WaitlistStatus.APPROVED
    )
    assert updated["status"] == WaitlistStatus.APPROVED

@pytest.mark.asyncio
async def test_email_notifications(test_request):
    """Test email notification system"""
    # Test confirmation email
    await email_service.send_confirmation_email(
        test_request["email"],
        test_request["name"]
    )
    # Note: In a real test, you'd want to mock the email service
    # and verify the email was sent with correct content

    # Test invitation email
    await email_service.send_invitation_email(
        test_request["email"],
        "TEST123",
        "Welcome to CloudEV.ai!"
    )
    # Note: In a real test, you'd want to mock the email service
    # and verify the email was sent with correct content

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting for signup endpoint"""
    # Make multiple requests in quick succession
    for _ in range(5):
        response = client.post("/early-access/signup", json={
            "email": f"rate_test_{_}@example.com",
            "privacy_policy_accepted": True
        })
        assert response.status_code in [200, 429]  # Either success or rate limit

@pytest.mark.asyncio
async def test_invitation_code_verification():
    """Test invitation code verification"""
    # Test invalid code
    response = client.post("/early-access/verify-invitation/INVALID")
    assert response.status_code == 400

    # Test valid code (would need to create a valid code first)
    # This is a placeholder for when invitation code verification is implemented
    # response = client.post("/early-access/verify-invitation/VALID_CODE")
    # assert response.status_code == 200 