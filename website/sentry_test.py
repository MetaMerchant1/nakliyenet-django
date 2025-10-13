"""
Sentry Test Views - Error tracking test
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

logger = logging.getLogger(__name__)


def sentry_test_error(request):
    """
    Test endpoint - Triggers a test error to Sentry
    URL: /test-sentry-error/
    """
    try:
        # Intentionally cause an error
        result = 1 / 0
    except Exception as e:
        logger.error(f"Test error triggered: {e}")
        raise

    return HttpResponse("This should not be reached")


def sentry_test_success(request):
    """
    Test endpoint - Check if Sentry is configured
    URL: /test-sentry-status/
    """
    import sentry_sdk
    from django.conf import settings

    sentry_configured = bool(settings.SENTRY_DSN if hasattr(settings, 'SENTRY_DSN') else False)
    debug_mode = settings.DEBUG

    # Send test event to Sentry
    if sentry_configured and not debug_mode:
        sentry_sdk.capture_message("Sentry test message from Django", level="info")
        status = "✅ Sentry is ACTIVE and configured"
    elif debug_mode:
        status = "⚠️ Sentry is DISABLED (DEBUG mode)"
    else:
        status = "❌ Sentry DSN not configured"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentry Status</title>
        <style>
            body {{ font-family: monospace; padding: 40px; background: #f5f5f5; }}
            .status {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .success {{ color: #28a745; }}
            .warning {{ color: #ffc107; }}
            .error {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="status">
            <h1>Sentry Configuration Status</h1>
            <h2>{status}</h2>
            <p><strong>Debug Mode:</strong> {debug_mode}</p>
            <p><strong>DSN Configured:</strong> {sentry_configured}</p>
            <hr>
            <p>Test endpoints:</p>
            <ul>
                <li><a href="/test-sentry-error/">Trigger Test Error</a> (will cause 500 error)</li>
                <li><a href="/test-sentry-status/">Check Status</a> (this page)</li>
            </ul>
            <p><small>Check your Sentry dashboard: <a href="https://sentry.io" target="_blank">sentry.io</a></small></p>
        </div>
    </body>
    </html>
    """

    return HttpResponse(html)
