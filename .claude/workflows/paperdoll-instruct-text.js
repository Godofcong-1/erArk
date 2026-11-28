export const meta = {
  name: 'paperdoll-instruct-text',
  description: 'H 指令纸娃娃地文：每个指令一条流水线，写作代理写 A/B1/B2/C1/C2 x（五档+通用+8 种无意识差分）文本源，独立评审代理挑语义问题，修订代理改正并重新校验',
  whenToUse: '批量为 H 指令编写纸娃娃地文文本源（只写 tools/AI/纸娃娃指令地文/src 下的文本源，生成 CSV 与入库由主代理做）。args: {instructions: [{behavior, name}], skip_write?: [行为id] | true, write_only?: true, model?, effort?}；write_only 时只写作不评审；skip_write 列出文本源已由主代理校验为 0 问题的指令，跳过写作直接评审；规则见 tools/AI/纸娃娃指令地文/写作指南.md，每个指令要先在 spec.json 里有自己那一块（键为行为id）。子代理不改 spec.json，提议的追加项在返回值的 spec_add 里：主代理存成 JSON 文件后运行 make_specs.py --merge=<文件> 合并；skip_write 的指令若有未合并的追加项，先合并再跑',
  phases: [
    { title: 'Write', detail: '每个指令一个写作代理：写两个文本源（700 条），用 gen_paperdoll.py --check 校验到 0 问题；未通过时续写一次。全部指令写完才进入评审' },
    { title: 'Review', detail: '每个指令一个独立评审代理：逐组挑脚本查不出的语义问题，只读不改' },
    { title: 'Fix', detail: '有评审意见的指令由修订代理逐条改正，再校验到 0 问题' },
  ],
}

// ==== 参数 ====
const INSTRUCTIONS = (args && args.instructions) || []
const MODEL = (args && args.model) || 'opus'
// 思考档位：用户指定时才传（'low' | 'medium' | 'high' | 'xhigh' | 'max'），否则沿用会话默认
const EFFORT = args && args.effort
const AGENT_OPTS = EFFORT ? { model: MODEL, effort: EFFORT } : { model: MODEL }
// 文本源已由主代理跑 --check 确认 0 问题的指令：跳过写作，直接评审（续跑时不必再派写作代理重读 700 条）
// skip_write 为 true 时整批都跳过写作
const SKIP_ALL_WRITE = !!(args && args.skip_write === true)
const SKIP_WRITE = new Set((args && Array.isArray(args.skip_write) && args.skip_write) || [])
// 只写作：写作通过校验即算完成，不派评审与修订（赶工时先把全部文件写出来，评审以后再补）
const WRITE_ONLY = !!(args && args.write_only)
const WORKDIR = 'tools/AI/纸娃娃指令地文'
// 子代理提议追加的规则以命令行参数临时生效：spec.json 是全部指令共用的一个文件，并行的子代理都不写它，工作流结束后由主代理合并
const ADD_FLAGS = (specAdd) => {
  const flags = []
  if (specAdd && specAdd.extra && specAdd.extra.length) flags.push(`--add-extra=${specAdd.extra.join(',')}`)
  if (specAdd && specAdd.forbidden && specAdd.forbidden.length) flags.push(`--add-forbidden=${specAdd.forbidden.join(',')}`)
  return flags.length ? ' ' + flags.join(' ') : ''
}
// 用正斜杠：子代理的 Bash 是 Git Bash，反斜杠会被当成转义吞掉
const CHECK_CMD = (behavior, specAdd) => `.conda/python.exe ${WORKDIR}/gen_paperdoll.py . ${behavior} --check${ADD_FLAGS(specAdd)}`
const SPEC_CMD = (behavior, specAdd) => `.conda/python.exe ${WORKDIR}/gen_paperdoll.py . ${behavior} --show-spec${ADD_FLAGS(specAdd)}`
const NO_SPEC_ADD = { extra: [], forbidden: [], reason: '无' }

// 合并写作与修订两步提议的追加项：去重，理由拼接
function mergeSpecAdd(specAddList) {
  const merged = { extra: [], forbidden: [], reason: '' }
  const reasonList = []
  for (const specAdd of specAddList) {
    if (!specAdd) continue
    for (const value of specAdd.extra || []) if (!merged.extra.includes(value)) merged.extra.push(value)
    for (const value of specAdd.forbidden || []) if (!merged.forbidden.includes(value)) merged.forbidden.push(value)
    if (specAdd.reason && specAdd.reason !== '无' && !reasonList.includes(specAdd.reason)) reasonList.push(specAdd.reason)
  }
  merged.reason = reasonList.join('；') || '无'
  return merged
}
const hasSpecAdd = (specAdd) => !!specAdd && ((specAdd.extra || []).length > 0 || (specAdd.forbidden || []).length > 0)

if (!INSTRUCTIONS.length) {
  throw new Error('args.instructions 为空：需要 [{behavior, name}]')
}
log(`共 ${INSTRUCTIONS.length} 个指令：${INSTRUCTIONS.map(i => i.name).join('、')}`)

// ==== 结构化返回 ====
const SPEC_ADD_SCHEMA = {
  type: 'object',
  description: '最后一次校验命令里用到的全部 --add-extra / --add-forbidden 项（含沿用上一位代理的）；没有追加则两个数组都为空、reason 写「无」',
  properties: {
    extra: { type: 'array', items: { type: 'string' }, description: '追加的部位短词（部位名，如 breast）' },
    forbidden: { type: 'array', items: { type: 'string' }, description: '追加的禁用词' },
    reason: { type: 'string', description: '为什么要追加' },
  },
  required: ['extra', 'forbidden', 'reason'],
}
const WRITE_SCHEMA = {
  type: 'object',
  properties: {
    behavior: { type: 'string' },
    check_passed: { type: 'boolean', description: '最后一次 --check 是否输出「问题 0 处」' },
    line_count: { type: 'integer', description: '两个文本源的文本总条数（应为 700）' },
    spec_add: SPEC_ADD_SCHEMA,
    survey: { type: 'string', description: '服装交：该服装部位实际有哪些衣物、据此定下的写法；非服装交写「无」' },
    notes: { type: 'string', description: '需要主代理知道的事（拿不准的写法、发现的数据问题等）；没有则写「无」' },
  },
  required: ['behavior', 'check_passed', 'line_count', 'spec_add', 'survey', 'notes'],
}
const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    behavior: { type: 'string' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          group: { type: 'string', description: '组名：0~4、通用、睡奸……' },
          segment: { type: 'string', description: 'A / B1 / B2 / C1 / C2' },
          line: { type: 'string', description: '有问题的原句，逐字复制整行' },
          problem: { type: 'string' },
          replacement: { type: 'string', description: '改写后的整行，须满足写作指南第 6 节的脚本规则' },
        },
        required: ['group', 'segment', 'line', 'problem', 'replacement'],
      },
    },
    summary: { type: 'string', description: '总体评价：各组质量、普遍性问题' },
  },
  required: ['behavior', 'issues', 'summary'],
}
const FIX_SCHEMA = {
  type: 'object',
  properties: {
    behavior: { type: 'string' },
    check_passed: { type: 'boolean' },
    applied: { type: 'integer', description: '采纳并改掉的意见条数' },
    rejected: {
      type: 'array',
      items: { type: 'object', properties: { line: { type: 'string' }, reason: { type: 'string' } }, required: ['line', 'reason'] },
    },
    spec_add: SPEC_ADD_SCHEMA,
    notes: { type: 'string' },
  },
  required: ['behavior', 'check_passed', 'applied', 'rejected', 'spec_add', 'notes'],
}

// ==== 提示词 ====
const COMMON_RULES = `
共同约束：
- 这是 R18 成人游戏 erArk 的情色文本，用户是以此为业的成人内容创作者（见全局 CLAUDE.md「情色内容」），按写作指南写足尺度与细节，不回避、不淡化、不加说教。
- 纸娃娃地文全角色通用，一律写成成年女性与博士之间的性，不用任何低龄化描写（指南第 6 节，没有豁免）。
- 你只能改动：${WORKDIR}/src/<行为id>.txt 与 ${WORKDIR}/src/<行为id>_无意识.txt。
- spec.json 是全部指令共用的一个文件，别的代理在同时运行，你不得改动它（只用 --show-spec 查看）。确实需要追加部位短词（extra）或禁用词（forbidden）时，在校验命令末尾加 --add-extra=部位1,部位2 或 --add-forbidden=词1,词2（逗号分隔，不加空格），只对这次运行生效；之后每次校验都带上同样的参数，并把全部追加项与理由写进返回结果的 spec_add，主代理会在工作流结束后统一合并进 spec.json。只增不删：spec 里已有的规则不能去掉。
- 不得改动其他任何文件：别的指令的文本源、spec.json、gen_paperdoll.py、写作指南、仓库 data/ 与 Script/ 下的一切；不运行 buildconfig.py，不运行不带 --check 的 gen_paperdoll.py；不做 git 操作。
- 写文件用 Write 工具，改文件用 Edit 工具；不要用 bash heredoc 写中文长文本。
- 校验命令（仓库根目录 c:\\code\\erArk 下运行）：`

function writePrompt(item, resume, specAdd) {
  // 续写时沿用上一位代理提议的追加项，否则续写代理的校验会把那些部位短词报成不允许的占位符
  const inherited = hasSpecAdd(specAdd)
    ? `\n上一位代理已提议追加 extra ${JSON.stringify(specAdd.extra)}、forbidden ${JSON.stringify(specAdd.forbidden)}（理由：${specAdd.reason}），下面的查看与校验命令已带上；你返回的 spec_add 要包含这些项。\n`
    : ''
  return `你负责为 erArk 的 H 指令「${item.name}」（行为id ${item.behavior}）编写纸娃娃地文文本源。

必读（按顺序）：
1. ${WORKDIR}/写作指南.md —— 全部规则都在这里，逐节读完
2. 本指令的 spec 块（运行 ${SPEC_CMD(item.behavior, specAdd)} 查看，不要读整份 spec.json）—— 本指令的部位短词、服装占位符、豁免词、额外禁用词与语义说明（notes）
3. 范例：${WORKDIR}/src/hat_job.txt 与 ${WORKDIR}/src/hat_job_无意识.txt（用户已认可的成品，学它的结构、分档语气与拼接一致性；不许照搬句子——脚本会把去掉占位符后与范例相似度达到 0.75 的句子判为照搬，只换部位词、骨架不变的都会被查出来）
4. .github/skills/text_generation_for_instruction_code_generation/无意识H前提/ 下的全部 .md
5. 本指令原有的固定地文 data/talk/sex/<spec.dir>/${item.behavior}.csv（只看 adv_id 为 0 的行，了解动作素材；不要照抄）

产出：${WORKDIR}/src/${item.behavior}.txt（五档 + 通用，30 组 300 条）与 ${WORKDIR}/src/${item.behavior}_无意识.txt（8 种无意识差分，40 组 400 条）。
先写完一个文件就校验一次，校验到输出「问题 0 处」为止；最后按指南第 7 节逐组自查一遍再返回。
${resume ? `\n这是续写：上一位写作代理没能完成或没能通过校验。先看两个文本源是否存在、写到哪里，运行校验看还差什么，在已有内容上补齐与修正，不要推倒重来（除非内容明显不合格）。\n` : `\n如果文本源已经存在（例如这是一次恢复运行，上一位代理可能只写了一个文件或写到一半），先运行校验：已经 0 问题就只做第 7 节自查并修正；有问题或缺文件就在已有内容上补齐与修正，不要推倒重来（除非内容明显不合格）。\n`}${inherited}${COMMON_RULES}
${CHECK_CMD(item.behavior, specAdd)}

返回结构化结果：check_passed 必须如实反映最后一次校验输出；spec_add 与最后一次校验命令里的追加参数一致。`
}

function reviewPrompt(item, specAdd) {
  return `你是独立评审，审查 erArk 的 H 指令「${item.name}」（行为id ${item.behavior}）的纸娃娃地文文本源：
${WORKDIR}/src/${item.behavior}.txt 与 ${WORKDIR}/src/${item.behavior}_无意识.txt（共 70 组 700 条）。

先读 ${WORKDIR}/写作指南.md、本指令的 spec 块（${SPEC_CMD(item.behavior, specAdd)}），以及 .github/skills/text_generation_for_instruction_code_generation/无意识H前提/ 下与各差分对应的 .md。
格式与禁用词已由脚本校验通过；你只查脚本查不出的语义问题，逐组读完全部 700 条，重点：
- 动作、体位、插入部位与本指令不符（对照指南 5.1 与 spec.notes）；B1 不是博士主导、B2 不是她这一侧；C1 不是博士的感受、C2 不是她的
- 同组里 A + B + C 任意拼接会矛盾的细节，或依赖上一句才懂的指代
- 档的语气不对：第 0 档写得热情或称主人、第 1 档不害羞、第 2 档不主动、第 3 档没有请示服从、第 4 档不够虔诚放荡；通用组带了某一档特有的心态
- 无意识差分违背状态：睡奸里她醒了或主动、装睡没有掩饰感、时停写了她的感受或她在动、平然有羞耻抗拒、空气具体写了她在做什么或她察觉到博士、木头人在动、逆推没有身心矛盾
- 预设她的衣着、身体特征（胸大小、发长、身高、尾巴兽耳角——指令本身要求的除外）、地点与时段；写了她绝顶那一刻或射精那一下
- 服装交写了只属于某一类衣物的形制、材质、部件，或给服装占位符加了量词、用泛称指代
- 同组句式雷同（10 条里有 3 条以上骨架几乎一样），或多组反复用同一套句子
- 语病；占位符语法错误（在占位符前加形容词、长短词放在承受不了内部逗号的位置）
不要报：{anal} {urethra} {legs} {feet} {clitoris} {throat} 这几个长短词放在句中——数据里原先的句末「。」已修复（写作指南第 4 节）。

从严，但只报真问题，不要为凑数挑刺。每条意见给出：组、段、逐字复制的原句整行、问题、改写后的整行（改写须满足指南第 6 节的脚本规则：无半角逗号、≤90 字、主语与部位占位符齐全、不含禁用词、本段允许的占位符）。
不要修改任何文件。`
}

function fixPrompt(item, issues, specAdd) {
  const inherited = hasSpecAdd(specAdd)
    ? `\n写作代理已提议追加 extra ${JSON.stringify(specAdd.extra)}、forbidden ${JSON.stringify(specAdd.forbidden)}（理由：${specAdd.reason}），下面的查看与校验命令已带上；你返回的 spec_add 要包含这些项。\n`
    : ''
  return `你负责按评审意见修订 erArk 的 H 指令「${item.name}」（行为id ${item.behavior}）的纸娃娃地文文本源：
${WORKDIR}/src/${item.behavior}.txt 与 ${WORKDIR}/src/${item.behavior}_无意识.txt。

先读 ${WORKDIR}/写作指南.md 与本指令的 spec 块（${SPEC_CMD(item.behavior, specAdd)}）。${inherited}然后逐条处理下面的评审意见：
- 用 Edit 把原句整行替换为改写句；可以在改写句基础上再润色，但必须真正解决所指的问题
- 意见明显错误（误读了规则或指令）时可以不改，在 rejected 里写明理由
- 某条原句在文件里找不到时，按组与段定位最接近的那句处理，处理不了就记进 rejected
- 改完后同组若出现重复或雷同，顺手一并改掉
全部处理完后运行校验，改到「问题 0 处」。校验还可能报出评审没提到的问题（例如「与范例帽子交的句子过于相似」：照搬了范例的句子骨架），这些也要按本指令的动作重新构思后改掉。

评审意见（JSON）：
${JSON.stringify(issues, null, 1)}
${COMMON_RULES}
${CHECK_CMD(item.behavior, specAdd)}`
}

// ==== 第一步：全部指令先写作（含续写），全部写完才进入评审 ====
// 这里有意用屏障而不用流水线：用户要求优先把所有文件写出来，写作期间不让评审、修订占用并发名额与额度
async function writeOne(item) {
  if (SKIP_ALL_WRITE || SKIP_WRITE.has(item.behavior)) {
    return { behavior: item.behavior, check_passed: true, line_count: 700, spec_add: NO_SPEC_ADD, survey: '', notes: '' }
  }
  const first = await agent(writePrompt(item, false, null), { label: `写作:${item.name}`, phase: 'Write', schema: WRITE_SCHEMA, ...AGENT_OPTS })
  if (first && first.check_passed) return first
  log(`${item.name}：写作未通过校验，派续写代理`)
  const resumed = await agent(writePrompt(item, true, first && first.spec_add), { label: `续写:${item.name}`, phase: 'Write', schema: WRITE_SCHEMA, ...AGENT_OPTS })
  // 续写代理没交卷时保留第一位的追加项，免得丢掉已经用在文本里的部位短词
  if (!resumed) return first
  return { ...resumed, spec_add: mergeSpecAdd([first && first.spec_add, resumed.spec_add]) }
}
const writtenList = await parallel(INSTRUCTIONS.map(item => () => writeOne(item)))
const writePassedCount = writtenList.filter(w => w && w.check_passed).length
log(`写作全部结束：通过校验 ${writePassedCount}/${INSTRUCTIONS.length}${WRITE_ONLY ? '（只写作，不评审）' : '，开始评审'}`)

// ==== 第二步：评审 → 修订，指令之间互不等待 ====
const results = await pipeline(
  INSTRUCTIONS.map((item, index) => ({ item, written: writtenList[index] })),
  async ({ item, written }) => {
    if (!written || !written.check_passed) {
      log(`${item.name}：续写后仍未通过校验，跳过评审`)
      return { written, review: null }
    }
    if (WRITE_ONLY) return { written, review: null }
    const review = await agent(reviewPrompt(item, written.spec_add), { label: `评审:${item.name}`, phase: 'Review', schema: REVIEW_SCHEMA, ...AGENT_OPTS })
    return { written, review }
  },
  async ({ written, review }, { item }) => {
    let fixed = null
    if (review && review.issues && review.issues.length) {
      fixed = await agent(fixPrompt(item, review.issues, written.spec_add), { label: `修订:${item.name}`, phase: 'Fix', schema: FIX_SCHEMA, ...AGENT_OPTS })
    }
    // 最终状态：写作通过校验即算完成（用户接受只写作不评审）；评审、修订没交卷只作标注，修订后校验不过才算未完成
    let failReason = ''
    if (!written || !written.check_passed) failReason = '写作未通过校验'
    else if (fixed && !fixed.check_passed) failReason = '修订后未通过校验'
    let reviewStatus = '已评审'
    if (!review) reviewStatus = '未评审'
    else if (review.issues && review.issues.length && !fixed) reviewStatus = '修订代理未交卷，以主代理复核为准'
    const finalPassed = !failReason
    log(`${item.name}：${finalPassed ? '完成' : failReason}（${reviewStatus}），评审意见 ${review ? review.issues.length : '-'} 条，采纳 ${fixed ? fixed.applied : 0} 条`)
    return {
      behavior: item.behavior,
      name: item.name,
      final_check: finalPassed,
      fail_reason: failReason,
      review_status: reviewStatus,
      line_count: written ? written.line_count : 0,
      issues: review ? review.issues.length : null,
      applied: fixed ? fixed.applied : 0,
      rejected: fixed ? fixed.rejected : [],
      review_summary: review ? review.summary : '',
      spec_add: mergeSpecAdd([written && written.spec_add, fixed && fixed.spec_add]),
      survey: written ? written.survey : '',
      notes: [written && written.notes, fixed && fixed.notes].filter(Boolean).join(' / '),
    }
  },
)

const done = results.filter(Boolean)
const failed = INSTRUCTIONS.filter(item => !done.find(r => r.behavior === item.behavior && r.final_check))
log(`完成 ${done.filter(r => r.final_check).length}/${INSTRUCTIONS.length}；未完成：${failed.map(i => i.name).join('、') || '无'}`)
// 待合并的 spec 追加项：格式就是 make_specs.py --merge=<文件> 要的列表，主代理原样存成 JSON 即可
const specAddList = done.filter(r => hasSpecAdd(r.spec_add)).map(r => ({ behavior: r.behavior, ...r.spec_add }))
if (specAddList.length) log(`${specAddList.length} 个指令提议追加 spec：${specAddList.map(a => a.behavior).join('、')}；用 make_specs.py --merge=<文件> 合并`)
return { results: done, failed: failed.map(i => i.behavior), spec_add: specAddList }
