from os import name
import time
import json
import logging
from typing import Dict

from server import *
from DU.Config import *

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_HAKGWA = range(3)

reply_keyboard = [
    ['초기 세팅'],
    ['시작'],
]
reply_Uni = [
    ['인문대학'],
    ['행정대학'],
    ['경상대학'],
    ['사회과학대학'],
    ['공과대학'],
    ['정보통신대학'],
    ['사범대학'],
    ['재활과학대학'],
    ['간호보건학부'],
    ['DU인재법학부'],
    ['조형예술대학'],
    ['과학생명융합대학'],
    ['성산교양대학']
]

reply_start1 = [['초기 세팅']]
reply_start2 = [['시작']]
reply_end = [['취소']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
markup_Uni = ReplyKeyboardMarkup(reply_Uni, one_time_keyboard=True)
markup_start1 = ReplyKeyboardMarkup(reply_start1, one_time_keyboard=True)
markup_start2 = ReplyKeyboardMarkup(reply_start2, one_time_keyboard=True)
markup_end = ReplyKeyboardMarkup(reply_end, one_time_keyboard=True)

# 대학 학과 정보 리스트
def hakgwa_data(content):
    reply_hakgwa = []
    json_data = open('hakgwa.json', 'r', encoding="utf-8").read()
    data = json.loads(json_data)
    for i in data['hakgwa']:
        if content in i['id']:
            reply_hakgwa.append([i['name']])
    return reply_hakgwa

# 대학, 학과 정보 변환
def facts_to_str(user_data: Dict[str, str]) -> str:
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])

# 학과 정보 변환
def facts_to_str2(user_data: Dict[str, str]) -> str:
    facts = [f'{value}' for key, value in user_data.items()]
    return "".join(facts).join(['',''])

# 처음 실행
def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation"""
    reply_text = "안녕하세요 대구대학교 학과공지 알리미 입니다.\n"
    if context.user_data:
        reply_text += (
            f"학과가 설정되어 있습니다. '시작'을 눌러 주세요\n\n변경을 원하시면 초기 세팅을 눌러주세요."
        )
        update.message.reply_text(reply_text, reply_markup=markup)
    else:
        reply_text += (
            "\n학과가 설정되어 있지 않습니다.\n'초기세팅'을 눌러 주세요"
        )
        update.message.reply_text(reply_text, reply_markup=markup_start1)

    return CHOOSING


# 초기 대학 입력
def choice_Uni(update: Update, context: CallbackContext) -> int:
    text = update.message.text.lower()
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = (
            f'기존 : {context.user_data[text]}. \n아래 선택창에서 대학을 선택하세요.'
        )
    else:
        reply_text = f'아래 선택창에서 대학을 선택하세요.'
    update.message.reply_text(reply_text,reply_markup=markup_Uni)

    return TYPING_HAKGWA

# 초기 학과 입력
def choice_hakgwa(update: Update, context: CallbackContext) -> int:
    """초기세팅 학과 입력란"""
    text = update.message.text.lower()
    reply_hakgwa = hakgwa_data(text)
    markup_hakgwa = ReplyKeyboardMarkup(reply_hakgwa, one_time_keyboard=True)
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = (
            f'기존 : {context.user_data[text]}. \n아래 선택창에서 전공을 선택하세요'
        )
    else:
        reply_text = f'아래 선택창에서 전공을 선택하세요'
    update.message.reply_text(reply_text,reply_markup=markup_hakgwa)

    return TYPING_REPLY

# 세팅 완료
def received_information(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    update.message.reply_text(
        "정상적으로 세팅을 완료 하였습니다."
        f"{facts_to_str(context.user_data)}"
        "시작을 눌러주세요",
        reply_markup=markup_start2,
    )
    return CHOOSING

# 취소
def done(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    if 'choice' in context.user_data:
        del context.user_data['choice']

    if context.user_data:
        chat_id = update.message.chat.id
        content = facts_to_str2(context.user_data)
        json_data = open('user.json', 'r', encoding="utf-8").read()
        user = json.loads(json_data)
        for i in user[content]:
            if chat_id == i['chat_id']:
                user[content].remove(i)
        json.dump(user, open("user.json", "w", encoding="utf-8"), ensure_ascii=False)

    update.message.reply_text(
        f"이용해주셔서 감사합니다 다시 시작을 원하시면 /start 를 입력하여 시작 부탁드립니다.",
    )
    user_data.clear()
    return ConversationHandler.END

#  초기화
def cancle(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text(
        '초기화를 완료 하였습니다.\n다시 시작을 원하시면 /start 를 입력하여 시작 부탁드립니다.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# 학과 공지사항 알림
def DU_Main(update: Update, context: CallbackContext) -> int:
    if context.user_data:
        content = facts_to_str2(context.user_data)
        chat_id = update.message.chat.id
        # 유저 정보 JSON 저장
        json_data = open('user.json', 'r', encoding="utf-8").read()
        user = json.loads(json_data)
        user[content].append({"chat_id":chat_id})
        json.dump(user, open("user.json", "w", encoding="utf-8"), ensure_ascii=False)
        update.message.reply_text(
            f"{content} 공지 서비스가 시작되었습니다.\n새글이 업로드 될시 알림이 옵니다.\n종료 및 재세팅을 원하시면 '취소'를 눌러주세요",
            reply_markup=markup_end
        )
        firstrun = True
        # 처음 실행후 JSON 데이터 저장
        paser(content, firstrun)
    else:
        update.message.reply_text(
            f"아직 학과 세팅을 하지 않으셨습니다. 초기세팅후 시작해 주세요",
            reply_markup=markup
        )
        return CHOOSING

    return TYPING_REPLY
    

def main() -> None:
    config = get_config()
    persistence = PicklePersistence(filename='conversationbot')
    updater = Updater(token=config["account"]["token"], persistence=persistence)

    dispatcher = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(초기 세팅)$'), choice_Uni
                ),
                MessageHandler(Filters.regex('^시작$'), DU_Main),
            ],
            TYPING_HAKGWA: [
                MessageHandler(
                    Filters.text & ~(Filters.command), choice_hakgwa
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^취소$')),
                    received_information,
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^취소$'), done),CommandHandler('cancle', cancle)],
        name="my_conversation",
        persistent=True,
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
