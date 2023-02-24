import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram_dialog import (
    Dialog, DialogRegistry, DialogManager, LaunchMode, Window,
)
from aiogram_dialog.widgets.kbd import Cancel, Row, Start
from aiogram_dialog.widgets.text import Const, Format

API_TOKEN = os.getenv("BOT_TOKEN")


class BannerSG(StatesGroup):
    default = State()


class MainSG(StatesGroup):
    default = State()


class Product(StatesGroup):
    show = State()


banner = Dialog(
    Window(
        Const("BANNER IS HERE"),
        Start(Const("Try start"), id="start", state=MainSG.default),
        Cancel(),
        state=BannerSG.default
    ),
    launch_mode=LaunchMode.EXCLUSIVE,
)
main_menu = Dialog(
    Window(
        Const("This is main menu"),
        Start(Const("Product"), id="product", state=Product.show),
        Cancel(),
        state=MainSG.default
    ),
    # we do not worry about resetting stack
    # each time we start dialog with ROOT launch mode
    launch_mode=LaunchMode.ROOT,
)


async def product_getter(dialog_manager: DialogManager, **kwargs):
    return {
        "data": dialog_manager.current_context().id,
    }


product = Dialog(
    Window(
        Format("This is product: {data}"),
        Row(
            Start(Const("Main menu"), id="main", state=MainSG.default),
            Start(Const("Banner"), id="banner", state=BannerSG.default),
            Start(Const("Product"), id="product", state=Product.show),
        ),
        Cancel(),
        getter=product_getter,
        state=Product.show
    ),
    # when this dialog is on top and tries to launch a copy
    # it just replaces himself with it
    launch_mode=LaunchMode.SINGLE_TOP,
)


async def main():
    # real main
    logging.basicConfig(level=logging.INFO)
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(storage=storage)
    registry = DialogRegistry()
    registry.register(banner)
    registry.register(product)
    registry.register(main_menu)

    registry.register_start_handler(state=MainSG.default, router=dp)
    registry.setup_dp(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
