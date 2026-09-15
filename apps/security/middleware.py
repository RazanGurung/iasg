class AuditMiddleware:
    """Placeholder for the read-audit trail.

    The Safeguards Rule expects a record of who accessed customer information,
    not just who changed it. Reveals of protected fields (SSN, DL, DOB,
    routing, account, portal credentials) are logged here.

    See docs/security.md. Never log the value itself.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)
