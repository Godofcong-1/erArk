erArk
====
era-明日方舟（目前）
====

Read this in [English](README_en.md)

介绍
----
R18游戏，艹干员，纯爱向，无牛无G。\
游戏基本内容以TW为主，顺便缝合了AM/YM/SQC/MGT等各Era，如有雷同，不是巧合。\
单人独立开发，抽空写点，有生之年系列\
当前游戏处于α测阶段，存在未实装的功能\
各系统代码说明文档：[README.md](.github/prompts/数据处理工作流/README.md)

非开发者的普通玩家
----
右边Releases有编译好的exe，点击即玩\
为了更好的显示效果（主要是AA地图），建议安装Releases里推荐的字体\
编辑器erArkEditor也附在Releases里了，不需要写代码可以直接使用编辑器创作口上、事件、角色属性、委托等

联系方式
----
discord群：https://discord.gg/Bur3EWTVkN

请求
----
特别甚至非常的缺文本，角色口上作者大量募集中，欢迎使用编辑器来写口上

BUG反馈
----
当遇到游戏BUG，可检查 error.log 文件，并将 error.log 文件中内容贴至 issues 中进行反馈，为了方便复现，请提供版本号、bug前大致在做什么，如果是复杂的BUG最好能够提供存档

更新日志
----
见[update.log](update.log)

著作权信息
----
项目本身基于Python独立进行开发，遵循 [cc by nc sa](http://creativecommons.org/licenses/by-nc-sa/2.0/) 协议 \
禁止任何人将其用作商业用途，详细版权声明见游戏内 \

配置要求
----
GPU: \
文字游戏，没有显卡需求，但因为AA地图的关系，所以仅保证在1080P及以上显示器上获得最佳效果（暂时） \
CPU: \
同上 \
Memory: \
峰值需占用1GB左右内存，请确保运行游戏前电脑至少有2GB的空闲内存空间 \
系统: \
仅限win \
配置调整: \
可通过 [config.ini](config.ini) 文件进行调整，出现兼容问题请提交反馈

依赖
----
python3.9

建议通过::

    pip install -r requirements.txt

进行安装

Repo说明
----
日常开发备份在master分支中进行,pr也请提交至此分支 \
代码风格化通常使用black自动完成，行宽为200

字体
----
本游戏界面设计依赖 Sarasa Mono SC 字体，字体文件已附在Releases中 \
若系统未安装此字体将会 fallback 到系统默认字体，不能保证能否达到设计效果 \
顺便贴一下字体的git链接[Sarasa Mono SC](https://github.com/be5invis/Sarasa-Gothic) \
如果不喜欢，可通过修改 config.ini 中的 font 项自行更改字体，同样不能保证能否达到设计效果

本地化
----
本项目使用gettext进行本地化设置 \
请于 data/po 目录下创建对应语言目录 \
切换语言请编辑 config.ini 中的 language 项 \
协作翻译方案待定

警告
----
本游戏包含有一定的色情，暴力等内容，禁止向任何未成年传播此游戏
