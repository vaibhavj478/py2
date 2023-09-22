from fastapi import FastAPI, Depends, status, Response, HTTPException,Request
import time
from . import schemas

from . import models

from .db import engine, SessionLocal

from sqlalchemy.orm import Session

app = FastAPI()

print("hello")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    print(start_time)
    print("middleware")
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(process_time)
    print("end")
    return response



models.Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@app.post("/blog")
async def create(blog: schemas.Blog):

    return {
        "success": True,
        "blog": blog

    }


@app.post("/create-blog", status_code=status.HTTP_201_CREATED)
def create(request: schemas.Blog, db: Session = Depends(get_db)):

    new_blog = models.Blog(title=request.title, body=request.body)

    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return new_blog


@app.get('/get-all-blog')
def all(db: Session = Depends(get_db)):

    blogs = db.query(models.Blog).all()

    return blogs


@app.get('/blog/{id}', status_code=200)
def show(id, response: Response,   db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        response.status_code = status.HTTP_404_NOT_FOUND

        return {"success": False, "message": f"blog not found for id:{id}"}

    return blog


@app.delete("/delete-blog/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destrory(id, db: Session = Depends(get_db)):

    blog = db.query(models.Blog).filter(models.Blog.id ==
                                        id).delete(synchronize_session=False)

    db.commit()

    return {"success": True}


@app.put('/update-blog/{id}', status_code=status.HTTP_202_ACCEPTED)
async def update(id, req: schemas.Blog, db: Session = Depends(get_db)):

    blog = db.query(models.Blog).filter(models.Blog.id == id)

    if not blog.first():
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT,
                            detail=f"Blog with id {id} not found")
    blog.update({"title" : req.title , "body": req.body})
    # blog.update(req)

    db.commit()

    # db.commit() {"success": True, "message": "blog is update"}

    return {"success": True, "message": "blog is update"}
