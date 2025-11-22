# Workflow管理系统使用说明

本系统实现了workflow的数据库管理和增量更新功能。

## 文件说明

### 1. `workflow_db.py` - 数据库管理模块

SQLite数据库管理类，提供以下功能：

- **数据库操作**：
  - `add_workflow()`: 添加或更新workflow记录
  - `get_workflow()`: 根据ID获取workflow
  - `get_workflow_by_json()`: 根据JSON字符串获取workflow
  - `get_workflows_by_catalog()`: 根据分类获取所有workflow
  - `get_all_workflows()`: 获取所有workflow
  - `delete_workflow()`: 删除workflow
  - `get_next_id()`: 获取下一个可用的ID（用于增量更新）

- **数据导出**：
  - `export_to_csv()`: 导出为CSV格式
  - `export_to_txt()`: 导出为TXT格式（类似name_map.txt）

- **数据搜索**：
  - `search_workflows()`: 根据关键词和分类搜索

- **数据迁移**：
  - `migrate_from_name_map()`: 从name_map.txt迁移数据到数据库

### 2. `workflow_update.py` - 增量更新脚本

处理`not_found.txt`中未找到的workflow，进行增量更新：

- 读取`not_found.txt`中的workflow JSON字符串
- 在`collected_results.json`中查找对应的items
- 对每个item重复执行指定次数（默认3次），直到找到匹配的workflow
- 如果找到匹配，则截图并更新数据库
- 文件名遵循增量规律（如`control_14.png`）
- 如果仍未找到，生成`not_found_{timestamp}.txt`文件

**配置参数**：
- `RETRY_TIMES`: 每个item重复执行次数（默认3）

### 3. `migrate_to_db.py` - 数据迁移脚本

将`name_map.txt`中的数据迁移到SQLite数据库。

## 使用步骤

### 步骤1：迁移现有数据

首次使用时，需要将`name_map.txt`中的数据迁移到数据库：

```bash
cd tool
python migrate_to_db.py
```

这将：
- 创建SQLite数据库（`workflow.db`）
- 从`name_map.txt`读取数据
- 从`collected_results.json`获取catalog和items信息
- 将所有数据导入数据库
- 导出为CSV和TXT格式

### 步骤2：使用数据库管理

```python
from workflow_db import WorkflowDB

# 创建数据库实例
db = WorkflowDB()

# 添加workflow
db.add_workflow(
    workflow_id="control_14.png",
    workflow_json='{"workflow": "...", "branch_rules": "[]"}',
    catalog="control",
    items=["语料1", "语料2"]
)

# 查询workflow
workflow = db.get_workflow("control_1.png")
print(workflow)

# 根据分类查询
control_workflows = db.get_workflows_by_catalog("control")

# 搜索workflow
results = db.search_workflows(keyword="PID", catalog="statistics")

# 导出数据
db.export_to_csv("workflows.csv")
db.export_to_txt("workflows.txt")
```

### 步骤3：增量更新workflow

运行增量更新脚本处理`not_found.txt`中的workflow：

```bash
cd tool
python workflow_update.py
```

脚本将：
1. 打开浏览器并登录
2. 读取`not_found.txt`
3. 对每个workflow尝试所有items（每个item重复3次）
4. 找到匹配后截图并更新数据库
5. 生成新的`not_found_{timestamp}.txt`（如果仍有未找到的）

**注意**：运行前需要：
- 确保浏览器驱动路径正确（`driver_path`）
- 确保API配置正确
- 手动确认浏览器登录状态

## 数据库结构

### workflows表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT | workflow的ID（文件名，如control_1.png） |
| workflow_json | TEXT | workflow的JSON字符串 |
| catalog | TEXT | 分类（control, statistics等） |
| items | TEXT | 语料列表（JSON数组） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 文件位置

- 数据库文件：`tool/workflow.db`
- 截图目录：`tool/picture/{catalog}/`
- 配置文件：`tool/collected_results.json`
- 未找到列表：`tool/picture/not_found.txt`

## 注意事项

1. **数据库文件**：SQLite数据库文件（`workflow.db`）会保存在`tool`目录下
2. **增量ID**：新增workflow时，ID会自动递增（如`control_14.png`）
3. **数据备份**：建议定期导出CSV或TXT文件作为备份
4. **性能**：数据库已创建索引，查询性能良好
5. **兼容性**：数据库可以完全替代`name_map.txt`的功能

## 示例：完整工作流程

```python
# 1. 迁移数据
python migrate_to_db.py

# 2. 使用数据库查询
from workflow_db import WorkflowDB
db = WorkflowDB()
workflows = db.get_workflows_by_catalog("control")

# 3. 增量更新
python workflow_update.py

# 4. 导出数据
db.export_to_csv()
db.export_to_txt()
```

