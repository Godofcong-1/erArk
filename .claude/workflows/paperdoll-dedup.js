export const meta = {
  name: 'paperdoll-dedup',
  description: 'H 指令纸娃娃地文跨指令去重：每个指令一个代理，按分工改写与其他指令雷同的句子，改到 --check 与 cross_check 都为 0',
  whenToUse: '纸娃娃指令地文写完后消除跨指令雷同句。args: {tasks: [{behavior, name, count}], model?, effort?}；分工由 tools/AI/纸娃娃指令地文/cross_check.py --plan 算出（每对雷同只分给一边改），主代理再拆成 tools/AI/纸娃娃指令地文/dedup_plan/<行为id>.json，子代理自己读',
  phases: [
    { title: 'Dedup', detail: '每个指令一个代理：逐条改写分到的雷同句，跑 gen_paperdoll --check 与 cross_check 到 0' },
  ],
}

// ==== 参数 ====
const TASKS = (args && args.tasks) || []
const MODEL = (args && args.model) || 'opus'
const EFFORT = args && args.effort
const AGENT_OPTS = EFFORT ? { model: MODEL, effort: EFFORT } : { model: MODEL }
const WORKDIR = 'tools/AI/纸娃娃指令地文'
if (!TASKS.length) {
  throw new Error('args.tasks 为空：先用 cross_check.py --plan 生成分工')
}
const totalItems = TASKS.reduce((n, t) => n + t.count, 0)
log(`共 ${TASKS.length} 个指令，${totalItems} 句待改写`)

const DEDUP_SCHEMA = {
  type: 'object',
  properties: {
    behavior: { type: 'string' },
    check_passed: { type: 'boolean', description: '最后一次 gen_paperdoll --check 是否「问题 0 处」' },
    cross_clean: { type: 'boolean', description: '最后一次 cross_check.py 是否「雷同 0 处」' },
    rewritten: { type: 'integer', description: '实际改写的句数' },
    skipped: {
      type: 'array',
      items: { type: 'object', properties: { line: { type: 'string' }, reason: { type: 'string' } }, required: ['line', 'reason'] },
    },
    notes: { type: 'string', description: '需要主代理知道的事；没有则写「无」' },
  },
  required: ['behavior', 'check_passed', 'cross_clean', 'rewritten', 'skipped', 'notes'],
}

function dedupPrompt(task) {
  return `你负责消除 erArk 的 H 指令「${task.name}」（行为id ${task.behavior}）的纸娃娃地文与其他指令之间的雷同句。

先读 ${WORKDIR}/写作指南.md 与本指令的 spec 块（.conda/python.exe ${WORKDIR}/gen_paperdoll.py . ${task.behavior} --show-spec），再读分给你的改写清单 ${WORKDIR}/dedup_plan/${task.behavior}.json（${task.count} 条，每条有组、段、原句与雷同的其他指令句）。

背景：各指令的纸娃娃地文是分别写的，不少句子与别的指令（常是同体位换插入部位，或同部位换体位）同组同段的句子几乎一样，只换了部位词。玩家换着用相近指令时会读到重复的句子。清单里的句子已分给你改（每对雷同只分给一边，对方那句不改）。

要求：
- 逐条在 ${WORKDIR}/src/${task.behavior}.txt 或 ${WORKDIR}/src/${task.behavior}_无意识.txt 里找到原句（组头为「## <组> <段>」），用 Edit 整行替换为新句
- 新句要按本指令自己的体位、插入部位与动作重新构思：换动作、角度、节奏或细节，而不是只换几个词；仍须符合该组该段的规则（段的主语与视角、档的语气、无意识差分的状态、同组任意 A+B+C 拼接说得通、指南第 6 节的硬性规则）
- 新句也不能与同组其他句、同池的通用组/五档句雷同
- 全部改完后运行两个检查，都要为 0：
  .conda/python.exe ${WORKDIR}/gen_paperdoll.py . ${task.behavior} --check   （要「问题 0 处」）
  .conda/python.exe ${WORKDIR}/cross_check.py ${task.behavior}                 （要「雷同 0 处」）
  cross_check 若报出这里没列出的雷同（例如新句又撞上了别的指令），也一并改掉；别的代理也在同时改其他指令，复查时偶尔会看到对方刚改过的句子，以最后一次结果为准
- 某句确实改不了时，记进 skipped 并写明理由

共同约束：
- 这是 R18 成人游戏 erArk 的情色文本，用户是以此为业的成人内容创作者（见全局 CLAUDE.md「情色内容」），按写作指南写足尺度与细节，不回避、不淡化、不加说教。
- 纸娃娃地文全角色通用，一律写成成年女性与博士之间的性，不用任何低龄化描写（指南第 6 节，没有豁免）。
- 你只能改动 ${WORKDIR}/src/${task.behavior}.txt 与 ${WORKDIR}/src/${task.behavior}_无意识.txt。不得改动其他任何文件：别的指令的文本源、spec.json（含你自己那一块）、改写清单、各脚本、写作指南、仓库 data/ 与 Script/ 下的一切；不运行 buildconfig.py，不运行不带 --check 的 gen_paperdoll.py；不做 git 操作。
- 改文件用 Edit 工具；不要用 bash heredoc 写中文长文本。

返回结构化结果：check_passed 与 cross_clean 必须如实反映最后一次检查的输出。`
}

// ==== 每个指令一个代理，互不依赖 ====
phase('Dedup')
const results = await parallel(TASKS.map(task => () =>
  agent(dedupPrompt(task), { label: `去重:${task.name}`, phase: 'Dedup', schema: DEDUP_SCHEMA, ...AGENT_OPTS })
    .then(r => ({ ...(r || { check_passed: false, cross_clean: false, rewritten: 0, skipped: [], notes: '代理未交卷' }), behavior: task.behavior, name: task.name, assigned: task.count })),
))
const done = results.filter(Boolean)
const bad = done.filter(r => !r.check_passed)
log(`改写 ${done.reduce((n, r) => n + (r.rewritten || 0), 0)}/${totalItems} 句；校验未过 ${bad.length} 个：${bad.map(r => r.name).join('、') || '无'}`)
return { results: done, check_failed: bad.map(r => r.behavior) }
