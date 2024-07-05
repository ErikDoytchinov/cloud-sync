import cloud_sync.api.make_httpx_client as mkclient
from cloud_sync.get_zivver_api_url import get_zivver_api_url
from cloud_sync.models.scim.scim_groups_response import ScimGroupResponse
from cloud_sync.version import __version__


async def get_scim_groups(api_key: str) -> ScimGroupResponse:
    async with mkclient.make_httpx_client() as client:
        response = await client.get(
            get_zivver_api_url() + "/scim/v2/Groups",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-Version": "CloudSync/" + __version__,
            },
        )
    return ScimGroupResponse(**response.json())
