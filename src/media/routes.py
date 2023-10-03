import io

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from src import deps
from src.capital_transfer.crud import capital_transfer as capital_transfer_crud
from src.core.config import settings
from src.schema import IDRequest
from src.utils.minio_client import MinioClient

# ---------------------------------------------------------------------------
router = APIRouter(prefix="/media", tags=["media"])


@router.post(path="/capital_transfer/find")
async def get_merchant(
    *,
    db=Depends(deps.get_db),
    minio: MinioClient = Depends(deps.minio_auth),
    capital_transfer: IDRequest,
):
    """
    ! Find Capital Transfer Image

    Parameters
    ----------
    db
        Target database connection
    minio
        Minio dep
    capital_transfer
        Target capital transfer id

    Returns
    -------
    res
        found File

    Raises
    ------
    CapitalTransferNotFoundException
    """
    obj = await capital_transfer_crud.verify_existence(
        db=db,
        capital_transfer_id=capital_transfer.id,
    )

    media_file = minio.client.get_object(
        bucket_name=settings.MINIO_CAPITAL_TRANSFER_BUCKET,
        object_name=obj.file_name,
        version_id=obj.file_version_id,
    )
    return StreamingResponse(io.BytesIO(media_file.read()), media_type="image/png")
