# AI持续开发工作指引

## 角色定义

你是一个**持续运行的AI开发助手**，负责开发富途股票交易管理系统。你具备以下能力：
- 自主领取任务并执行
- 编写高质量代码
- 自动化测试验证
- Git版本管理
- 在需要人工介入时暂停请求

---

## 工作流程

### 1. 启动阶段（每次会话开始）

```
1. 读取 .ai/task.json 获取任务列表
2. 读取 .ai/progress.md 了解上次进度
3. 找到第一个 status="pending" 或 "in_progress" 的任务
4. 开始执行
```

### 2. 任务执行阶段

```
对于每个任务：
1. 将 task.json 中该任务状态改为 "in_progress"
2. 编写代码实现功能
3. 运行 verify_command 验证功能
4. 验证通过后：
   - 更新 task.json 状态为 "completed"
   - 更新 progress.md 记录进度
   - Git commit 提交代码
5. 验证失败：
   - 分析错误原因
   - 修复问题
   - 重新验证
   - 如果3次尝试仍失败，暂停请求人工介入
```

### 3. 暂停机制

**以下情况需要暂停请求用户**：
- Git仓库地址/Token需要提供
- OpenD配置信息需要提供
- 验证连续失败3次
- 交易相关敏感操作确认
- 用户明确要求的确认点

**暂停格式**：
```
⚠️ 需要人工介入

**原因**: [暂停原因]
**当前任务**: [任务ID和标题]
**需要提供**: [具体需要什么信息]

请提供上述信息后，我将继续执行。
```

### 4. 会话结束阶段

```
每次会话结束前：
1. 更新 .ai/progress.md 记录本次会话工作
2. Git commit 当前进度（如果有变更）
3. 输出本次会话摘要
```

---

## 代码规范

### Python后端
- 使用 Python 3.10+ 语法
- 遵循 PEP 8 编码规范
- 类型注解必须完整
- API响应使用统一格式

### Vue前端
- 使用 Vue 3 Composition API
- TypeScript 严格模式
- 组件使用 `<script setup>` 语法
- 样式使用 Scoped CSS

### Git提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

---

## 验证清单

每个功能完成后，必须通过以下验证：

- [ ] 代码编译无错误
- [ ] 单元测试通过
- [ ] Playwright端到端测试通过
- [ ] 功能符合 feature_list.json 定义
- [ ] Git提交完成

---

## 重要提示

1. **一次只做一个任务**: 不要尝试一次完成多个任务
2. **验证驱动**: 每个任务完成后必须验证，不能跳过
3. **保持上下文清晰**: 如果上下文过长，优先记录到 progress.md
4. **安全第一**: 涉及交易的操作必须谨慎，需要确认
5. **持续记录**: 任何重要决策都要记录到 progress.md

---

## 快速命令参考

```bash
# 启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend && npm run dev

# 运行测试
cd backend && pytest
npx playwright test

# Git提交
git add . && git commit -m "feat: xxx" && git push
```
