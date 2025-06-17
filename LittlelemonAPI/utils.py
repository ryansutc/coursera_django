from django.contrib.auth.models import User


def get_best_delivery_person(orders):
    """
    Given a list of orders, return the delivery person (user) with the least orders.
    """
    from collections import Counter

    if not orders:
        return None

    delivery_users = User.objects.filter(groups__name="delivery").prefetch_related(
        "groups"
    )
    user_ids = [order.user.id for order in orders]
    least_common_user_id = Counter(user_ids).most_common()[-1]

    for delivery_user in delivery_users:
        if delivery_user.id not in user_ids:
            return delivery_user

    return User.objects.get(id=least_common_user_id)
