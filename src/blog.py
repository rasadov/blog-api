import os
import json

from fastapi import Depends, APIRouter, File, Form, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.utils import secure_filename

from db import get_db
from oauth2 import get_current_user

from models import Post
from schemas import PostSchema

router = APIRouter(
    tags=["Blog"]
)

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")

@router.get('/posts/{user_id}')
async def get_posts(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    posts_query = await db.execute(
        select(Post).filter(Post.user_id == user_id).limit(page_size).offset(offset)
    )
    posts = posts_query.scalars().all()
    return posts

@router.post('/posts')
async def create_post(
    image: UploadFile = File(...),
    content: str = Form(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_folder = f'{UPLOAD_FOLDER}{user.user_id}'
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)

    secure_name = secure_filename(image.filename)
    file_path = os.path.join(user_folder, secure_name)

    file_path = f'{user_folder}/{secure_name}'
    # with open(file_path, 'wb') as f:
    #     f.write(await image.read())

    with open(file_path, 'wb') as f:
        f.write(await image.read())

    new_post = Post(
        content=json.loads(content),
        image_url=os.getenv("DOMAIN") + f"/image/{user.user_id}/{secure_name}",
        user_id=user.user_id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    return new_post

@router.put('/posts/{post_id}')
async def update_post(post_id, post: PostSchema, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = await db.execute(select(Post).filter(Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    post.content = post.content
    await db.commit()

    return post

@router.get('/post/{post_id}')
async def get_post(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.execute(select(Post).filter(Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post

@router.delete('/posts/{post_id}')
async def delete_post(post_id: int, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = await db.execute(select(Post).filter(Post.id == post_id))
    post = post.scalars().first()

    try:
        os.remove(f'{UPLOAD_FOLDER}{user.user_id}/{post.image_url}')
    except FileNotFoundError:
        pass

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()

    return post

@router.get('/image/{user_id}/{image_name}')
async def get_image(user_id, image_name):
    return FileResponse(f'{UPLOAD_FOLDER}{user_id}/{image_name}')
