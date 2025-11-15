# encoding: utf-8

import typing as tp

data1 = [[[0], {'type': 'text', 'text': ''}, [0, 'text'], '\n\n'], [[1], {'id': '019a8175-261d-7731-8118-b1923d70dd88', 'type': 'view', 'view': {'format': 'card', 'content': {'title': '😄已接收到您的问题~', 'type': 'title'}}}], [[2], {'id': '019a8175-261f-7132-9c19-f36d6e22bd2b', 'type': 'text', 'text': '</think>\n\n\n\n'}, [2, 'text'], '您希望通过多煤种的OTS（操作培训仿真）模拟，对乙烯装置中的压力控制回路PIC14063进行PID参数整定，使其能够更好地适应DCS系统在实际运行中的动态调整需求，提升控制系统的响应速度和稳定性。\n\n我将执行以下任务帮您解决。\n\n'], [[3], {'id': '019a8175-28fe-7a41-891e-145e492b0b6e', 'type': 'view', 'view': {'format': 'card', 'content': {'title': '思考结果', 'type': 'think', 'description': '针对您的问题已找到解决方案', 'details': '\n\n'}}}, [3, 'view', 'content', 'details'], '用户希望对 PIC14063 的 PID 参数进行整定，以提高装置在不同工况下的适应性和控制精度，确保装置运行更加高效和稳定。鉴于装置工况复杂多变，可能需要采用 AI 智能控制技术来实现这一目标。\n\n首先，我会通过用户交互界面，提示您确认主副回路的信息。\n\n随后，进入数据质量分析阶段，系统将评估数据集的质量，包括数据量、数据范围和数据波动性等，确保数据集满足建模要求。如果数据质量不达标，系统将在数据导入时标注异常数据，并提供数据预处理建议，帮助您提升数据质量。\n\n接下来，系统将进行 AI 可控性评估，针对数据集中除需控制的主变量外的其他变量，分析变量的变化趋势和控制范围，以确定系统是否适合采用 AI 模控技术进行整定。如果系统具有良好的 AI 可控性，表明环境变化对系统的影响较小，变量变化具有一定的规律性，适合使用 AI 模控技术进行整定；反之，则需谨慎考虑。\n\n之后，系统将进行关键影响因素分析，从所有筛选出的变量中分析出对主变量影响最大的变量，为后续建模提供依据。\n\n然后，系统将进行工况识别与验证，利用历史数据构建初始模型，并基于此模型对数据进行工况分类。同时，系统会对每种工况的特征进行图形展示，帮助您更好地理解数据模式。随后，系统将利用新数据对这些模型进行验证，评估模型的分类准确度，确保模型的可靠性和准确性。\n\n紧接着，系统将基于这些模型进行预测仿真，形成预测模型并进行验证，以确保模型的预测效果满足控制要求。在此过程中，系统会评估模型的预测准确性、稳定性及控制的合理性，为后续的控制优化提供坚实保障。\n\n随后，系统将搭建控制器并进行验证，结合您提供的工艺知识和控制需求，系统将自动设计控制器的结构，并利用预测模型进行控制计算。这一步骤将显著提升控制的效率和准确性，确保控制器设计的合理性。\n\n最后，系统将进入 AI 自整定阶段，根据之前确定的控制策略，系统将自动调整 PID 参数，以实现装置的高效、稳定运行。在整个整定过程中，系统会实时监控工况变化，自动适应不同工况，确保在各种条件下都能达到最佳控制效果。\n\n'], [[4], {'id': '019a8175-4516-7b82-aee8-1ac88381700d', 'type': 'json', 'json': '\n\n'}, [4, 'json'], '[{"id": "id1", "tool": "SPC", "ability": "AI控制补充信息", "dep": null},\n\n{"id": "id2", "tool": "SPC", "ability": "用户交互界面", "dep": ["id1"]},\n\n{"id": "id3", "tool": "SPC", "ability": "数据质量分析", "dep": ["id2"]},\n\n{"id": "id4", "tool": "SPC", "ability": "AI可控性评估", "dep": ["id3"]},\n\n{"id": "id5", "tool": "SPC", "ability": "关键影响因素分析", "dep": ["id4"]},\n\n{"id": "id6", "tool": "SPC", "ability": "工况识别与验证", "dep": ["id5"]},\n\n{"id": "id7", "tool": "SPC", "ability": "预测模型构建与验证", "dep": ["id6"]},\n\n{"id": "id8", "tool": "SPC", "ability": "控制器搭建及验证", "dep": ["id7"]},\n\n{"id": "id9", "tool": "SPC", "ability": "AI自整定", "dep": ["id8"]},\n\n{"id": "id10", "tool": "general_tool", "ability": "end", "dep": ["id9"]}]\n\n'], [[5], {'id': '019a8175-587e-7263-b382-a82f54b8ac2c', 'type': 'view', 'view': {'format': 'card', 'content': {'title': '置信度', 'type': 'confidence', 'description': '低'}}}], [[6], {'id': '019a8175-5881-7152-8f98-6e4ac6486ac1', 'type': 'view', 'view': {'format': 'card', 'content': {'title': '思考结果', 'type': 'verify_think', 'description': '验证结果', 'details': '能力:--用户交互界面-- 不存在于 --AI控制补充信息-- 的可能能力节点下'}}}], [[7], {'id': '019a8175-5883-7b20-be17-f44ab2bfeef7', 'type': 'text', 'text': '由于当前的工作流验证未通过，我将检索我的记忆库\n\n'}, [7, 'text'], '记忆库检索完毕！我将结合记忆和您的问题重新生成工作流'], [[8], {'id': '019a8175-b675-7500-a63a-cd1b0d3e991e', 'type': 'view', 'view': {'format': 'card', 'content': {'title': '思考结果', 'type': 'think', 'description': '针对您的问题已找到解决方案', 'details': '\n'}}}], [[9], {'id': '019a8175-b677-7062-b037-dbee3aad0b3b', 'type': 'json', 'json': '\n[{"id": "id1", "tool": "PID", "ability": "\\u56de\\u8def\\u4fe1\\u606f\\u67e5\\u8be2", "dep": null}, {"id": "id2", "tool": "PID", "ability": "\\u56de\\u8def\\u8fd0\\u884c\\u5b9e\\u65f6\\u72b6\\u6001\\u8ba1\\u7b97", "dep": ["id1"]}, {"id": "id3", "tool": "PID", "ability": "\\u591a\\u7b56\\u7565\\u81ea\\u9002\\u5e94\\u6574\\u5b9a", "dep": ["id2"]}, {"id": "id4", "tool": "general_tool", "ability": "end", "dep": ["id3"]}]\n'}], [[10], {'id': '019a8175-b67a-7d73-903e-dd3d93b3c2c7', 'type': 'view', 'view': {'format': 'card', 'content': {'title': '验证结果', 'type': 'verify', 'content': '{"title": "已完成工作流输出，请在右侧进行查看，并完成手动确认", "subtitle": "", "status": true}'}}}], [[11], {'id': '019a8175-b67c-7383-abee-df7bf5460fc1', 'type': 'branch', 'branch': 'null'}], [[12], {'id': '019a8175-b67e-7703-b4f8-18cc4818ffe5', 'type': 'require_confirm', 'require_confirm': 'true'}], [[13], {'type': 'workflow', 'workflow': '019a8175-b670-7701-9c06-2ee1c028b7ef', 'catalog': 'statistics', 'json': '[{"id":"id1","tool":"PID","ability":"回路信息查询","dep":null},{"id":"id2","tool":"PID","ability":"回路运行实时状态计算","dep":["id1"]},{"id":"id3","tool":"PID","ability":"多策略自适应整定","dep":["id2"]}]', 'branch': '[]', 'name': '基于 OTS 多煤种模拟，整定乙烯装置 PIC14063 的 PID 参数，适配 DCS 动态调整', 'metadata': None}], [[14], {'type': 'execute_confirm', 'execute_confirm': {'workflow_id': '019a8175-b670-7701-9c06-2ee1c028b7ef'}}]]

# for line in data1:
#     print(line)



def format_workflow_diagram(workflow_str: str, branch_rules_str: str = "") -> str:
    """将 workflow 和 branch_rules 转换为文本流程图"""
    import json
    
    try:
        workflow = json.loads(str(workflow_str)) if workflow_str else []
        branch_rules = json.loads(str(branch_rules_str)) if branch_rules_str else []
    except:
        return ""
    
    if not workflow:
        return ""
    
    # 构建节点映射
    nodes = {node['id']: node for node in workflow}
    
    # 构建依赖关系图（正向：从当前节点到后续节点）
    next_map = {}
    for node in workflow:
        node_id = node['id']
        deps = node.get('dep') or []
        if isinstance(deps, str):
            deps = [deps]
        # 找到所有依赖当前节点的节点（即当前节点的后续节点）
        next_nodes = []
        for other_node in workflow:
            other_deps = other_node.get('dep') or []
            if isinstance(other_deps, str):
                other_deps = [other_deps]
            if node_id in other_deps:
                next_nodes.append(other_node['id'])
        next_map[node_id] = next_nodes
    
    # 构建分支规则映射
    branch_map = {}
    for rule in branch_rules:
        from_id = rule.get('from')
        to_id = rule.get('to')
        expr = rule.get('expression', '')
        # 简化表达式显示
        if 'Eq true' in expr:
            expr = expr.replace('Variable([String("', '').replace('")]) Eq true', ' = true')
        elif 'Eq false' in expr:
            expr = expr.replace('Variable([String("', '').replace('")]) Eq false', ' = false')
        else:
            expr = expr.replace('Variable([String("', '').replace('")])', '')
        
        if from_id not in branch_map:
            branch_map[from_id] = []
        branch_map[from_id].append({'to': to_id, 'expr': expr})
    
    # 找到起始节点（没有依赖的节点）
    start_nodes = [node_id for node_id in nodes.keys() if not nodes[node_id].get('dep')]
    
    lines = []
    
    def format_node(node_id):
        """格式化节点显示"""
        node = nodes.get(node_id, {})
        ability = node.get('ability', node_id)
        return ability
    
    def get_node_width(node_id):
        """获取节点显示宽度"""
        return len(format_node(node_id)) + 2
    
    def draw_flow(start_id, visited=None, indent=0):
        """绘制流程图"""
        if visited is None:
            visited = set()
        
        if start_id in visited:
            return []
        
        visited.add(start_id)
        result_lines = []
        prefix = "  " * indent
        
        # 绘制当前节点
        node_text = format_node(start_id)
        result_lines.append(f"{prefix}% {node_text} %")
        
        # 获取后续节点
        next_nodes = next_map.get(start_id, [])
        
        # 检查是否有分支规则
        if start_id in branch_map:
            branches = branch_map[start_id]
            branch_targets = {b['to'] for b in branches}
            # 合并分支目标和普通后续节点
            all_next = list(set(next_nodes + list(branch_targets)))
            
            if all_next:
                result_lines.append(f"{prefix}    │")
                # 绘制分支
                for i, branch in enumerate(branches):
                    branch_id = branch['to']
                    expr = branch.get('expr', '')
                    is_last_branch = (i == len(branches) - 1) and all(nid in branch_targets for nid in next_nodes if nid not in branch_targets)
                    
                    if expr:
                        connector = "└─→" if is_last_branch and i == len(branches) - 1 else "├─→"
                        result_lines.append(f"{prefix}    {connector} [{expr}]")
                    else:
                        connector = "└─→" if is_last_branch and i == len(branches) - 1 else "├─→"
                        result_lines.append(f"{prefix}    {connector}")
                    
                    # 递归绘制分支路径
                    sub_lines = draw_flow(branch_id, visited.copy(), indent + 3)
                    result_lines.extend(sub_lines)
                    
                    if i < len(branches) - 1 or any(nid not in branch_targets for nid in next_nodes):
                        result_lines.append(f"{prefix}    │")
                
                # 绘制非分支的后续节点（通过 dep 关系，但不在分支规则中）
                non_branch_next = [nid for nid in next_nodes if nid not in branch_targets]
                for i, next_id in enumerate(non_branch_next):
                    is_last = i == len(non_branch_next) - 1
                    result_lines.append(f"{prefix}    {'└─→' if is_last else '├─→'}")
                    sub_lines = draw_flow(next_id, visited.copy(), indent + 3)
                    result_lines.extend(sub_lines)
                    if not is_last:
                        result_lines.append(f"{prefix}    │")
        else:
            # 没有分支，直接连接后续节点
            if next_nodes:
                result_lines.append(f"{prefix}    │")
                for i, next_id in enumerate(next_nodes):
                    is_last = i == len(next_nodes) - 1
                    result_lines.append(f"{prefix}    {'└─→' if is_last else '├─→'}")
                    sub_lines = draw_flow(next_id, visited.copy(), indent + 3)
                    result_lines.extend(sub_lines)
                    if not is_last:
                        result_lines.append(f"{prefix}    │")
        
        return result_lines
    
    # 从起始节点开始绘制
    for start_id in start_nodes:
        lines.extend(draw_flow(start_id))
        if len(start_nodes) > 1:
            lines.append("")
    
    return "\n".join(lines)


class ConversationInfo:

    def __init__(self):
        self.catalog = ""
        self.workflow = ""
        self.branch_rules = ""
        self.confidence = ""
        self.verify_think_details = ""
        self.first_workflow = ""
        self.thinking_info = ""

    def __str__(self):
        """美化打印输出"""
        import json
        lines = ["=" * 60, "ConversationInfo", "=" * 60]
        if self.catalog:
            lines.append(f"📁 Catalog: {str(self.catalog)}")
        if self.confidence:
            lines.append(f"🎯 Confidence: {str(self.confidence)}")
        if self.workflow:
            lines.append("\n📋 Workflow:")
            diagram = format_workflow_diagram(self.workflow, self.branch_rules)
            if diagram:
                lines.append(diagram)
            else:
                try:
                    lines.append(str(json.dumps(json.loads(str(self.workflow)), ensure_ascii=False, indent=2)))
                except:
                    lines.append(str(self.workflow))
        if self.verify_think_details:
            lines.append("\n🔍 Verify Think Details:")
            lines.append(str(self.verify_think_details))
        if self.first_workflow:
            lines.append("\n📝 First Workflow:")
            lines.append(str(self.first_workflow))
        if self.thinking_info:
            lines.append("\n💭 Thinking Info:")
            lines.append(str(self.thinking_info))
        lines.append("=" * 60)
        return "\n".join(lines)


def conversation_analyze(data: tp.List[tp.List]) -> ConversationInfo:
    """

    Args:
        data:

    Returns:

    """

    out = ConversationInfo()

    for index, line in enumerate(data):
        # 获得结果 workflow
        msg = line[1]



        if msg.get('type') == "workflow":
            out.catalog = msg.get('catalog')
            out.workflow = msg.get('json')
            out.branch_rules = msg.get('branch')
        elif msg.get('type') == "view":
            if isinstance(msg.get('view').get('content'), dict) and msg.get('view').get('content').get('type') == "confidence":
                out.confidence = msg.get('view').get('content').get('description')
                out.first_workflow = data[index - 1][-1]
            elif isinstance(msg.get('view').get('content'), dict) and msg.get('view').get('content').get('type') == "verify_think":
                out.verify_think_details = msg.get('view').get('content').get('details')

    return out


if __name__ == "__main__":
    print(conversation_analyze(data1))
