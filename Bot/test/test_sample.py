import unittest
from unittest.mock import Mock, patch, AsyncMock

from telegram import (
    Update,
    PhotoSize,
)
import asyncio

from bot import CATEGORY, PHOTO, DESCRIPTION


class TestAdsBotSampleTestCase(unittest.TestCase):
    def setUp(self):
        self.update = Mock(spec=Update)
        self.context = AsyncMock()

    @patch("bot.db_client")
    def test_sample_add_category_command_handler_with_dev_id(self, mock_db_client):
        self.update.effective_chat.id = 987654321
        self.update.effective_user.id = 92129627
        self.update.effective_message.id = 111222333
        self.update.message.text = "/add_category خودرو"
        self.context.args = ["خودرو"]

        with patch.object(self.context.bot, "send_message") as mock_send_message:
            from bot import add_category_command_handler

            asyncio.run(add_category_command_handler(self.update, self.context))

            mock_send_message.assert_called_once_with(
                chat_id=self.update.effective_chat.id,
                text="دسته بندی {category} با موفقیت اضافه شد.".format(
                    category="خودرو"
                ),
                reply_to_message_id=self.update.effective_message.id,
            )
            try:
                mock_db_client.add_category.assert_called_once_with(
                    category="خودرو",
                )
            except AssertionError:
                mock_db_client.add_category.assert_called_once_with("خودرو")

    @patch("bot.db_client")
    def test_sample_add_advertising_command_handler(self, mock_db_client):
        self.update.effective_chat.id = 987654321
        self.update.effective_user.id = 92129627
        self.update.effective_message.id = 111222333
        self.context.args = []
        self.update.message.text = "/add_advertising"

        mock_db_client.get_categories.return_value = ["خودرو", "موبایل"]

        with patch.object(self.context.bot, "send_message") as mock_send_message:
            from bot import add_advertising_command_handler

            state = asyncio.run(
                add_advertising_command_handler(self.update, self.context)
            )

            mock_send_message.assert_called_once_with(
                chat_id=self.update.effective_chat.id,
                text="لطفا از بین دسته بندی های زیر یکی را انتخاب کنید:\nخودرو\nموبایل",
                reply_to_message_id=self.update.effective_message.id,
            )
            mock_db_client.get_categories.assert_called_once_with()

            self.assertEqual(state, CATEGORY)
