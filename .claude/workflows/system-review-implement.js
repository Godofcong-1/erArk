export const meta = {
  name: 'system-review-implement',
  description: 'erArk 系统复查 P5：按实施单元并行实施与单元复审，再跑全套回归与三视角复审',
  whenToUse: '由 system-review-round skill 在用户拍板、主代理改完共用文件之后调起；args 为方案、实施文档与实施单元表（字段见 .github/skills/system-review-round/tools/Workflow编排.md）',
  phases: [
    { title: 'Implement', detail: '每个实施单元一个代理，文件互不相交；随后单元复审' },
    { title: 'Regress', detail: '一个代理跑校验工具与全套回归' },
    { title: 'Audit', detail: '方案对照 / 测试覆盖 / 收尾与文档三个视角复审整体 diff' },
  ],
}

// ==== 输出结构 ====
const UNIT_RESULT = {
  type: 'object',
  properties: {
    changed_files: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
    tests_added: {
      type: 'array',
      items: { type: 'object', properties: { file: { type: 'string' }, name: { type: 'string' } }, required: ['file', 'name'] },
    },
    deviations: {
      type: 'array',
      description: '与方案不一致之处（没有照做或做法不同），交主代理先改方案再定夺',
      items: { type: 'object', properties: { what: { type: 'string' }, why: { type: 'string' } }, required: ['what', 'why'] },
    },
    needs_outside: {
      type: 'array',
      description: '需要改、但不在本单元文件清单里的改动',
      items: { type: 'object', properties: { file: { type: 'string' }, change: { type: 'string' } }, required: ['file', 'change'] },
    },
  },
  required: ['changed_files', 'summary', 'tests_added', 'deviations', 'needs_outside'],
}

const ISSUES = {
  type: 'object',
  properties: {
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['H', 'M', 'L'] },
          file: { type: 'string' },
          line: { type: 'integer' },
          issue: { type: 'string' },
          suggestion: { type: 'string' },
        },
        required: ['severity', 'file', 'issue'],
      },
    },
    p6_todo: { type: 'array', items: { type: 'string' }, description: '收尾阶段主代理还要做的事' },
  },
  required: ['issues'],
}

const REGRESS = {
  type: 'object',
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          command: { type: 'string' },
          exit_code: { type: 'integer' },
          log_path: { type: 'string' },
          pass: { type: 'integer' },
          fail: { type: 'integer' },
          failures: { type: 'array', items: { type: 'string' } },
        },
        required: ['command', 'exit_code', 'failures'],
      },
    },
    po_restored: { type: 'boolean' },
    notes: { type: 'string' },
  },
  required: ['results', 'po_restored'],
}

// ==== 参数校验：单元的文件集合必须互不相交 ====
const A = args || {}
const errors = []
for (const key of ['plan', 'impl', 'scratch']) if (typeof A[key] !== 'string' || !A[key]) errors.push(`缺少字符串参数 ${key}`)
if (!Array.isArray(A.units) || A.units.length === 0) errors.push('units 必须是非空数组')
if (!Array.isArray(A.regress_commands) || A.regress_commands.length === 0) errors.push('regress_commands 必须是非空数组（例：["./.conda/python.exe tools/tests/education/run_all.py"]）')
const owner = {}
const conflicts = []
for (const u of A.units || []) {
  if (!u || typeof u.id !== 'string' || typeof u.title !== 'string' || !Array.isArray(u.files) || u.files.length === 0) {
    errors.push(`实施单元缺字段（要有 id、title、非空 files）：${JSON.stringify(u)}`)
    continue
  }
  for (const f of u.files.concat(u.tests || [])) {
    const norm = String(f).replace(/\\/g, '/').toLowerCase()
    if (owner[norm] && owner[norm] !== u.id) conflicts.push(`${f}：${owner[norm]} 与 ${u.id}`)
    else owner[norm] = u.id
  }
}
if (conflicts.length) errors.push(`实施单元的文件相交（共用文件应由主代理先改好，测试文件也要分开）：${conflicts.join('；')}`)
if (errors.length) return { error: errors }
if (A.validateOnly) return { ok: true, units: A.units.map(u => u.id), agent_count: 0 }

const DOCS = `方案：${A.plan}
实施文档：${A.impl}`
let agentCount = 0
const counted = (p) => { agentCount += 1; return p }

const implementPrompt = (u) => `你是 erArk 系统复查实施阶段的实施代理，负责实施单元「${u.id}：${u.title}」。

## 依据
${DOCS}
先通读方案 §1~§5（接口与数据结构以方案 §4 为准），再读实施文档 ${(u.sections || []).join('、') || '§2 中与本单元相关的小节'}。

## 你名下的文件（只能改这些）
代码 / 数据：
${u.files.map(f => `- ${f}`).join('\n')}
测试：
${(u.tests || []).map(f => `- ${f}`).join('\n') || '- （无）'}

## 规则
- 只改上面列出的文件；需要改别的文件时不要改，写进 needs_outside
- 与方案不一致（照方案做不下去、或事实与方案冲突）时不要自作主张，写进 deviations，并按你认为对的做法实施、在代码注释里不提 Plan 编号以外的推测
- 代码规范照 CLAUDE.md：中文注释、每个函数有中文 docstring（参数、返回值、功能），Black 行宽 200
- 只允许用 ./.conda/python.exe -m py_compile <文件> 检查语法；**不跑测试、不跑 buildconfig、不跑游戏**（测试引导会触发增量构建写 data/*.json，其它单元在并行改文件）
- 不做任何 git 写操作（commit / stash / checkout / reset）
- 测试：在你名下的测试文件里为本单元的每条发现加断言（写法与夹具陷阱见测试目录的 README），断言名写清对应的发现编号
- 含反斜杠或中文的内容用 Write / Edit 工具写，不要走 Bash heredoc
- 全部用中文回答`

const unitReviewPrompt = (u, r) => `你是 erArk 系统复查实施阶段的单元复审代理，只读，复审实施单元「${u.id}：${u.title}」。

## 依据
${DOCS}（相关小节：${(u.sections || []).join('、') || '按单元标题在实施文档 §2 里找'}）

## 实施代理的自述
${r ? JSON.stringify({ summary: r.summary, deviations: r.deviations, needs_outside: r.needs_outside, tests_added: r.tests_added }) : '（实施代理没有返回结果）'}

## 做法
1. git diff -- ${u.files.concat(u.tests || []).join(' ')}
2. 逐条对照方案与实施文档：方案要求的点有没有漏、有没有做得不一样或多做了、接口签名与字段是否与方案 §4 一致
3. 检查：中文 docstring 与注释、前提函数是否纯函数（不写数据、不惰性创建）、新字段的存档回填、Tk / Web 两种绘制是否都走抽象绘制类、每条发现是否都有断言
4. 只报问题，不改任何文件，不做 git 写操作；全部用中文回答`

// ==== Implement ====
phase('Implement')
const unitResults = await pipeline(
  A.units,
  (u) => counted(agent(implementPrompt(u), { label: `实施:${u.id}`, phase: 'Implement', schema: UNIT_RESULT })),
  (r, u) => counted(agent(unitReviewPrompt(u, r), { label: `单元复审:${u.id}`, phase: 'Implement', schema: ISSUES })).then(review => ({ result: r, review })),
)

// ==== Regress（屏障：全部单元改完才能跑回归） ====
phase('Regress')
const scratch = A.scratch.replace(/[\\/]+$/, '')
const regress = await counted(agent(`你是 erArk 系统复查实施阶段的回归代理。全部实施单元已经改完，逐条运行下面的命令并汇报结果。

## 命令
${A.regress_commands.map((c, i) => `${i + 1}. ${c}`).join('\n')}

## 做法
- 每条命令都重定向到文件再读，不要接管道：timeout 600 <命令> > ${scratch}/regress_<序号>.log 2>&1; echo EXIT=$?
- 读日志末尾，取汇总行里的 PASS= / FAIL= 与失败断言名；run_all.py 的各文件日志在 %TEMP%/erArk_education_tests/ 之类的目录里，汇总行会写
- 全部跑完后执行 git status --short data/po/，有改动就 git checkout -- data/po/（本机无 gettext，构建会写乱 PO）；Script/Config/config_def.py 只多了空行时也还原
- 不修改任何代码或测试，不做其它 git 写操作；全部用中文回答`, { label: '全套回归', phase: 'Regress', schema: REGRESS }))

// ==== Audit ====
phase('Audit')
const LENSES = [
  { key: '方案对照', task: '逐条对照方案 §3 / §4 与实施文档 §2，列出没实现的、实现得不一样的、方案没写却多做了的' },
  { key: '测试覆盖', task: '方案里每条发现（H / M / L 编号）是否都有断言守住；实施文档 §2.0 复现表里「问题命中」的各项修好之后是否有断言锁定' },
  { key: '收尾与文档', task: '代码层面的配套是否齐：常量注册、ArkEditor 副本 CSV、存档回填、注释与 docstring 是否跟上新口径；再列出收尾阶段主代理还要做的事（说明文档、索引、总纲回指、测试 README、update.log）写进 p6_todo' },
]
const audits = await parallel(LENSES.map(l => () =>
  counted(agent(`你是 erArk 系统复查实施阶段的复审代理，视角是「${l.key}」，只读。

## 依据
${DOCS}
整体改动：git diff 与 git status（忽略工作区里与本次无关的 config.ini、.claude/settings.local.json、tools/ArkEditor/editor_config.ini）
回归结果：${regress ? JSON.stringify(regress.results.map(r => ({ command: r.command, exit_code: r.exit_code, fail: r.fail, failures: r.failures }))) : '（回归代理没有返回结果）'}

## 任务
${l.task}

只报问题，不改任何文件，不做 git 写操作；全部用中文回答。`, { label: `复审:${l.key}`, phase: 'Audit', schema: ISSUES })).then(r => (r ? { lens: l.key, ...r } : null)),
))

return {
  units: A.units.map((u, i) => {
    const item = unitResults[i]
    return { id: u.id, result: item ? item.result : null, review_issues: item && item.review ? item.review.issues : null }
  }),
  regress,
  audit: audits.filter(Boolean),
  agent_count: agentCount,
}
