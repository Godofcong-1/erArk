"""Medical subsystem package - 医疗系统子模块"""
# 显式导入所有子模块以便 PyInstaller 打包
# 注意：导入顺序很重要，需要先导入基础模块，再导入依赖它们的模块
# 避免循环导入问题

# 第一层：基础常量和工具模块（无内部依赖）
from Script.System.Medical_System import medical_constant
from Script.System.Medical_System import medical_core
from Script.System.Medical_System import log_system

# 第二层：病人管理模块（依赖基础模块）
from Script.System.Medical_System import clinic_patient_management
from Script.System.Medical_System import hospital_patient_management

# 第三层：医生服务模块（依赖病人管理模块）
from Script.System.Medical_System import clinic_doctor_service
from Script.System.Medical_System import hospital_doctor_service

# 第四层：高层服务模块（依赖上述所有模块）
from Script.System.Medical_System import medical_service

# 第五层：UI 面板模块（依赖服务模块）
from Script.System.Medical_System import medical_department_panel
from Script.System.Medical_System import medical_player_diagnose_function
from Script.System.Medical_System import medical_player_diagnose_panel

