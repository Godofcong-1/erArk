# 新增一条检查

在 `checks/` 下新增模块，或在既有领域模块中注册：

```python
@register_check("GROUPSEX-01", "群交参与人数一致性")
def check_group_sex_member_count() -> List[CheckFailure]:
    """
    参数:
        无
    返回值:
        List[CheckFailure]: 失败记录列表，空列表表示通过
    功能:
        校验群交场景中登记的参与人数与实际参与角色数量一致
    """
    cache = cache_control.cache
    failures = []
    return failures
```

规则：

1. 检查函数无参、只读不写。用到 `cache` 的检查函数，函数体第一句取 `cache = cache_control.cache`；不读 cache 的函数不取。不给检查函数加 cache 形参：进程内只有一个全局 cache 引用，形参提供不了真正的替换能力。
2. 禁止模块级 `cache = cache_control.cache` 别名。全局 cache 在 `game.py` 启动时才赋值，模块级别名在导入时固定，一旦与全局引用分离就永久持有旧对象。
3. `make_failure` 的前两个参数与 `@register_check(check_id, check_name)` 逐字一致，以装饰器为准。
4. `check_id` 全局唯一。重复 id 会在该模块导入时抛 `ValueError`，该模块剩余检查不会注册；其他模块不受影响。
5. 检查不得修改状态，也不得调用会写状态的前提函数（`Script/Design/handle_premise`）。已知的写路径包括异常位掩码升级、指令过滤缺键补值、助理跟随 `setdefault`。
6. 每条检查的文档字符串须说明健康存档为何恒不命中。说不清就不注册。
7. 只读现有数据，不调用会惰性创建数据的 getter（例如养成数据的 `child_growth`）。
8. 注册表、配置表、时钟和静态集合直接读取；它们各自只有一种实现，不必加注入层。
9. 消息以 `[warning] ` 开头表示警示级诊断（状态不一致、历史容量超限、已移除角色引用、额外配置键等），`CheckFailure` 没有独立的 severity 字段。一条警示不足以断定缺陷成因。
10. 每个违规元素单独报告 cid、键与原值；容器缺失或外层类型错误时跳过，检查目标本身就是容器时则报告。

要附带修复时，见 [repairs.md](repairs.md) 的原则。
