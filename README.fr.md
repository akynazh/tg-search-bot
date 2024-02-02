# tg-search-bot

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-4-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

**Un robot Telegram qui peut être utilisé pour rechercher divers liens magnétiques vidéo. Il prend en charge des opérations telles que la collecte, l'exportation d'enregistrements et l'enregistrement automatique des liens magnétiques. Il peut être configuré manuellement pour bloquer le contenu NSFW et l'accès Internet proxy.**

Le robot est construit sur Python3, prend en charge le déploiement en un clic avec Docker et implémente des fonctions de mise en cache via Redis.

## Présentation de la fonction

Les fonctions suivantes sont triées par heure d'achèvement du développement et de nouvelles fonctions seront continuellement ajoutées à l'avenir.

-   Prend en charge l'obtention d'informations vidéo de base et de liens magnétiques - 2022/11/25
-   Prise en charge du proxy de configuration - 26/11/2022
-   Prise en charge des liens magnétiques de filtrage (non censuré => hd => sous-titre) - 26/11/2022
-   Support permettant aux robots de sauvegarder automatiquement les liens magnétiques optimaux vers Pikpak - 29/12/2022
-   Prise en charge de l'obtention d'un aperçu de la vidéo et de la vidéo complète - 2022/12/31
-   Prise en charge de l'obtention de captures d'écran vidéo - 01/01/2023
-   Collecte de soutien d'acteurs et de vidéos - 04/01/2023
-   Support déploiement via docker - 08/01/2023
-   Prend en charge l'obtention de classements d'acteurs et de classements de films - 20/01/2023
-   Prend en charge l'accès aléatoire aux vidéos les plus performantes et aux dernières vidéos - 2023/01/25
-   Aide à l'obtention des noms chinois des acteurs via Wikipédia - 2023/02/18
-   Support traduction des titres japonais - 18/02/2023
-   Accompagnement à la recherche d'acteurs - 18/02/2023
-   Prise en charge de la mise en cache via Redis - 2023/03/17

## Didacticiel

Tout d'abord, vous devez télécharger le code du projet localement, puis configurer le robot et modifier`~/.tg_search_bot/config.yaml`：

```yaml
# TG 对话 ID
tg_chat_id:
# TG 机器人 Token
tg_bot_token:
# 全局是否使用代理 1 是 | 0 否
use_proxy:
# 访问 dmm 时是否使用代理，如果全局使用代理，则忽略该字段 1 是 | 0 否
use_proxy_dmm:
# 代理服务器地址，如果不使用代理，则忽略该字段
proxy_addr:
# 是否使用 Pikpak 自动发送功能 1 是 | 0 否
use_pikpak:
# 配置 TG API，如果不使用 Pikpak 自动发送功能，则忽略以下两个字段，可在这里申请 API: https://my.telegram.org/apps
tg_api_id:
tg_api_hash:
# 是否使用缓存 1 是 | 0 否
use_cache:
# redis 地址，如果不使用缓存，则忽略以下两个字段
redis_host:
redis_port:
# nsfw 1 是 | 0 否
enable_nsfw: 0
```

PS: 如需使用 Pikpak 自动发送功能，需要先手动授权 [Robot officiel Pikpak](https://t.me/PikPak6_Bot), puis connectez-vous lors de la première exécution du robot. (Mon code d'invitation Pikpak : 99492001, entrez pour devenir membre)

Enfin, exécutez le robot : (les fichiers tels que les enregistrements et les journaux se trouvent dans`~/.tg_search_bot`Sous contenu)

```sh
# 方法一: 通过 docker 运行：(推荐)
docker-compose up -d
# 方法二: 通过普通方法运行:（Python >=3.10, 如果使用缓存的话需先开启 redis 服务）
pip install -r requirements.txt && python3 bot.py
```

## Étapes de développement

J'utilise python-3.10.9 pour le développement. Veuillez utiliser python &lt;= 3.10 pour le développement. De plus, il est recommandé d'utiliser le développement d'un environnement virtuel python pour éviter des problèmes inutiles. Voici mes étapes de développement à titre de référence uniquement :

```shell
# python=3.10.9
git clone https://github.com/akynazh/tg-search-bot.git
cd tg-search-bot
python3 -m venv venv
source ./venv/bin/activate
pip3 install -r requirements.txt
```

Ensuite, vous pouvez commencer à écrire du code. Lorsque vous avez terminé, n'oubliez pas d'écrire ou d'exécuter une instance de test (dans`tests/test.py`milieu). Veuillez vous assurer qu'il n'y a aucun problème avec le test avant de soumettre le code ~

## TOUS

-   version anglaise
-   La recherche vidéo prend en charge davantage de sites Web magnétiques (actuellement, seul The Pirate Bay est pris en charge)
-   D'autres fonctionnalités que vous aimeriez voir apparaître...

## Remerciements

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

Si vous souhaitez également contribuer à la communauté, veuillez consulter[TOUS](https://github.com/akynazh/tg-search-bot#todo), et basé sur[Étapes de développement](https://github.com/akynazh/tg-search-bot#开发步骤)Pour le développement, les problèmes et les relations publiques sont les bienvenus.
