from django.conf.urls import url, include
from rest_framework import routers

from crams_review.views.review_date import ReviewDateView
from crams_review.views.review_send import ReviewSendView
from crams_review.views.review_skip import ReviewSkipView

router = routers.SimpleRouter(trailing_slash=True)
router.register(r'review_date', ReviewDateView)
router.register(r'send', ReviewSendView)
router.register(r'skip', ReviewSkipView)

urlpatterns = [
    url(r'^', include((router.urls, 'review'), namespace='review')),
]
