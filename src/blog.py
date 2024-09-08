import os

from fastapi import Depends, APIRouter, UploadFile, HTTPException, Query
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

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
async def create_post(post: PostSchema, image: UploadFile,
                      user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not image or not image.filename:
        raise HTTPException(status_code=400, detail="File and payload are required")

    with open(f'{UPLOAD_FOLDER}{image.filename}', 'wb') as f:
        f.write(image.file.read())
    
    new_post = Post(
        title=post.title,
        content=post.content,
        image_url=image.filename,
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

@router.delete('/posts/{post_id}')
async def delete_post(post_id, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    post = await db.execute(select(Post).filter(Post.id == post_id))
    post = post.scalars().first()

    os.remove(f'{UPLOAD_FOLDER}{user.user_id}/{post.image_url}')

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    await db.commit()

    return post
