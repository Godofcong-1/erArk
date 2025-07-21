erArk
====
era-Arknights (Current)
====

查看中文介绍 [中文](README.md)

Introduction
----
R18 game, sex with Operators, pure romance, no NTR or guro.\
Most contents refer to TW, as well as other eras like AM/YM/SQC/MGT, etc. It's not a coincidence if there are similarities in contents.\
Solo development, updates at free time, it’s a creation of lifetime\
Currently in the α testing phase, consisting of unimplemented functions.\
All system code documentation: [README.md](.github/prompts/数据处理工作流/README.md)

Normal Non-developer Players
----
The Releases section at the right has the coded exe, can be played immediately on click\
For better visual effect (mainly for AA map) , it’s recommended to download the suggested font in Releases\
The editor for dialogues/events, erArkEditor, was also in Releases, allowing production of dialogues and events without the need of coding

Contact Method
----
Discord：https://discord.gg/Bur3EWTVkN

Request
----
Very lacking on text, recruiting dialogues writers, it’s welcomed to write dialogues with the editor

BUG Feedback
----
When meeting BUG, check on the error.log file, and paste the content inside error.log at issues for feedback, and provide version date and the actions before the bug occurred for easy checking, and provide save files if it’s a complex BUG


Update Log
----
Look at [update.log](update.log)

Copyright Info
----
The project was developed independently with Python, following the [cc by nc sa](http://creativecommons.org/licenses/by-nc-sa/2.0/) agreement \
No one is permitted to use this for business purposes, with the detailed copyright statement in game \

Configuration Requirement
----
GPU: \
No special graphic card requirement as it’s a text game, but because of the AA map, it’s recommended to use a monitor with 1080P and above for best visual effect (temporary) \
CPU: \
Same as above \
Memory: \
About 1GB memory was used at its peak value, it’s recommended to ensure there’s at least 2GB of free memory space before processing the game \
System: \
Windows only \
Configuration Settings: \
Configure via the config.ini file, submit the feedback if there’s any compatible issues

Relied on
----
python3.9

Recommend to download through:

    pip install -r requirements.txt

Repo Explanation
----
Daily backup at master branch, also submit pr to this branch \
Code style was automatically completed with black, line width as 200

Font
----
The game interface heavily relied on Sarasa Mono SC font, attached at Releases \
The system will fallback to default font if the font above is absent, which might not reach the target design effect \
Git link of the font [Sarasa Mono SC](https://github.com/be5invis/Sarasa-Gothic) \
Can change the font via config.ini-> font, lso might not reach the target design effect \

Localization
----
The project used gettext for localization settings \
Please head to catalog of data/po to create the corresponding language directories \
Change the language at [config.ini](config.ini)-> language \
Plan for collaborative translations not determined yet

Warning
----
There is certain instances of pornography and violence in the game, it’s prohibited to share the game to any underage
