# Workflow异步检查和截图模块使用说明

本系统将workflow更新流程分为两个独立的模块，以提高效率：

1. **workflow_async_check.py** - 异步并发检查workflow匹配
2. **workflow_screenshot.py** - 根据匹配结果进行UI截图

## 模块一：异步检查模块 (workflow_async_check.py)

### 功能说明

- 读取 `not_found.txt` 中的未找到的workflow
- 异步并发发起所有API请求（支持高并发）
- 判断返回的workflow是否与预期匹配
- 如果匹配，记录title和workflow到txt文件

### 优势

- **高效并发**：支持多个API请求同时进行，大幅提升速度
- **自动重试**：每个item自动重试指定次数（默认3次）
- **会话保留**：调用过的会话会保留在系统中，后续可以用于截图

### 使用方法

```bash
# 基本用法（使用默认参数）
python workflow_async_check.py

# 指定并发数量
python workflow_async_check.py --concurrent 20

# 指定平台类型（arm或x86）
python workflow_async_check.py --platform arm
python workflow_async_check.py --platform x86

# 组合使用
python workflow_async_check.py --concurrent 20 --platform arm
```

### 参数说明

- `--concurrent`: 最大并发数量（默认10）
- `--platform`: 平台类型，可选 'arm' 或 'x86'（默认'arm'）

### 输出文件

- `matched_workflows_{timestamp}.txt`: 匹配成功的记录
  - 格式：`title\tworkflow_json\tcatalog`
- `not_found_{timestamp}.txt`: 仍未找到的workflow（如果存在）

### 示例输出

```
matched_workflows_20240101_120000.txt:
title	workflow_json	catalog
1_fb19_10回路即将启用，请求输出PID初始参数配置方案	{"workflow": "...", "branch_rules": "[]"}	statistics
...
```

## 模块二：截图模块 (workflow_screenshot.py)

### 功能说明

- 读取匹配结果文件（`matched_workflows_{timestamp}.txt`）
- 打开浏览器，根据title查找对应的会话
- 点击会话，切换到工作流标签
- 截图并保存到对应目录
- 更新SQLite数据库

### 使用方法

```bash
# 使用最新的匹配结果文件（自动查找）
python workflow_screenshot.py

# 指定匹配结果文件
python workflow_screenshot.py --file matched_workflows_20240101_120000.txt
```

### 参数说明

- `--file`: 匹配结果文件路径（默认使用最新的文件）

### 工作流程

1. 打开浏览器并登录
2. 等待用户确认登录状态和设置
3. 遍历匹配结果文件中的每条记录
4. 根据title在会话列表中查找对应的会话
5. 点击会话，切换到工作流标签
6. 截图并保存
7. 更新数据库

## 完整工作流程

### 步骤1：异步检查（快速）

```bash
# 高并发检查所有workflow（推荐并发数10-20）
python workflow_async_check.py --concurrent 20 --platform arm
```

这一步会：
- 快速并发发起所有API请求
- 判断workflow是否匹配
- 生成匹配结果文件

**预计时间**：根据workflow数量和并发数，通常几分钟到十几分钟

### 步骤2：截图（串行）

```bash
# 根据匹配结果进行截图
python workflow_screenshot.py
```

这一步会：
- 打开浏览器
- 根据title找到对应的会话（会话已保留在系统中）
- 截图并更新数据库

**预计时间**：每个workflow约10-30秒

## 配置参数

### workflow_async_check.py

在文件顶部可以修改：

```python
MAX_CONCURRENT = 10  # 最大并发数量
RETRY_TIMES = 3      # 每个item重复执行次数
```

### workflow_screenshot.py

在文件顶部可以修改：

```python
driver_path = "f:\\chrome144\\chromedriver.exe"  # 浏览器驱动路径
```

## 注意事项

1. **会话保留**：系统会保留所有调用过的会话，所以可以先运行异步检查，再运行截图
2. **并发控制**：建议并发数不要太高（10-20），避免对服务器造成压力
3. **平台选择**：根据实际使用的平台选择arm或x86
4. **文件路径**：确保 `collected_results.json` 和 `not_found.txt` 文件存在
5. **浏览器设置**：截图前需要手动确认浏览器登录状态和设置

## 性能对比

### 原方式（串行）
- API请求 → UI操作 → 截图（每个workflow串行）
- 预计时间：每个workflow约1-2分钟
- 100个workflow：约100-200分钟

### 新方式（异步+串行）
- 步骤1：异步检查（并发20）：约10-20分钟
- 步骤2：截图（串行）：约10-30分钟
- 总计：约20-50分钟

**效率提升：约4-10倍**

## 故障排查

### 问题1：找不到匹配结果文件

**解决**：确保先运行 `workflow_async_check.py` 生成匹配结果文件

### 问题2：找不到会话

**解决**：
- 确保浏览器已登录
- 检查title是否完全匹配
- 可能需要刷新浏览器页面

### 问题3：并发错误

**解决**：降低并发数量（`--concurrent` 参数）

### 问题4：登录失败

**解决**：检查平台配置和网络连接

