from typing import Final

from telegram import (
    Update,
    InlineQueryResultPhoto,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ConversationHandler,
    filters,
    MessageHandler,
    InlineQueryHandler,
)

from mongo_client import AdsMongoClient

BOT_TOKEN: Final = "BOT_TOKEN"

CATEGORY, PHOTO, DESCRIPTION = range(3)
# db connection
db_client = AdsMongoClient("localhost", 27017)

dev_ids = [92129627, 987654321]


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """a function that can handle start commands """
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="سلام، من ربات ثبت آگهی هستم. برای قبت آگهی جدید از دستور /add_advertising استفاده کنید.",
        reply_to_message_id=update.effective_message.id,
    )


async def add_category_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """a function in case of adding categories, it only works if the user is admin"""

    userid = update.effective_user.id
    category = context.args[0]
    if userid in dev_ids:
        db_client.add_category(category)

        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text = f"دسته بندی {category} با موفقیت اضافه شد.",
            reply_to_message_id=update.effective_message.id,
            )
    else:
        
        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text = "شما اجازه دسترسی به این دستور را ندارید.",
            reply_to_message_id=update.effective_message.id,
            )

async def add_advertising_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """a function for selecting an advertising"""
    categories = db_client.get_categories()
    text = "لطفا از بین دسته بندی های زیر یکی را انتخاب کنید:\n"+"\n".join(categories)

    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text = text,
        reply_to_message_id=update.effective_message.id,
    )

    return CATEGORY
async def choice_category_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """a function to get the category from the user message and asking for ad's thumbnail"""
    context.user_data["category"] = update.effective_message.text
    
    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text = "لطفا عکس آگهی خود را ارسال کنید.",
        reply_to_message_id=update.effective_message.id,
    )

    return PHOTO
async def photo_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    
    """a function to add description and getting the photo's url for the ad's thumbnail"""

    context.user_data["photo_url"] = update.effective_message.photo[-1].file_id
    
    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text="لطفا توضیحات آگهی خود را وارد کنید. در توضیحات می توانید اطلاعاتی مانند قیمت، شماره تماس و ... را وارد کنید.",
        reply_to_message_id= update.effective_message.id,
    )

    return DESCRIPTION

async def description_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    """a function to get the user's description and adding the user's ad to the database"""
    context.user_data["description"] = update.effective_message.text

    db_client.add_advertising(
        user_id= update.effective_user.id,
        photo_url=context.user_data["photo_url"],
        category= context.user_data["category"],
        description=context.user_data["description"]
        )
    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text="آگهی شما با موفقیت ثبت شد.",
        reply_to_message_id= update.effective_message.id,
    )

    return ConversationHandler.END
async def cancel_command_handler( update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    """a function to cancel the bot"""

    await context.bot.send_message(
        chat_id= update.effective_chat.id,
        text="عملیات ثبت آگهی لغو شد. برای ثبت آگهی جدید از دستور /add_category استفاده کنید.",
        reply_to_message_id= update.effective_message.id,
    )
    return ConversationHandler.END

async def my_ads_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """a function to send all of the user's ads to the user"""
    ads = db_client.get_ads_by_user_id(update.effective_user.id)
    if ads:
        for ad in ads:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=ad["photo_url"],
                caption=ad["description"] + f"\n\n" + "برای حذف آگهی از دستور زیر استفاده کنید."+"\n\n"+f"/delete_ad {ad['id']}",
                reply_to_message_id=update.effective_message.id,
            )
    else:
        await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text="شما هیچ آگهی ثبت نکرده‌اید.",
            reply_to_message_id= update.effective_message.id,
        )

async def delete_ad_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """a funtion to delete a specific user's ad"""
    user = update.effective_user.id

    doc = context.args[0]
    db_client.delete_advertising(user,doc)

    await context.bot.send_message(
            chat_id= update.effective_chat.id,
            text="آگهی با موفقیت حذف شد.",
            reply_to_message_id= update.effective_message.id,
        )


async def search_ads_by_category_inline_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """an inline query function to show ads to the user by category"""
    category = update.inline_query.query
    ads = db_client.get_ads_by_category(category)
    results = [
        InlineQueryResultPhoto(
            id=ad["id"],
            title=ad["description"],
            photo_url=ad["photo_url"],
            thumbnail_url=ad["photo_url"],
            caption=ad["description"],
    )
    for ad in ads
    ]
    await context.bot.answer_inline_query(update.inline_query.id, results)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command_handler))
    app.add_handler(CommandHandler("add_category", add_category_command_handler))
    app.add_handler(CommandHandler("my_ads", my_ads_command_handler))
    app.add_handler(CommandHandler("delete_ad", delete_ad_command_handler))
    app.add_handler(
        ConversationHandler(
            entry_points=[
                CommandHandler("add_advertising", add_advertising_command_handler)
            ],
            states={
                CATEGORY: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, choice_category_message_handler
                    )
                ],
                PHOTO: [
                    MessageHandler(filters.PHOTO, photo_message_handler),
                ],
                DESCRIPTION: [
                    MessageHandler(
                        filters.TEXT & ~filters.COMMAND, description_message_handler
                    )
                ],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_command_handler),
            ],
            allow_reentry=True,
        )
    )
    app.add_handler(InlineQueryHandler(search_ads_by_category_inline_query))
    app.run_polling()
