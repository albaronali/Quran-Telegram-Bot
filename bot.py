from telegram import Update , ReplyKeyboardMarkup, KeyboardButton , InputFile , BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import asyncio,nest_asyncio,requests,json
from enum import Enum
import random
from dotenv import load_dotenv
import os



# Load environment variables from .env file
load_dotenv()

#bot and channel ids
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
channel_id = os.getenv("CHANNEL_ID")
suggest_channel_id = os.getenv("SUGGESTION_CHANNEL_ID")

# get surahs from json file
file_path = 'surahs.json'
with open(file_path,'r',encoding='utf-8') as json_file:
    surahs = json.load(json_file)


#context state
class user_state (Enum):
    TASKS_CHOICE = 1
    SURA_CHOICE_GROUP_HANDLER = 2
    SURA_CHOICE_HANDLER = 3
    READER_HANDLER = 4
    GET_RANDOM_AYAH = 5
    SUGGESTION = 6

# tasks list 
tasks = ['1️⃣ سور القران الكريم','2️⃣ رسالة من القران' , '3️⃣ البحث']

nest_asyncio.apply()


async def start(update : Update , context : ContextTypes.DEFAULT_TYPE ) -> None :
    commands = """
✨ مرحباً بك في بوت القرآن الكريم! ✨

🔹 /start
   - إعادة تشغيل البوت وعرض كافة الخدمات المتاحة.

🔹 /main
   - عرض قائمة الأوامر والخدمات المتاحة بشكل منظم.

🔹 /info
   - عرض معلومات شاملة عن خدمات البوت لتسهيل الاستخدام.

🔹 /sugg
   - يمكنك من تقديم اقتراحاتك وآرائك لتطوير البوت وتحسينه.
"""
    await update.message.reply_text(text=commands , parse_mode='MarkDown')

    
    

async def main_menu(update:Update,context:ContextTypes.DEFAULT_TYPE)->None:
    keyboard = [[task] for task in tasks]

    reply_markup = ReplyKeyboardMarkup(keyboard , resize_keyboard=True , one_time_keyboard=True)

    await update.message.reply_text("ما الخيار الذي تريده؟", reply_markup=reply_markup)
    
    context.user_data['state'] = user_state.TASKS_CHOICE
    
    
async def suggestion(update : Update , context : ContextTypes.DEFAULT_TYPE ) -> None :
    welcome_message = """
مرحبًا بك في بوت الاقتراحات الخاص بالقرآن الكريم! 🌟 
نحن سعداء بانضمامك إلينا. هنا، يمكنك مشاركتنا أفكارك وآرائك 
لتحسين تجربتك في استخدام البوت. نحن هنا للاستماع إليك، 
ونسعى دائمًا لتقديم أفضل خدمة لمساعدتك في تلاوة القرآن 
وفهم معانيه.
"""
    await update.message.reply_text(text=welcome_message)
    context.user_data['state'] = user_state.SUGGESTION
    

async def info(update : Update , context : ContextTypes.DEFAULT_TYPE ) -> None :
    instructions = """
--- 

📌 بعض الخدمات المتاحة:

1️⃣ سور القرآن الكريم بالصوت  
   - تم تقسيم السور الـ114 إلى 6 مجموعات، كل مجموعة تضم 19 سورة.
   - عند اختيارك لمجموعة معينة، ستظهر لك السور ضمن هذه المجموعة.
   - اضغط على السورة التي تريد سماعها، وستتمكن من اختيار القارئ المفضل.

2️⃣ رسالة من القرآن  
   - احصل على آية قرآنية عشوائية لتذكيرك بكلمات الله الكريمة، التي تلهمك وتريح قلبك.

3️⃣ البحث باسم السورة  
   - اكتب اسم السورة التي ترغب في سماعها، وسيقوم البوت بإرسال تلاوتها الصوتية إليك مباشرة.

---

📌 ملاحظات:

- استخدم الأوامر والقائمة للوصول إلى الخدمات بسهولة.  
- يمكنك الاعتماد على هذا البوت كمصدر للراحة والتذكير بآيات الله.

💬 إذا كانت لديك أي استفسارات أخرى، لا تتردد في مراسلتنا عبر تيليجرام: [@AliAUoda](https://t.me/AliAUoda)
"""
    await update.message.reply_text(text=instructions , parse_mode='MarkDown')


async def choice_tasks_handler(update : Update , context : ContextTypes.DEFAULT_TYPE)-> None :
    
    if context.user_data['state'] == user_state.TASKS_CHOICE:
        
        if update.message.text == '2️⃣ رسالة من القران':
            context.user_data['state'] = user_state.GET_RANDOM_AYAH
            await choices_handler(update,context)
        
        elif update.message.text == '3️⃣ البحث':
            await surah_search_by_name(update,context)
        else:
            await display_surah_groups(update,context)
            
    elif context.user_data['state'] == user_state.SUGGESTION:
        await get_suggest(update,context)
        
    else:
        await choices_handler(update,context)
    
async def surah_search_by_name(update:Update , context=ContextTypes.DEFAULT_TYPE)->None:
    await update.message.reply_text(text="عذرا الخدمه غير متوفره الان , اختر خدمه اخرى")
    await main_menu(update,context)

async def display_surah_groups(update:Update,context:ContextTypes.DEFAULT_TYPE)->None:
    
    keyboard = [[surah_group] for surah_group in surahs.keys()]
    markup_reply = ReplyKeyboardMarkup(keyboard=keyboard,resize_keyboard=True,one_time_keyboard=True)
    
    await update.message.reply_text(text= "اختر احد مجموعات السور؟",reply_markup=markup_reply)
    context.user_data['state'] = user_state.SURA_CHOICE_GROUP_HANDLER

async def get_suggest(update=Update,context=ContextTypes.DEFAULT_TYPE)->None:
    thank_you_message = """
شكرًا لك على مشاركتك معنا! 🙏🏼 
نحن نقدر وقتك وجهودك في تقديم الاقتراحات. 
كل فكرة منك تُساعدنا في تحسين خدماتنا 
وجعل تجربة تلاوة القرآن الكريم أكثر سهولة وفاعلية. 
نأمل أن تواصل مشاركتنا أفكارك في المستقبل!
"""
    await update.message.reply_text(text=thank_you_message)
    await froward_suggest(update,context)
    await start(update,context)
    
async def froward_suggest(update=Update,context = ContextTypes.DEFAULT_TYPE)->None:
    user = update.message.from_user
    username = user.username if user.username else "No username"
    user_id = user.id
    suggest = update.message.text
    message = f"""
اسم المستخدم : \n @{username}
الاقتراح : \n{suggest}
    """
    await context.bot.send_message(chat_id=suggest_channel_id, text=message)
    await main_menu(update,context)
    
    
async def choices_handler(update:Update,context:ContextTypes.DEFAULT_TYPE) -> None :

    if context.user_data.get('state') == user_state.SURA_CHOICE_GROUP_HANDLER :
        await suras_group_handler(update,context)

    elif context.user_data.get('state') == user_state.SURA_CHOICE_HANDLER :
        await sura_choice_handler(update,context)
    
    elif context.user_data.get('state') == user_state.READER_HANDLER :
        await reader_handler(update,context)
        
    elif context.user_data.get('state') == user_state.GET_RANDOM_AYAH:
        await random_ayah_handler(update,context)     
        
async def suras_group_handler(update: Update,context : ContextTypes.DEFAULT_TYPE) -> None:
    
    surah_group_chosen = update.message.text
    
    if surah_group_chosen in surahs.keys() : 
        
        await disply_suras(update,context)
        
    else:

        await update.message.reply_text("اختر خيار صحيح فقط")

async def disply_suras(update : Update , context : ContextTypes.DEFAULT_TYPE) -> None :
    
    surah_group_chosen = update.message.text
    
    context.user_data['surah-group'] = surah_group_chosen
    
    keyboard = [["سورة " + surah_name] for surah_name in surahs[surah_group_chosen].keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_text("اختر سورة؟", reply_markup=reply_markup)
    
    context.user_data['state'] = user_state.SURA_CHOICE_HANDLER

async def sura_choice_handler(update : Update , context : ContextTypes.DEFAULT_TYPE) -> None :
    
    surah_chosen = update.message.text.replace("سورة " , "") # get text from user reply and remove word "سورة" from text 
    
    surah_group_chosen = context.user_data['surah-group']
    
    if surah_chosen in surahs[surah_group_chosen].keys():
        
        context.user_data['surah'] = surah_chosen
        await disply_readers(update,context)
        
    else :
        
        await update.message.reply_text("لا توجد سورة بهذا الاسم")

async def disply_readers(update : Update , context : ContextTypes.DEFAULT_TYPE) -> None :
    
    surah_group_chosen = context.user_data['surah-group']
    surah_chosen = context.user_data['surah']
    
    keyboard = [[reader] for reader in surahs[surah_group_chosen][surah_chosen]['readers'].keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard=keyboard , resize_keyboard=True , one_time_keyboard=True)
    await update.message.reply_text("اختر القارئ ؟" , reply_markup=reply_markup)
    context.user_data['state'] = user_state.READER_HANDLER

async def reader_handler(update : Update , context : ContextTypes.DEFAULT_TYPE) -> None :
    
    surah_group_chosen = context.user_data['surah-group']
    surah_chosen = context.user_data['surah']
    reader_chosen = update.message.text
    
    if reader_chosen in surahs[surah_group_chosen][surah_chosen]['readers'].keys() :
        if surahs[surah_group_chosen][surah_chosen]['readers'][reader_chosen]:
            context.user_data['reader'] = reader_chosen 
            await send_sura(update,context)
        else :
            await update.message.reply_text(text='القارئ غير متاح')
            await disply_readers(update,context)
      
async def random_ayah_handler(update:Update , context:ContextTypes.DEFAULT_TYPE)->None:
    random_surah_number = random.randint(1,114)
    url_1 = f"https://api.alquran.cloud/v1/surah/{random_surah_number}"
    respone = requests.get(url_1)
    
    if respone.status_code == 200:
        surah = json.loads(respone.text) 
    else:
        await update.message.reply_text(text=respone.text)
        
    max_number_of_ayahs_in_surah = surah['data']['numberOfAyahs']
    random_ayah_number = random.randint(1,max_number_of_ayahs_in_surah)
    url_2 = f"https://api.alquran.cloud/v1/ayah/{random_surah_number}:{random_ayah_number}"
    respone = requests.get(url_2)
    
    if respone.status_code == 200:
        
        ayah = json.loads(respone.text)
        random_ayah = ayah['data']['text']
        random_ayah_info = f"""
        اسم السوره : {ayah['data']['surah']['name']}
رقم الايه : {ayah['data']['number']}
        """
        await update.message.reply_text(text=random_ayah)
        await update.message.reply_text(text=random_ayah_info)
        
    else:
        
        await update.message.reply_text(text=respone.text)
        
    await main_menu(update,context)
        
async def send_sura (update: Update , context : ContextTypes.DEFAULT_TYPE)->None:
    
    #1- send surah information 
    await send_surah_info(update,context)
    
    #2- send surah audio 
    await send_surah_audio(update,context)
    
    #3-send special character
    special_text = 'لا تنسى الدعوه بالرحمه لوالدتي ❤'
    await update.message.reply_text(text=special_text)
    
    #Back Method ()
          
async def send_surah_info(update=Update,context=ContextTypes.DEFAULT_TYPE)->None:
    surah_group_chosen = context.user_data['surah-group']
    surah_chosen = context.user_data['surah']
    
    data = await get_surah_info(surah_group_chosen,surah_chosen)
    surah_info = f"""اسم السوره : {data['data'].get('name')}
اسم السورة بالانكليزي : {data['data'].get('englishName')}
ترتبها في القران : {surahs[surah_group_chosen][surah_chosen].get("QuanNumber")}
ترتيبها في النزول : {surahs[surah_group_chosen][surah_chosen].get("revelationNumber")}
عدد ايات السوره: {data['data'].get('numberOfAyahs')}
مكان النزول : { "مكة" if data['data'].get('revelationType') == "Mecca" else "المدينة"} """
    await update.message.reply_text(text=surah_info)
    
async def send_surah_audio(update=Update,context=ContextTypes.DEFAULT_TYPE)->None:
    surah_group_chosen = context.user_data['surah-group']
    surah_chosen = context.user_data['surah']
    reader_chosen = context.user_data['reader']
    
    message_id = surahs[surah_group_chosen][surah_chosen]['readers'].get(reader_chosen)
    await context.bot.forward_message(chat_id = update.message.chat_id , from_chat_id=channel_id , message_id= message_id)

async def get_surah_info(surah_group , surah_name) :
    surah_number = surahs[surah_group][surah_name].get("QuanNumber")
    url = f"https://api.alquran.cloud/v1/surah/{surah_number}"
    res = requests.get(url)
    if res.status_code == 200:
        data = json.loads(res.text)
    else:
        print(res.text)
        
    return data
  
  
async def setup_commands(application) -> None :
    
    commands = [
        BotCommand("start", "اعادة تشغيل البوت"),
        BotCommand("main", "الصفحه الرئيسية"),
        BotCommand("info", "تعلميات البوت"),
        BotCommand("sugg", "اقتراحاتك"),
    ] 
    
    try :
        
        await application.bot.set_my_commands(commands)
        
    except Exception as e :
        
        print(f"error setup commands : {e}")
  
async def main ():

    print("Bot Starting !!")

    application = ApplicationBuilder().token(bot_token).build()
    
    # Set the bot commands
    await setup_commands(application)
    
    
    #Command Handler
    application.add_handler(CommandHandler("start" , start))
    application.add_handler(CommandHandler("main" , main_menu))
    application.add_handler(CommandHandler("info" , info))
    application.add_handler(CommandHandler("sugg" , suggestion))

    application.add_handler(MessageHandler(filters.TEXT& ~filters.COMMAND,choice_tasks_handler))
    


    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())  # This will correctly run your async main function
    main()
    
    
    
# info page
# suggestion page