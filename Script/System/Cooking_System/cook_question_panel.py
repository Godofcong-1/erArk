import random
from types import FunctionType
from Script.Core import cache_control, game_type, get_text, flow_handle, py_cmd, text_handle
from Script.Design import attr_calculation
from Script.System.Cooking_System import cooking
from Script.UI.Moudle import draw
from Script.Config import normal_config

cache: game_type.Cache = cache_control.cache
""" 游戏缓存数据 """
_: FunctionType = get_text._
""" 翻译api """
window_width: int = normal_config.config_normal.text_width
""" 窗体宽度 """


def run_cook_question_flow(food_id: int, base_quality: int) -> int:
    """
    精细模式烹饪答题流程
    依次回答 备料/烹饪/调味/装盘 四个阶段各一题，每阶段从该食物题库随机抽题，选项随机排列。
    答对每题食物品质+1（封顶绝珍），答错品质不变。
    Keyword arguments:
    food_id -- 食物（菜谱）id
    base_quality -- 基础品质值
    Return arguments:
    int -- 答题后的最终品质值
    """
    # 阶段显示标签
    stage_label = {
        _("备料"): _("备料时"),
        _("烹饪"): _("烹饪时"),
        _("调味"): _("调味时"),
        _("装盘"): _("装盘时"),
    }
    quality = base_quality
    max_quality = cooking.get_max_food_quality()
    food_name = cache.recipe_data[food_id].name
    question_lib = cooking.get_food_cook_questions(food_id)

    # 换行绘制对象
    line_feed = draw.NormalDraw()
    line_feed.text = "\n"
    line_feed.width = 1

    py_cmd.clr_cmd()
    title_draw = draw.TitleLineDraw(_("精细烹饪 - {0}").format(food_name), window_width)
    title_draw.draw()
    intro_draw = draw.NormalDraw()
    intro_draw.text = _("○用心烹饪，依次处理各阶段的细节，正确的操作可提升食物品质。\n")
    intro_draw.draw()

    # 依次处理每个阶段
    for stage in cooking.COOK_QUESTION_STAGES:
        stage_questions = question_lib.get(stage, [])
        # 该阶段无题则跳过
        if not stage_questions:
            continue
        # 随机抽取一题
        question_data = random.choice(stage_questions)
        question_text = question_data.get("question", "")
        correct_answer = question_data.get("correct_answer", "")
        # 最错误的答案为3号错误答案
        max_wrong_answer = question_data.get("wrong_answer_3", "")
        # 收集选项（正确答案+错误答案，去除空值）
        options = [correct_answer]
        for key in ("wrong_answer_1", "wrong_answer_2", "wrong_answer_3"):
            wrong_answer = question_data.get(key, "")
            if wrong_answer:
                options.append(wrong_answer)
        # 选项随机排列，使每次顺序不同
        random.shuffle(options)

        py_cmd.clr_cmd()
        # 阶段分隔线与标题
        stage_line = draw.LineDraw("-", window_width)
        stage_line.draw()
        stage_info = draw.NormalDraw()
        stage_info.text = _("【{0}】\n").format(stage_label.get(stage, stage))
        stage_info.draw()
        # 问题内容
        question_draw = draw.NormalDraw()
        question_draw.text = _("○{0}\n").format(question_text)
        question_draw.draw()
        line_feed.draw()

        # 绘制选项按钮
        return_list = []
        option_return_map = {}
        for index, option_text in enumerate(options):
            option_button = draw.LeftButton(
                _("{0}{1}").format(text_handle.id_index(index), option_text),
                str(index),
                window_width,
            )
            option_button.draw()
            line_feed.draw()
            return_list.append(option_button.return_text)
            option_return_map[option_button.return_text] = option_text

        # 等待玩家选择
        yrn = flow_handle.askfor_all(return_list)
        chosen_answer = option_return_map.get(yrn, "")

        # 判定正误并绘制结果提示
        _level, quality_name = attr_calculation.get_food_quality(quality)
        result_draw = draw.WaitDraw()
        result_draw.width = window_width
        if chosen_answer == correct_answer:
            quality = min(quality + 1, max_quality)
            _new_level, new_quality_name = attr_calculation.get_food_quality(quality)
            result_draw.text = _("处理方式完全正确！食物品质+1，当前品质：{0}\n").format(new_quality_name)
        elif chosen_answer == max_wrong_answer:
            quality = max(quality - 1, 0)
            _new_level, new_quality_name = attr_calculation.get_food_quality(quality)
            result_draw.text = _("处理方式完全错误，正确方式是「{0}」。品质降低，当前品质：{1}\n").format(
                correct_answer, new_quality_name
            )
        else:
            result_draw.text = _("处理方式不够好，正确方式是「{0}」。品质不变，当前品质：{1}\n").format(
                correct_answer, quality_name
            )
        result_draw.draw()

    return quality
