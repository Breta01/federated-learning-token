"""Module for storing and managing data files at IPFS/Filecoin using web3.storage."""
import asyncio
import os

import aiofiles
import httpx

from felt.core.web3 import decrypt_bytes


async def ipfs_upload_file(file):
    """Upload file to IPFS using web3.storage.

    Args:
        file: file-like object in byte mode.

    Returns:
        Response: httpx response object
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.post(
            f"https://api.web3.storage/upload",
            headers={"Authorization": "Bearer " + os.environ["WEB3_STORAGE_TOKEN"]},
            files={"file": file},
        )

    return res


async def ipfs_download_file(cid, output_path=None, secret=None):
    """Download file stored in IPFS.

    Args:
        cid (str): string describing location of the file.
        output_path (Optiona[str]): if set file will be stored at this path.

    Returns:
        Response: httpx response object
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        for _ in range(5):
            try:
                res = await client.get(
                    f"https://{cid}.ipfs.dweb.link/",
                )
            except httpx.ReadTimeout:
                print("Connection timeout - retry")
                await asyncio.sleep(5)

    content = res.content
    if secret is not None:
        content = decrypt_bytes(res.content, secret)

    if output_path is not None:
        async with aiofiles.open(output_path, "wb") as f:
            await f.write(content)

    return content