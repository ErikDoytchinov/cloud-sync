import cloud_sync.api.make_httpx_client as mkclient
from cloud_sync.get_zivver_api_url import get_zivver_api_url
from cloud_sync.models.scim.scim_user_response import ScimUserResponse
from cloud_sync.version import __version__


async def get_scim_users(api_key: str) -> ScimUserResponse:
    async with mkclient.make_httpx_client() as client:
        response = await client.get(
            get_zivver_api_url() + "/scim/v2/Users",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-Version": "CloudSync/" + __version__,
            },
        )
    return ScimUserResponse(**response.json())
