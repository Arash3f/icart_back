import pytest
import json
import logging
from apps.error.utils.helper import generate_error_exception
from apps.role.models import Role
from tests.role.factories import RoleFactory

LOGGER = logging.getLogger(__name__)


@pytest.mark.django_db
class TestRoleEndpoints:
    """
    * Test all role app Endpoints
    """

    def test_successfully_get_all_roles(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[2],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create some Role
        role_count = 20
        RoleFactory.create_batch(role_count)

        # ? Get all roles from server
        response = client.get("/role/item/list/")
        data = json.loads(response.content)

        assert data["count"] == role_count + 5 + 1  # hard code for default role
        assert response.status_code == 200
        assert len(data["results"]) == 10

        # ! Page 2
        response2 = client.get(data["next"])
        data2 = json.loads(response2.content)
        assert len(data2["results"]) == 10
        assert response.status_code == 200

        # ! Page 3
        response3 = client.get(data2["next"])
        data3 = json.loads(response3.content)
        assert len(data3["results"]) == 6
        assert response.status_code == 200

    def test_unsuccessfully_get_all_roles_permission_denied(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[1],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        with pytest.raises(Exception) as err:
            client.get("/role/item/list/")

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=2001))

    def test_unsuccessfully_get_all_roles_not_authorization(self, client):
        with pytest.raises(Exception) as err:
            client.get("/role/item/list/")

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=1001))

    def test_successfully_get_one_role(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[2],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create Role
        role_list = RoleFactory.create()

        # ? Get all roles from server
        response = client.get("/role/item/{}/".format(role_list.id))
        data = json.loads(response.content)

        assert data["id"] == role_list.id
        assert data["name"] == role_list.name
        assert response.status_code == 200

    def test_unsuccessfully_get_one_role_permission_denied(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[1],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        with pytest.raises(Exception) as err:
            client.get("/role/item/{}/".format(2))

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=2001))

    def test_unsuccessfully_get_one_role_not_authorization(self, client):
        with pytest.raises(Exception) as err:
            client.get("/role/item/{}/".format(2))

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=1001))

    def test_successfully_delete_role(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[4],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create Role
        new_role = RoleFactory.create()

        # ? Delete role from server
        response = client.delete("/role/item/delete/{}/".format(new_role.id))
        assert response.status_code == 204

        find_role = Role.objects.filter(id=new_role.id).count()
        assert find_role == 0

    def test_unsuccessfully_delete_role_not_found(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[4],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # ? Delete role from server
        response = client.delete("/role/item/delete/{}/".format(4646))
        data = json.loads(response.content)

        assert data["detail"] == "Not found."

    def test_unsuccessfully_delete_role_permission_denied(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[1],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        with pytest.raises(Exception) as err:
            client.delete("/role/item/delete/{}/".format(2))

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=2003))

    def test_unsuccessfully_delete_role_not_authorization(self, client):
        with pytest.raises(Exception) as err:
            client.delete("/role/item/delete/{}/".format(2))

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=1001))

    def test_successfully_create_role(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[3],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create Role
        create_role_data = {
            "name": "admin22",
        }
        response = client.post("/role/item/create/", create_role_data)
        data = json.loads(response.content)
        assert response.status_code == 201
        assert data["name"] == create_role_data["name"]

        find_role = Role.objects.filter(name=data["name"]).count()
        assert find_role == 1

    def test_unsuccessfully_create_role_permission_denied(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[1],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        with pytest.raises(Exception) as err:
            client.post("/role/item/create/", {"name": "test"})

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=2004))

    def test_unsuccessfully_create_role_not_authorization(self, client):
        with pytest.raises(Exception) as err:
            client.post("/role/item/create/", {"name": "test"})

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=1001))

    def test_unsuccessfully_create_role_duplicate_name(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[3],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create Role
        new_role = RoleFactory.create()

        response = client.post("/role/item/create/", {"name": new_role.name})
        data = json.loads(response.content)
        assert data["name"][0] == "role with this name already exists."
        assert response.status_code == 400

    def test_update_role(self, client, login_user, create_user_with_permissions):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[5],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create Role
        new_role = RoleFactory.create()

        # ? Get all roles from server
        update_role_data = {
            "name": "Super",
        }
        response = client.put(
            "/role/item/update/{}/".format(new_role.id),
            update_role_data,
        )
        data = json.loads(response.content)
        assert response.status_code == 200
        assert data["name"] == update_role_data["name"]

        find_new_role = Role.objects.filter(name=update_role_data["name"]).count()
        assert find_new_role == 1

        find_old_role = Role.objects.filter(name=new_role.name).count()
        assert find_old_role == 0

    def test_unsuccessfully_update_role_permission_denied(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[1],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        with pytest.raises(Exception) as err:
            client.put("/role/item/update/{}/".format(2), {"name": "test"})

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=2002))

    def test_unsuccessfully_update_role_not_authorization(self, client):
        with pytest.raises(Exception) as err:
            client.put("/role/item/update/{}/".format(2), {"name": "test"})

        # * Check error
        assert str(err.value) == str(generate_error_exception(error_code=1001))

    def test_update_role_duplicate_name(
        self,
        client,
        login_user,
        create_user_with_permissions,
    ):
        # * Create role with permissions and assign it to user
        password = "test_password"
        icart_user = create_user_with_permissions(
            username="test",
            password=password,
            permissions_code_list=[5],
        )

        # * login user
        client = login_user(icart_user.user.username, password, client)

        # * Create Role
        new_role_list = RoleFactory.create_batch(2)

        # ? Get all roles from server
        update_role_data = {
            "name": new_role_list[1].name,
        }
        response = client.put(
            "/role/item/update/{}/".format(new_role_list[0].id),
            update_role_data,
        )
        data = json.loads(response.content)

        assert data["name"][0] == "role with this name already exists."
        assert response.status_code == 400
