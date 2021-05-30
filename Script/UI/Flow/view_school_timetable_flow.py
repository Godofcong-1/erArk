from Script.Core import constant
from Script.Design import handle_panel
from Script.UI.Panel import view_school_timetable_panel
from Script.Config import normal_config

width = normal_config.config_normal.text_width
""" 屏幕宽度 """


# @handle_panel.add_panel(constant.Panel.VIEW_SCHOOL_TIMETABLE)
# def view_school_timetable():
    # """查看课程表面板"""
    # now_panel = view_school_timetable_panel.SchoolTimeTablePanel(width)
    # now_panel.draw()
