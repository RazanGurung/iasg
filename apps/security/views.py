import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

logger = logging.getLogger("apps.security.reveal")


@login_required
def reveal(request, field_id):
    # Placeholder only: real decrypt-and-audit wiring lands when apps.security
    # is built out (see docs/security.md). This just logs who asked for what.
    logger.info("reveal requested field_id=%s user=%s", field_id, request.user)
    return HttpResponse(
        '<span class="protected open">Not built yet: '
        f'{field_id} <span class="tag">viewed, logged</span></span>'
    )
