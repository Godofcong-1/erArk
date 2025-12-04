"""Medical subsystem package - 医疗系统子模块"""
# 显式导入所有子模块以便 PyInstaller 打包
from Script.System.Medical import (
    medical_constant,
    medical_service,
    medical_core,
    medical_department_panel,
    medical_player_diagnose_panel,
    medical_player_diagnose_function,
    hospital_doctor_service,
    hospital_patient_management,
    clinic_doctor_service,
    clinic_patient_management,
    log_system,
)
