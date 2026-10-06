from fastapi import APIRouter, HTTPException
from api.schemas import InstagramAccountIn, InstagramAccountOut
from storage.supabase import list_instagram_accounts, add_instagram_account, delete_instagram_account

router = APIRouter()


@router.get("/instagram", response_model=list[InstagramAccountOut])
def get_instagram_accounts():
    return list_instagram_accounts()


@router.post("/instagram", response_model=InstagramAccountOut, status_code=201)
def create_instagram_account(body: InstagramAccountIn):
    try:
        return add_instagram_account(body.username, body.password, body.label)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.delete("/instagram/{account_id}", status_code=204)
def remove_instagram_account(account_id: str):
    delete_instagram_account(account_id)
