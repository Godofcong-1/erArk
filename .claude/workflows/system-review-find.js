export const meta = {
  name: 'system-review-find',
  description: 'erArk 系统复查 P1~P3：按检查维度并行核查、逐条对抗式核实、补漏、写复现脚本',
  whenToUse: '由 system-review-round skill 在 P0 建档之后调起；args 为系统档案与已知清单（字段见 .github/skills/system-review-round/tools/Workflow编排.md）',
  phases: [
    { title: 'Find', detail: '每个检查维度一个只读核查代理' },
    { title: 'Verify', detail: '逐条对抗式核实，默认反驳' },
    { title: 'Critic', detail: '补漏代理；有缺口时追加一轮定向核查与核实' },
    { title: 'Repro', detail: '把存活的发现写成 scratchpad 复现脚本并运行' },
  ],
}

// ==== 内置检查维度（与 .github/skills/system-review-round/tools/复查清单.md 的七组一一对应） ====
const DEFAULT_DIMENSIONS = [
  {
    key: '设计对账',
    focus: '对照说明文档、总纲口径与既往方案，逐条核对「设计写了的是否真的实装且生效」：口径未实装、实装了但因调用时机或前提而不生效、提示文案 / 注释 / 文档与实际行为不符。先例：Plan 25 M1（口径 61/62 提前到岗实际不生效）、总纲 §8.1（口径 27 从未实装）。',
  },
  {
    key: '行为循环结构',
    focus: '沿 character_behavior 的行为循环推演：NPC 只在发呆时做决策、进行中的行为只有 judge_interrupt_character_behavior 能插手、结算发生在行为开始时、玩家一步可能跨过整个时间窗、寻路 wait_open 时一分钟一分钟地空转。找「按单个函数看都对、放进循环里就断」的地方。先例：Plan 25 §2.3、总纲 §10.1 #2。',
  },
  {
    key: '判定口径一致',
    focus: '同一件事被多处判定时是否同口径：「可用 / 能参加」类判定与目标行 normal 前提是否同步；玩家指令与 NPC 状态机两个入口是否各写一套；取数口是否统一（下游不要各自再判一次）；前提函数是否纯函数（不写数据、不惰性创建）。先例：Plan 25 M3（醉酒教师被判可用）、Plan 25 M5（303 拉人绕过两道闸）、Plan 24 §2.6-1。',
  },
  {
    key: '身份阶段岗位过滤',
    focus: '遍历角色或名单的地方是否漏了身份过滤：改岗后的残留数据、成年 / 未成年阶段、婴儿不在 npc_id_got、非女儿、离线 / 住院 / 外勤 / 不在岛上。先例：Plan 28 H1（婴儿期事件从未派出）、Plan 30 L3（改岗萝莉仍判有课与同学）、Plan 30 M3。',
  },
  {
    key: '计数去重与时序',
    focus: '累计值与标记：同一时段记两次、同一时段记两种互斥记录、基线重置之后才读本期数值、跨天结算的先后顺序、结算幂等、临时数据 / 覆盖层下课后泄漏进每周数据、派活地点未开放、复用既有行为却缺了它原本的前置步骤。先例：Plan 30 L1 / M2、总纲 §10.1 #8、Plan 27 M1、Plan 29 M2。',
  },
  {
    key: '数据死内容与校验',
    focus: '逐条检查本系统的 CSV / 口上 / 公务事件的前提 token：前提在推送或触发时刻永远判不过的死内容、token 拼错、引用了不存在的编号、正文与前提对不上；发现死内容时同时想「校验工具加哪条规则能防复发」。先例：Plan 30 M2（期末 9 / 10 永远推不出来）。',
  },
  {
    key: '代码卫生与夹具',
    focus: '死代码（注册式调用按注册表判断，不算死代码）、写死的编号（应从常量或配置取）、对已翻译常量又包一层 _()、过期注释与文档、未用 import、TODO；回归测试夹具是否与真实数据对齐（夹具偏离真实会让问题多轮测不出来）。先例：Plan 25 L3~L5、说明文档「婴儿夹具让问题八轮没测出来」。',
  },
]

// ==== 输出结构 ====
const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string', description: '一句话结论' },
          severity_guess: { type: 'string', enum: ['H', 'M', 'L'] },
          evidence: {
            type: 'array',
            items: {
              type: 'object',
              properties: { file: { type: 'string' }, line: { type: 'integer' }, symbol: { type: 'string' } },
              required: ['file', 'line'],
            },
          },
          mechanism: { type: 'string', description: '为什么会出问题：代码层面的机理' },
          trigger: { type: 'string', description: '在游戏里怎么触发：玩家或 NPC 的真实操作路径' },
          repro_idea: { type: 'string', description: '无头复现的思路：造什么角色、调哪个函数、断言什么' },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['title', 'severity_guess', 'evidence', 'mechanism', 'trigger', 'confidence'],
      },
    },
    cleared: {
      type: 'array',
      description: '查过、结论是没有问题的疑点（进方案 §2.3）',
      items: {
        type: 'object',
        properties: { suspect: { type: 'string' }, conclusion: { type: 'string' }, evidence: { type: 'string' } },
        required: ['suspect', 'conclusion'],
      },
    },
    read_scope: { type: 'array', items: { type: 'string' }, description: '实际逐行读过的文件或函数' },
  },
  required: ['findings', 'cleared', 'read_scope'],
}

const VERDICT = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
    evidence: { type: 'string', description: '支持结论的 file:line' },
    corrected_mechanism: { type: 'string', description: '发现成立但机理或范围需要修正时填写' },
    repro_check: { type: 'string', description: '一条能在无头环境里断言的检查' },
  },
  required: ['refuted', 'reason', 'evidence'],
}

const GAPS = {
  type: 'object',
  properties: {
    gaps: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          kind: { type: 'string', enum: ['unread', 'dimension', 'claim'] },
          target: { type: 'string' },
          why: { type: 'string' },
          focus: { type: 'string', description: '给追加核查代理的具体任务' },
        },
        required: ['kind', 'target', 'why', 'focus'],
      },
    },
  },
  required: ['gaps'],
}

const REPRO = {
  type: 'object',
  properties: {
    script_path: { type: 'string' },
    log_path: { type: 'string' },
    groups: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          group: { type: 'string' },
          finding: { type: 'string' },
          checks: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                idx: { type: 'integer' },
                desc: { type: 'string' },
                holds: { type: 'boolean' },
                category: { type: 'string', enum: ['问题命中', '前提对照', '数据事实', '随口径'] },
                after: { type: 'string', description: '修好之后这一项预期成立还是不成立' },
              },
              required: ['idx', 'desc', 'holds', 'category', 'after'],
            },
          },
        },
        required: ['group', 'finding', 'checks'],
      },
    },
    not_reproduced: {
      type: 'array',
      items: { type: 'object', properties: { finding: { type: 'string' }, why: { type: 'string' } }, required: ['finding', 'why'] },
    },
    summary: { type: 'string' },
  },
  required: ['script_path', 'groups', 'not_reproduced', 'summary'],
}

// ==== 参数校验 ====
const A = args || {}
const errors = []
for (const key of ['system', 'scratch']) if (typeof A[key] !== 'string' || !A[key]) errors.push(`缺少字符串参数 ${key}`)
for (const key of ['round', 'plan_no']) if (typeof A[key] !== 'number') errors.push(`缺少数字参数 ${key}`)
if (!Array.isArray(A.modules) || A.modules.length === 0) errors.push('modules 必须是非空数组')
let dimensions = DEFAULT_DIMENSIONS
if (Array.isArray(A.dimensions) && A.dimensions.length) {
  dimensions = []
  for (const d of A.dimensions) {
    if (typeof d === 'string') {
      const hit = DEFAULT_DIMENSIONS.find(x => x.key === d)
      if (hit) dimensions.push(hit)
      else errors.push(`未知维度 ${d}（内置：${DEFAULT_DIMENSIONS.map(x => x.key).join(' / ')}）`)
    } else if (d && typeof d.key === 'string' && typeof d.focus === 'string') dimensions.push(d)
    else errors.push('dimensions 的元素要么是内置维度名，要么是 {key, focus}')
  }
}
if (errors.length) return { error: errors }
if (A.validateOnly) return { ok: true, dimensions: dimensions.map(d => d.key), agent_count: 0 }

// ==== 公共提示词片段 ====
const list = (arr) => (Array.isArray(arr) && arr.length ? arr.map(x => `- ${typeof x === 'string' ? x : JSON.stringify(x)}`).join('\n') : '- （无）')
const K = A.known || {}
const DOSSIER = `## 系统档案
系统：${A.system}（第 ${A.round} 轮复查，Plan ${A.plan_no}，代码快照 ${A.snapshot || '未提供'}）
模块：
${list(A.modules)}
外部挂接点：
${list(A.hooks)}
数据文件：
${list(A.data)}
说明文档：
${list(A.docs)}
回归测试套件：${A.tests || '（无）'}`
const KNOWN = `## 已知清单（这些都不要再报成发现；若你认为其中某条结论已经不成立，写进 cleared 并说明新证据）
已拍板的口径：
${list(K.decided)}
既往轮次排查过、没有问题的疑点：
${list(K.cleared)}
不在范围内的事项：
${list(K.out_of_scope)}
既往轮次尚未覆盖的验证：
${list(K.uncovered)}`
const RULES = `## 规则
- 只读：不修改仓库里任何文件，不跑构建、不跑游戏、不跑测试，不做任何 git 写操作
- 每条发现都要有 file:line 与函数名作证据，并写清触发路径；拿不到依据的写 confidence=low，不要写成事实
- 逐行读代码，不凭命名或注释推断行为；注册式调用（装饰器注册、register_* 注册表）不算死代码
- 全部用中文回答`

let agentCount = 0
const counted = (p) => { agentCount += 1; return p }
const keyOf = (f) => {
  const ev = (f.evidence || [])[0] || {}
  return { file: String(ev.file || '').replace(/\\/g, '/').toLowerCase(), line: ev.line || 0 }
}
const RANK = { H: 0, M: 1, L: 2 }

// 按标题或相邻行号归并重复发现（纯代码，不是代理）
const mergeInto = (pool, items) => {
  const fresh = []
  for (const f of items) {
    const k = keyOf(f)
    const hit = pool.find(o => o.title === f.title || (k.file && o._file === k.file && Math.abs(o._line - k.line) <= 3))
    if (hit) {
      if (!hit.dimensions.includes(f.dimension)) hit.dimensions.push(f.dimension)
      if (RANK[f.severity_guess] < RANK[hit.severity_guess]) hit.severity_guess = f.severity_guess
      hit.evidence = hit.evidence.concat(f.evidence || [])
      if (f.title !== hit.title) hit.merged_titles.push(f.title)
    } else {
      const entry = { ...f, dimensions: [f.dimension], merged_titles: [], _file: k.file, _line: k.line }
      pool.push(entry)
      fresh.push(entry)
    }
  }
  return fresh
}

const findPrompt = (d) => `你是 erArk「${A.system}」第 ${A.round} 轮复查的核查代理，负责「${d.key}」这一个维度。

${DOSSIER}

${KNOWN}

## 本维度要查什么
${d.focus}

## 做法
1. 逐行读档案里的模块，再按挂接点清单逐个读外部调用处（必要时自己 grep 补全调用方）
2. 只报本维度的问题；顺手看到的其它维度问题可以报，但 title 前加「[其它维度]」
3. 查过、确认没有问题的疑点写进 cleared，免得下一轮重复排查

${RULES}`

const verifyLenses = (f) => {
  const lenses = ['读代码反驳：逐行读证据位置及其全部调用方，找出能让这条发现不成立的守卫、提前返回、其它写入点或被忽略的前提']
  if (f.severity_guess !== 'L') lenses.push('推演触发路径：从玩家或 NPC 的真实操作出发，推演触发条件在游戏里能否真的走到（前提、时序、状态机派发、跨天顺序），走不到就判为反驳')
  return lenses
}
const verifyPrompt = (f, lens) => `你是 erArk「${A.system}」复查的核实代理。下面这条发现由另一个代理报告，你的任务是**尽力反驳它**；拿不准时判 refuted=true。

## 发现
标题：${f.title}
严重度猜测：${f.severity_guess}
证据：${JSON.stringify(f.evidence)}
机理：${f.mechanism}
触发：${f.trigger}
${f.merged_titles.length ? `合并进来的同类发现：${f.merged_titles.join('；')}` : ''}

## 你的视角
${lens}

${KNOWN}

${RULES}
- 发现成立但机理或范围要修正时，refuted=false 并填 corrected_mechanism
- 无论结论如何，都给一条能在无头环境里断言的 repro_check`

// 对一批发现做对抗式核实，返回带投票结果的发现
const verifyAll = (items, phaseName) => pipeline(items, (f) =>
  parallel(verifyLenses(f).map((lens, i) => () =>
    counted(agent(verifyPrompt(f, lens), { label: `核实:${f.title.slice(0, 18)}#${i + 1}`, phase: phaseName, schema: VERDICT })),
  )).then((votes) => {
    const valid = votes.filter(Boolean)
    const refutes = valid.filter(v => v.refuted).length
    return { ...f, votes: valid, killed: valid.length > 0 && refutes * 2 > valid.length }
  }),
)

// ==== Find ====
phase('Find')
const found = await parallel(dimensions.map(d => () =>
  counted(agent(findPrompt(d), { label: `核查:${d.key}`, phase: 'Find', schema: FINDINGS })).then(r => (r ? { ...r, dimension: d.key } : null)),
))
const reports = found.filter(Boolean)
if (reports.length < dimensions.length) log(`有 ${dimensions.length - reports.length} 个维度的核查代理没有返回结果`)
const pool = []
const cleared = []
const readScope = new Set()
for (const r of reports) {
  mergeInto(pool, r.findings.map(f => ({ ...f, dimension: r.dimension })))
  r.cleared.forEach(c => cleared.push({ ...c, dimension: r.dimension }))
  r.read_scope.forEach(s => readScope.add(s))
}
log(`核查完毕：${reports.length} 个维度共报 ${reports.reduce((n, r) => n + r.findings.length, 0)} 条，归并后 ${pool.length} 条`)

// ==== Verify ====
phase('Verify')
let judged = (await verifyAll(pool, 'Verify')).filter(Boolean)

// ==== Critic（补漏，只追加一轮） ====
phase('Critic')
const critic = await counted(agent(`你是 erArk「${A.system}」第 ${A.round} 轮复查的补漏代理。其它代理已经按维度核查并核实完毕，你要找出**还没覆盖到的地方**。

${DOSSIER}

## 已覆盖
检查维度：${dimensions.map(d => d.key).join(' / ')}
实际读过的范围：
${list([...readScope])}
存活的发现：
${list(judged.filter(f => !f.killed).map(f => f.title))}
被驳倒的发现：
${list(judged.filter(f => f.killed).map(f => f.title))}

## 要找的缺口
- unread：档案里列了、但没人读过的模块 / 挂接点 / 数据文件
- dimension：某个维度明显只查了一部分（例如只看了 Python 没看 CSV）
- claim：存活发现里有没被核实到的关键说法
每个缺口给一条具体的 focus，交给追加的核查代理去做。没有缺口就返回空数组。

${RULES}`, { label: '补漏', phase: 'Critic', schema: GAPS }))
const gaps = critic ? critic.gaps : []
const maxGap = typeof A.maxGapAgents === 'number' ? A.maxGapAgents : 4
const dropped = []
if (gaps.length > maxGap) {
  gaps.slice(maxGap).forEach(g => dropped.push(`缺口未追查：${g.kind} ${g.target}`))
  log(`补漏发现 ${gaps.length} 个缺口，只追查前 ${maxGap} 个，其余记在返回值 dropped 里`)
}
if (gaps.length && A.followUp !== false) {
  const extra = await parallel(gaps.slice(0, maxGap).map((g, i) => () =>
    counted(agent(findPrompt({ key: `补漏${i + 1}`, focus: `${g.focus}\n（缺口类型 ${g.kind}：${g.target}；原因：${g.why}）` }), { label: `补漏核查#${i + 1}`, phase: 'Critic', schema: FINDINGS }))
      .then(r => (r ? { ...r, dimension: `补漏${i + 1}` } : null)),
  ))
  const extraFresh = []
  for (const r of extra.filter(Boolean)) {
    extraFresh.push(...mergeInto(pool, r.findings.map(f => ({ ...f, dimension: r.dimension }))))
    r.cleared.forEach(c => cleared.push({ ...c, dimension: r.dimension }))
    r.read_scope.forEach(s => readScope.add(s))
  }
  log(`追加核查新增 ${extraFresh.length} 条`)
  judged = judged.concat((await verifyAll(extraFresh, 'Critic')).filter(Boolean))
}
const confirmed = judged.filter(f => !f.killed).sort((a, b) => RANK[a.severity_guess] - RANK[b.severity_guess])
const refuted = judged.filter(f => f.killed)

// ==== Repro ====
let repro = null
if (A.repro !== false && confirmed.length) {
  phase('Repro')
  const dir = `${A.scratch.replace(/[\\/]+$/, '')}/p${A.plan_no}`
  repro = await counted(agent(`你是 erArk「${A.system}」第 ${A.round} 轮复查的复现代理。把下面每条存活的发现写成无头复现检查，并真的跑出结果。

## 发现
${confirmed.map((f, i) => `${i + 1}. [${f.severity_guess}] ${f.title}
   证据：${JSON.stringify(f.evidence)}
   机理：${f.corrected_mechanism || f.mechanism}
   复现思路：${f.repro_idea || '（无）'}；核实代理给的检查：${f.votes.map(v => v.repro_check).filter(Boolean).join('；') || '（无）'}`).join('\n')}

## 做法
1. 以 .github/skills/system-review-round/repro_template.py 为骨架，写到 ${dir}/repro_plan${A.plan_no}.py（用 Write 工具写文件，不要用 heredoc）
2. 引导：${A.tests ? `把 ${A.tests} 加进 sys.path 后 from _bootstrap import *（fixture 陷阱见该目录 README）` : '本系统没有回归套件，照 .claude/skills/headless-game-test/SKILL.md 模式 A 自建引导'}
3. 每条发现一组 R 检查，每项的「成立」都表示「问题现在确实存在」；另外补前提对照（证明夹具真的走到了那条路径）与数据事实；每项写明修好之后预期成立还是不成立
4. 运行：timeout 300 ./.conda/python.exe -u <脚本> > ${dir}/repro.log 2>&1，读日志；脚本报错就修到能跑完
5. 复现不出来的发现写进 not_reproduced 并说明原因，不要硬凑
6. 只写 ${dir} 下的文件，不改仓库；跑完如果 git status 里出现 data/po/ 的改动，执行 git checkout -- data/po/

全部用中文回答。`, { label: '复现脚本', phase: 'Repro', schema: REPRO }))
}

return {
  system: A.system,
  round: A.round,
  plan_no: A.plan_no,
  confirmed: confirmed.map(({ _file, _line, ...f }) => f),
  refuted: refuted.map(({ _file, _line, ...f }) => f),
  cleared,
  read_scope: [...readScope],
  gaps,
  dropped,
  repro,
  agent_count: agentCount,
}
