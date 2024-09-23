from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.orm import Session

from src.bot.handlers.streamer.post.post_router import post_router
from src.bot.keyboards.buttons.generate_buttons.generate_reply_markup import (
    get_reply_markup,
)
from src.bot.keyboards.buttons.generate_buttons.streamer.post.post_back_button import (
    get_post_back_button,
)
from src.bot.keyboards.buttons.post.post_buttons import PostActionButtons
from src.bot.keyboards.callback_data.streamer.post.post_cd import EditPostCD
from src.bot.keyboards.states.post.post_states import EditPostState
from src.db.repository.post_repository import PostRepository


@post_router.message(EditPostState.EDIT_NAME)
async def edit_name(
    message: Message,
    db_session: Session,
    state: FSMContext,
):
    context_data = await state.get_data()
    post_id = context_data.get("id")
    post_repository = PostRepository(db_session)
    post = await post_repository.get_one(id=post_id)
    go_back_button = get_post_back_button(post)
    await post_repository.update({"id": post_id}, name=message.text)
    await post_repository.commit()
    await state.clear()
    await message.answer(
        text="Имя поста успешно изменено!",
        reply_markup=await get_reply_markup(None, go_back_button),
    )


@post_router.callback_query(
    EditPostCD.filter(F.post_action_button == PostActionButtons.EDIT_NAME)
)
async def edit_name_intent(
    callback_query: CallbackQuery,
    callback_data: EditPostCD,
    db_session: Session,
    state: FSMContext,
):
    post_id = callback_data.post_id
    post_repository = PostRepository(db_session)
    post = await post_repository.get_one(id=post_id)
    go_back_button = get_post_back_button(post)
    await state.update_data(id=callback_data.post_id)
    await state.set_state(EditPostState.EDIT_NAME)
    await callback_query.message.edit_text(
        text="Введите новое имя поста",
        reply_markup=await get_reply_markup(None, go_back_button),
    )


@post_router.message(EditPostState.EDIT_TEXT)
async def edit_text(
    message: Message,
    db_session: Session,
    state: FSMContext,
):
    context_data = await state.get_data()
    post_id = context_data.get("id")
    post_repository = PostRepository(db_session)
    post = await post_repository.get_one(id=post_id)
    go_back_button = get_post_back_button(post)
    await post_repository.update({"id": post_id}, text=message.text)
    await post_repository.commit()
    await state.clear()
    await message.answer(
        text="Текст поста успешно изменено!",
        reply_markup=await get_reply_markup(None, go_back_button),
    )


@post_router.callback_query(
    EditPostCD.filter(F.post_action_button == PostActionButtons.EDIT_TEXT)
)
async def edit_text_intent(
    callback_query: CallbackQuery,
    callback_data: EditPostCD,
    db_session: Session,
    state: FSMContext,
):
    post_repository = PostRepository(db_session)
    post = await post_repository.get_one(id=callback_data.post_id)
    go_back_button = get_post_back_button(post)
    await state.update_data(id=callback_data.post_id)
    await state.set_state(EditPostState.EDIT_TEXT)
    await callback_query.message.edit_text(
        text="Введите новый текст поста.",
        reply_markup=await get_reply_markup(None, go_back_button),
    )


@post_router.callback_query(
    EditPostCD.filter(F.post_action_button == PostActionButtons.SET_AS_ACTIVE)
)
async def set_as_active(
    callback_query: CallbackQuery, db_session: Session, callback_data: EditPostCD
):
    post_repository = PostRepository(db_session)
    post = await post_repository.get_one(id=callback_data.post_id)
    go_back_button = get_post_back_button(post)
    if await post_repository.set_as_active(post):
        await post_repository.commit()
        text = "Теперь пост активен."
    else:
        text = "Этот пост нельзя сделать активным. Убедитесь, что у поста есть активное медиа."
    await callback_query.message.edit_text(
        text=text, reply_markup=await get_reply_markup(None, go_back_button)
    )


@post_router.callback_query(
    EditPostCD.filter(F.post_action_button == PostActionButtons.SET_AS_INACTIVE)
)
async def set_as_inactive(
    callback_query: CallbackQuery, db_session: Session, callback_data: EditPostCD
):
    post_repository = PostRepository(db_session)
    post = await post_repository.get_one(id=callback_data.post_id)
    go_back_button = get_post_back_button(post)
    if await post_repository.set_as_inactive(post):
        text = "Теперь пост неактивен"
        await post_repository.commit()
    else:
        text = "Этот пост нельзя сделать неактивным."
    await callback_query.message.edit_text(
        text=text, reply_markup=await get_reply_markup(None, go_back_button)
    )