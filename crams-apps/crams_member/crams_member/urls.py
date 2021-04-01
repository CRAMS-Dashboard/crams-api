# coding=utf-8
"""
Report URL definitions
"""

from django.conf.urls import url, include
from rest_framework import routers

from crams_member import views

# Viewset URLs
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'project_leader_members', views.ProjectLeaderMemberViewSet)
router.register(r'project_member', views.ProjectMemberViewSet)

urlpatterns = [
    url(r'^', include((router.urls, 'member'), namespace='member')),
    url(r'project_leader_invite',
        views.ProjectLeaderInviteViewSet.as_view()),
    url(r'project_leader_request',
        views.ProjectLeaderRequestViewSet.as_view()),
    url(r'project_member_request',
        views.ProjectMemberRequestViewSet.as_view()),
    url(r'project_member_join',
        views.ProjectMemberJoinViewSet.as_view()),
    url(r'project_join_search',
        views.ProjectJoinSearchViewSet.as_view({'get': 'list'})),
    url(r'project_admin_add_user',
        views.ProjectAdminAddUserViewSet.as_view()),
    url(r'project_leader_set_role',
        views.ProjectLeaderSetRoleViewSet.as_view()),
    url(r'project_member_leave',
        views.ProjectMemberLeaveViewSet.as_view())
]
