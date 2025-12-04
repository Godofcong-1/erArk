"""Medical subsystem package - 医疗系统子模块"""
# 显式导入所有子模块以便 PyInstaller 打包（使用相对导入）
from Script.System.Medical import (
    medical_constant,
    medical_core,
    log_system,
    medical_service,
    medical_department_panel,
    medical_player_diagnose_function,
    medical_player_diagnose_panel,
    clinic_patient_management,
    clinic_doctor_service,
    hospital_patient_management,
    hospital_doctor_service,
)
