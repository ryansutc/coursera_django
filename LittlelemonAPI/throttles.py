from rest_framework.throttling import UserRateThrottle


class TenCallsPerMinute(UserRateThrottle):
    """
    A simple throttle that allows 10 calls per minute.
    """

    scope = "ten"
