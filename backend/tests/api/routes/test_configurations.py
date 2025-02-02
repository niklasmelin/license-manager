from httpx import AsyncClient
from pytest import mark
from sqlalchemy import select

from lm_backend.api.models.configuration import Configuration
from lm_backend.permissions import Permissions


@mark.asyncio
async def test_add_configuration__success(
    backend_client: AsyncClient,
    inject_security_header,
    read_object,
):
    data = {
        "name": "Abaqus",
        "cluster_client_id": "dummy",
        "grace_time": 60,
        "type": "flexlm",
    }

    inject_security_header("owner1@test.com", Permissions.CONFIG_EDIT)
    response = await backend_client.post("/lm/configurations", json=data)
    assert response.status_code == 201

    stmt = select(Configuration).where(Configuration.name == "Abaqus")
    fetched = await read_object(stmt)

    assert fetched.name == "Abaqus"


@mark.asyncio
async def test_get_all_configurations__success(
    backend_client: AsyncClient,
    inject_security_header,
    create_configurations,
):
    inject_security_header("owner1@test.com", Permissions.CONFIG_VIEW)
    response = await backend_client.get("/lm/configurations")

    assert response.status_code == 200

    response_configurations = response.json()
    assert response_configurations[0]["name"] == create_configurations[0].name
    assert response_configurations[0]["cluster_client_id"] == create_configurations[0].cluster_client_id
    assert response_configurations[0]["grace_time"] == create_configurations[0].grace_time
    assert response_configurations[0]["type"] == create_configurations[0].type

    assert response_configurations[1]["name"] == create_configurations[1].name
    assert response_configurations[1]["cluster_client_id"] == create_configurations[1].cluster_client_id
    assert response_configurations[1]["grace_time"] == create_configurations[1].grace_time
    assert response_configurations[1]["type"] == create_configurations[1].type


@mark.asyncio
async def test_get_all_configurations__with_search(
    backend_client: AsyncClient,
    inject_security_header,
    create_configurations,
):
    inject_security_header("owner1@test.com", Permissions.CONFIG_VIEW)
    response = await backend_client.get(f"/lm/configurations/?search={create_configurations[0].name}")

    assert response.status_code == 200

    response_configuration = response.json()
    assert response_configuration[0]["name"] == create_configurations[0].name
    assert response_configuration[0]["cluster_client_id"] == create_configurations[0].cluster_client_id
    assert response_configuration[0]["grace_time"] == create_configurations[0].grace_time
    assert response_configuration[0]["type"] == create_configurations[0].type


@mark.asyncio
async def test_get_all_configurations__with_sort(
    backend_client: AsyncClient,
    inject_security_header,
    create_configurations,
):

    inject_security_header("owner1@test.com", Permissions.CONFIG_VIEW)
    response = await backend_client.get("/lm/configurations/?sort_field=name&sort_ascending=false")

    assert response.status_code == 200

    response_configurations = response.json()
    assert response_configurations[0]["name"] == create_configurations[1].name
    assert response_configurations[0]["cluster_client_id"] == create_configurations[1].cluster_client_id
    assert response_configurations[0]["grace_time"] == create_configurations[1].grace_time
    assert response_configurations[0]["type"] == create_configurations[1].type

    assert response_configurations[1]["name"] == create_configurations[0].name
    assert response_configurations[1]["cluster_client_id"] == create_configurations[0].cluster_client_id
    assert response_configurations[1]["grace_time"] == create_configurations[0].grace_time
    assert response_configurations[1]["type"] == create_configurations[0].type


@mark.asyncio
async def test_get_configuration__success(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
):
    id = create_one_configuration[0].id

    inject_security_header("owner1@test.com", Permissions.CONFIG_VIEW)
    response = await backend_client.get(f"/lm/configurations/{id}")

    assert response.status_code == 200

    response_configuration = response.json()
    assert response_configuration["name"] == create_one_configuration[0].name
    assert response_configuration["cluster_client_id"] == create_one_configuration[0].cluster_client_id
    assert response_configuration["grace_time"] == create_one_configuration[0].grace_time
    assert response_configuration["type"] == create_one_configuration[0].type


@mark.parametrize(
    "id",
    [
        0,
        -1,
        999999999,
    ],
)
@mark.asyncio
async def test_get_configuration__fail_with_bad_parameter(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
    id,
):
    inject_security_header("owner1@test.com", Permissions.CONFIG_VIEW)
    response = await backend_client.get(f"/lm/configurations/{id}")

    assert response.status_code == 404


@mark.asyncio
async def test_update_configuration__success(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
    read_object,
):
    new_configuration = {
        "name": "New Abaqus",
    }

    id = create_one_configuration[0].id

    inject_security_header("owner1@test.com", Permissions.CONFIG_EDIT)
    response = await backend_client.put(f"/lm/configurations/{id}", json=new_configuration)

    assert response.status_code == 200

    stmt = select(Configuration).where(Configuration.id == id)
    fetch_configuration = await read_object(stmt)

    assert fetch_configuration.name == new_configuration["name"]


@mark.parametrize(
    "id",
    [
        0,
        -1,
        999999999,
    ],
)
@mark.asyncio
async def test_update_configuration__fail_with_bad_parameter(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
    read_object,
    id,
):
    new_configuration = {
        "name": "New Abaqus",
    }

    inject_security_header("owner1@test.com", Permissions.CONFIG_EDIT)
    response = await backend_client.put(f"/lm/configurations/{id}", json=new_configuration)

    assert response.status_code == 404


@mark.asyncio
async def test_update_configuration__fail_with_bad_data(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
    read_object,
):
    new_configuration = {
        "bla": "bla",
    }

    id = create_one_configuration[0].id

    inject_security_header("owner1@test.com", Permissions.CONFIG_EDIT)
    response = await backend_client.put(f"/lm/configurations/{id}", json=new_configuration)

    assert response.status_code == 400


@mark.asyncio
async def test_delete_configuration__success(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
    read_object,
):
    id = create_one_configuration[0].id

    inject_security_header("owner1@test.com", Permissions.CONFIG_EDIT)
    response = await backend_client.delete(f"/lm/configurations/{id}")

    assert response.status_code == 200
    stmt = select(Configuration).where(Configuration.id == id)
    fetch_configuration = await read_object(stmt)

    assert fetch_configuration is None


@mark.parametrize(
    "id",
    [
        0,
        -1,
        999999999,
    ],
)
@mark.asyncio
async def test_delete_configuration__fail_with_bad_parameter(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
    id,
):
    inject_security_header("owner1@test.com", Permissions.CONFIG_EDIT)
    response = await backend_client.delete(f"/lm/configurations/{id}")

    assert response.status_code == 404


@mark.asyncio
async def test_get_configurations_by_client_id__success(
    backend_client: AsyncClient,
    inject_security_header,
    create_one_configuration,
):
    id = create_one_configuration[0].id
    cluster_client_id = create_one_configuration[0].cluster_client_id

    inject_security_header("owner@test1.com", Permissions.CONFIG_VIEW, client_id="not-the-correct-client-id")
    response = await backend_client.get("/lm/configurations/by_client_id")

    assert response.status_code == 200
    assert response.json() == []

    inject_security_header("owner@test1.com", Permissions.CONFIG_VIEW, client_id=cluster_client_id)
    response = await backend_client.get("/lm/configurations/by_client_id")

    response_configurations = response.json()

    assert response.status_code == 200
    assert response_configurations[0]["id"] == id
    assert response_configurations[0]["name"] == create_one_configuration[0].name
    assert response_configurations[0]["cluster_client_id"] == create_one_configuration[0].cluster_client_id
    assert response_configurations[0]["grace_time"] == create_one_configuration[0].grace_time
    assert response_configurations[0]["type"] == create_one_configuration[0].type
