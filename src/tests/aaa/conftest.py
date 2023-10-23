from typing import List
import json
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from apps.aaa.models import ICartUser
from apps.permissions.models import RolePermissions
from apps.role.models import Role
from tests.aaa.factories import ICartUserFactory
from tests.role.factories import RoleFactory


@pytest.fixture
def client() -> APIClient:
    """
    * Generate default data in database
    * Generate APIClient

    :return: APIClient
    """
    # ? Generate project errors
    from apps.error.utils.generate_erros import generate_errors

    generate_errors()

    # ? Generate project permissions
    from apps.permissions.utils.generate_permissions import generate_permissions

    generate_permissions()

    # ? Generate project roles
    from apps.role.utils.generate_role import generate_roles

    generate_roles()

    return APIClient()


@pytest.fixture
def create_icart_user():
    """
    * Create New ICart User
        ! Create Django User
        ! Create ICart User

    :return: new icart user
    """

    def _method(username: str, password: str) -> ICartUser:
        user = User.objects.create_user(
            username=username,
            password=password,
            is_active=True,
            is_staff=True,
        )
        icart_user = ICartUserFactory.create(user=user)
        return icart_user

    return _method


@pytest.fixture
def create_user_with_permissions(create_icart_user):
    """
    * Create New ICart User with permissions
        ! Create Django User
        ! Create ICart User
        ! Create Role
            ! Assign Permissions to Role

    :param create_icart_user: fixture for create Django user and ICart user
    :return: new ICart user with role and permissions
    """

    def _method(
        username: str,
        password: str,
        permissions_code_list: List[int],
    ) -> ICartUser:
        # ? Generate Django user and ICart user
        icart_user: ICartUser = create_icart_user(username=username, password=password)

        # * Find permissions
        permissions = RolePermissions.objects.filter(id__in=permissions_code_list)

        # * Create role by Factory
        factory_role = RoleFactory.create()

        # * Assign permissions to role
        role = Role.objects.get(id=factory_role.id)
        role.permissions.set(permissions)

        # * Assign Role to ICart user
        updated_user = ICartUser.objects.filter(id=icart_user.id).first()
        updated_user.role = role
        updated_user.save()

        return updated_user

    return _method


@pytest.fixture
def login_user():
    """
    * Login user

    :return: client
    """

    def _method(username: str, password: str, client: APIClient) -> APIClient:
        response = client.post(
            "/user/login/",
            {"username": username, "password": password},
        )
        data = json.loads(response.content)
        client.credentials(HTTP_AUTHORIZATION="Bearer " + data["access"])
        return client

    return _method
