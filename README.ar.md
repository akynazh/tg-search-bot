# tg-بحث-بوت

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

**روبوت Telegram يمكن استخدامه للبحث عن روابط فيديو مغناطيسية مختلفة. وهو يدعم عمليات مثل التجميع وتصدير السجلات وحفظ الروابط المغناطيسية تلقائيًا. يمكن تهيئته يدويًا لحظر محتوى NSFW والوصول إلى الإنترنت عبر الوكيل.**

تم تصميم الروبوت استنادًا إلى Python3، ويدعم النشر بنقرة واحدة باستخدام Docker، وينفذ وظائف التخزين المؤقت من خلال Redis.

وثائق README بلغات أخرى (يتم إنشاؤها تلقائيًا بواسطة[ترجمة الملف التمهيدي](https://github.com/dephraiim/translate-readme)):[عربي](./README.ar.md),[لا](./README.hi.md),[فرنسي](./README.fr.md),[الصينية المبسطة](./README.zh-CN.md),[الصينية التقليدية](./README.zh-TW.md).

## المهام

The following functions are sorted by development completion time, and new functions will be continuously added in the future.

-   يدعم الحصول على معلومات الفيديو الأساسية وروابط المغناطيس - 2022/11/25
-   دعم وكيل التكوين - 2022/11/26
-   دعم تصفية الروابط المغناطيسية (غير خاضعة للرقابة => hd => الترجمة)- 2022/11/26
-   دعم السماح للروبوت بحفظ الروابط المغناطيسية المثالية تلقائيًا إلى Pikpak - 2022/12/29
-   دعم الحصول على معاينة الفيديو والفيديو الكامل - 2022/12/31
-   دعم الحصول على لقطات فيديو - 2023/01/01
-   دعم مجموعة الممثلين ومقاطع الفيديو - 2023/01/04
-   دعم النشر عبر عامل الإرساء - 2023/01/08
-   يدعم الحصول على تصنيفات الممثلين وتقييمات الأفلام - 2023/01/20
-   يدعم الوصول العشوائي إلى مقاطع الفيديو عالية الدرجات وأحدث مقاطع الفيديو - 2023/01/25
-   دعم الحصول على أسماء الممثلين الصينية من خلال ويكيبيديا - 2023/02/18
-   دعم ترجمة العناوين اليابانية - 2023/02/18
-   دعم البحث عن الممثلين - 2023/02/18
-   دعم التخزين المؤقت من خلال redis - 2023/03/17

## درس تعليمي

أولاً، تحتاج إلى تنزيل رمز المشروع محليًا، ثم تكوين الروبوت وتحريره`~/.tg_search_bot/config.yaml`：

```yaml
# required, your telegram chat id
tg_chat_id:
# required, your telegram bot token
tg_bot_token:
# required, global proxy, 1 yes | 0 no
use_proxy:
# required, dmm proxy, 1 yes | 0 no
use_proxy_dmm:
# optional, proxy server address (required if use_proxy == 1 or use_proxy_dmm == 1)
proxy_addr:
# required, pikpak’s automatic sending function, 1 yes | 0 no
use_pikpak:
# optional, your telegram api id (required if use_pikpak == 1)
tg_api_id:
# optional, your telegram api hash (required if use_pikpak == 1)
tg_api_hash:
# required, enable cache or not, 1 yes | 0 no
use_cache:
# optional, your redis host (required if use_cache == 1)
redis_host:
# optional, your redis port (required if use_cache == 1)
redis_port:
# optional, your redis password
redis_password:
# required, enable nsfw or not, 1 yes | 0 no
enable_nsfw: 0
```

PS: If you want to use Pikpak’s automatic sending function, you need to authorize it manually first: [بوت Pikpak الرسمي](https://t.me/PikPak6_Bot)، ثم قم بتسجيل الدخول عند تشغيل الروبوت لأول مرة. (رمز دعوة بيكباك الخاص بي: 99492001، أدخل للحصول على العضوية)

أخيرًا، قم بتشغيل الروبوت: (توجد ملفات مثل السجلات والسجلات في`~/.tg_search_bot`)

```sh
# op1. docker-compose
docker-compose up -d
# op2. simple way (Python >=3.10)
pip install -r requirements.txt && python3 bot.py
```

## تطوير

أستخدم python-3.10.9 للتطوير. الرجاء استخدام python &lt;= 3.10 للتطوير. بالإضافة إلى ذلك، يوصى باستخدام تطوير البيئة الافتراضية بايثون لتجنب المشاكل غير الضرورية. فيما يلي خطوات التطوير الخاصة بي كمرجع فقط:

```shell
git clone https://github.com/akynazh/tg-search-bot.git
cd tg-search-bot
~/.pyenv/versions/3.10.9/bin/python -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

ثم يمكنك البدء في كتابة التعليمات البرمجية. عند الانتهاء، تذكر كتابة أو تشغيل مثيل اختبار (في`tests/test.py`). يرجى التأكد من عدم وجود مشكلة في الاختبار قبل إرسال الرمز.

## الجميع

-   النسخة الإنجليزية
-   يدعم البحث عن الفيديو المزيد من مواقع الويب المغناطيسية (حاليًا يتم دعم The Pirate Bay فقط)
-   الميزات الأخرى التي ترغب في رؤيتها تظهر...

## شكر وتقدير

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->

<!-- prettier-ignore-start -->

<!-- markdownlint-disable -->

<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://akynazh.site"><img src="https://avatars.githubusercontent.com/u/78672905?v=4?s=100" width="100px;" alt="Jack Bryant"/><br /><sub><b>Jack Bryant</b></sub></a><br /><a href="#maintenance-akynazh" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/z-hhh"><img src="https://avatars.githubusercontent.com/u/8455958?v=4?s=100" width="100px;" alt="zhhh"/><br /><sub><b>zhhh</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=z-hhh" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://allcontributors.org"><img src="https://avatars.githubusercontent.com/u/46410174?v=4?s=100" width="100px;" alt="All Contributors"/><br /><sub><b>All Contributors</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=all-contributors" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/JackBryant286"><img src="https://avatars.githubusercontent.com/u/113345781?v=4?s=100" width="100px;" alt="Jack Bryant"/><br /><sub><b>Julia</b></sub></a><br /><a href="https://github.com/akynazh/tg-search-bot/commits?author=JackBryant286" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->

<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

إذا كنت تريد أيضًا المساهمة في المجتمع، فيرجى التحقق من ذلك[قائمة كل شيء](https://github.com/akynazh/tg-search-bot#TODO)و أقرأ[خطوات التطوير](https://github.com/akynazh/tg-search-bot#Development)، القضايا واستراتيجية الحد من الفقر هي موضع ترحيب.
