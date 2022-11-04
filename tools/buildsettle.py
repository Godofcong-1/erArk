#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import csv
import os

data_path = os.path.join("skills.csv")
out_path = os.path.join("out")


def build_target_skills():
    with open(data_path,encoding="utf-8") as now_file:
        now_read = csv.DictReader(now_file)
        now_data = []
        for row in now_read:
            now_data.append(row)
        out_str = ""
        now_type = "性经验类结算器"
        for row in now_data:
            if row['skill_type'] != "性":
                continue
            skill: str = row["skill"]
            skill_info: str = row["skill_info"]
            out_str += f"{now_type},{skill_info},增加少量{skill_info}经验,add_small_{skill}_experience\n"
            out_str += f"{now_type},{skill_info},增加中量{skill_info}经验,add_medium_{skill}_experience\n"
            out_str += f"{now_type},{skill_info},增加大量{skill_info}经验,add_large_{skill}_experience\n"
        now_type = "交互对象性经验类结算器"
        for row in now_data:
            if row['skill_type'] != "性":
                continue
            skill: str = row["skill"]
            skill_info: str = row["skill_info"]
            out_str += f"{now_type},{skill_info},交互对象增加少量{skill_info}经验,target_add_small_{skill}_experience\n"
            out_str += f"{now_type},{skill_info},交互对象增加中量{skill_info}经验,target_add_medium_{skill}_experience\n"
            out_str += f"{now_type},{skill_info},交互对象增加大量{skill_info}经验,target_add_large_{skill}_experience\n"
    with open(out_path,"w",encoding="utf-8") as out_file:
        out_file.write(out_str)


build_target_skills()
