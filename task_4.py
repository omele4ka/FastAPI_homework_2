# Задание №4
# Напишите API для управления списком задач. Для этого создайте модель Task
# со следующими полями:
# ○ id: int (первичный ключ)
# ○ title: str (название задачи)
# ○ description: str (описание задачи)
# ○ done: bool (статус выполнения задачи)
# API должно поддерживать следующие операции:
# ○ Получение списка всех задач: GET /tasks/
# ○ Получение информации о конкретной задаче: GET /tasks/{task_id}/
# ○ Создание новой задачи: POST /tasks/
# ○ Обновление информации о задаче: PUT /tasks/{task_id}/
# ○ Удаление задачи: DELETE /tasks/{task_id}/
# Для валидации данных используйте параметры Field модели Task.
# Для работы с базой данных используйте SQLAlchemy и модуль databases

from fastapi import FastAPI
from typing import List
import databases
from pydantic import BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import insert, select, update, delete
from sqlalchemy import create_engine, Boolean, Integer, Column, String


DATABASE_URL = "sqlite:///tasks_db.db"
database = databases.Database(DATABASE_URL)
Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String, nullable=True)
    done = Column(Boolean, default=False)


engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
Base.metadata.create_all(bind=engine)
app = FastAPI()

class TaskIn(BaseModel):
    title: str = Field()
    description: str | None = Field(default=None)
    done: bool = Field(default=False)

class TaskOut(TaskIn):
    id: int


@app.get('/tasks/', response_model=List[TaskOut])
async def get_tasks_list():
    query = select(Task)
    return await database.fetch_all(query)

@app.get('/tasks/{task_id}', response_model=TaskOut)
async def get_task(task_id:int):
    query = await database.fetch_one(select(Task).where(Task.id == task_id))
    return query

@app.post('/tasks/', response_model=TaskIn)
async def create_task(task:TaskIn):
    new_task = insert(Task).values(
        title=task.title, description=task.description, done=task.done
        )
    await database.execute(new_task)
    return task

@app.put('/tasks/{task_id}', response_model=TaskIn)
async def update_task(task_id:int, task:TaskIn):
    task_update = (
        update(Task).where(Task.id == task_id).values(**task.model_dump())
    )
    await database.execute(task_update)

    return await database.fetch_one(select(Task).where(Task.id == task_id))
    

@app.delete('/tasks/{task_id}')
async def delete_task(task_id:int):
    query = delete(Task).where(Task.id == task_id)
    await database.execute(query)
    return {'message': f'Task {task_id} deleted'}