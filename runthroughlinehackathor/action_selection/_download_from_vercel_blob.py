import requests
from runthroughlinehackathor.settings import settings


def download_from_vercel_blob(filename: str) -> str:
    """
    Download a file from Vercel Blob (synchronously).

    Args:
        filename: The blob filename or key, e.g. "myfolder/image.png"

    Returns:
        The file content as str.
    """
    url = f"{settings.VERCEL_BLOB_URL}/{filename}"
    headers = {
        "Authorization": (
            f"Bearer {settings.BLOB_READ_WRITE_TOKEN.get_secret_value()}"
        )
    }

    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    content = response.content.decode()

    return content
