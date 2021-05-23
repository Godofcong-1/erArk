erArk
====
era-明日方舟
====

介绍
----
暂无

初次启动
----
游戏初次启动时需要对数据进行预热处理(大约一分钟，请耐心等待)

操作攻略
----
暂无

BUG反馈
----
当遇到游戏闪退，可检查 error.log 文件，并将 error.log 文件中内容贴至 issues 中进行反馈

更新日志
----
暂无

著作权信息
----
此项目为明日方舟的二次同人游戏，原著作权归yj所有 \
此项目基于Python独立进行开发 \
此项目的原版本来自于任悠云开发的https://github.com/pokemonchw/dieloli \
基于 [cc by nc sa](http://creativecommons.org/licenses/by-nc-sa/2.0/) 协议，开发者允许任何人基于此项目做除商业行为外的任何事，同时允许任何人对本项目进行除协议外的任何改动，仅需注明原作者，以及以相同方式进行传播(指同样使用cc by-nc-sa协议) \
请勿将其用作商业用途

Repo说明
----
日常开发备份在instability分支中进行,pr也请提交至此分支 \
master分支在开发完成前作为设计展示分支使用 \
代码风格化通常使用black自动完成，行宽为108

请求
----
口上作者募集中

配置要求
----
GPU: \
文字游戏，没有显卡需求，但因为AA地图的关系，所以仅保证在1080P及以上显示器上获得最佳效果 \
CPU: \
同上 \
Memory: \
峰值需占用1GB左右内存，请确保运行游戏前电脑至少有2GB的空闲内存空间 \
系统: \
本游戏兼容 archlinux/steamos/chromeos/ubuntu/debian/aoscos 等绝大部分支持 gui 的 linux 系操作系统，同时也可以在 macos 和 windows7 及以上操作系统中运行 \
配置调整: \
可通过 config.ini 文件中的 random_npc_max 选项进行调整，出现兼容问题请提交反馈

依赖
----
python3.9+

建议通过::

    pip install -r requirements.txt

进行安装

字体
----
本游戏界面设计依赖 Sarasa Mono SC 字体，若系统未安装此字体将会 fallback 到系统默认字体，不能保证能否达到设计效果 \
字体相关配置可以通过 data/FontConfig.json 更改 \
本游戏不提供Sarasa Mono SC相关字体文件 \
请自行下载并安装:[Sarasa Mono SC](https://github.com/be5invis/Sarasa-Gothic) \
可通过修改 config.ini 中的 font 项自行更改字体

本地化
----
本项目使用gettext进行本地化设置 \
请于 data/po 目录下创建对应语言目录 \
切换语言请编辑 config.ini 中的 language 项 \
协作翻译方案待定

警告
----
在游戏设计中，有一定的色情，暴力，宗教，等内容，在进行游戏前请确认自己的三观足够健全到不会随意被动摇和影响

联系方式
----
无