# encoding: utf-8

"""
Workflow统一管理模块
提供数据库和截图的统一管理功能，包括删除、查询等操作
"""

import os
import sys
from typing import Optional, Dict, List

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))
from workflow_db import WorkflowDB


class WorkflowManager:
    """Workflow统一管理类"""
    
    def __init__(self):
        """初始化管理器"""
        self.db = WorkflowDB()
        self.picture_dir = os.path.join(os.path.dirname(__file__), "picture")
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        删除workflow（包括数据库记录和截图文件）
        
        Args:
            workflow_id: workflow的ID（如 control_12 或 control_12.png）
        
        Returns:
            是否成功删除
        """
        # 标准化ID格式（确保有.png后缀）
        if not workflow_id.endswith('.png'):
            workflow_id = f"{workflow_id}.png"
        
        # 1. 获取workflow信息（用于确定catalog）
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            print(f"✗ 数据库中未找到记录: {workflow_id}")
            return False
        
        catalog = workflow['catalog']
        
        # 2. 删除数据库记录
        if self.db.delete_workflow(workflow_id):
            print(f"✓ 已删除数据库记录: {workflow_id}")
        else:
            print(f"✗ 删除数据库记录失败: {workflow_id}")
            return False
        
        # 3. 删除截图文件
        screenshot_path = os.path.join(self.picture_dir, catalog, workflow_id)
        if os.path.exists(screenshot_path):
            try:
                os.remove(screenshot_path)
                print(f"✓ 已删除截图文件: {screenshot_path}")
            except Exception as e:
                print(f"⚠ 删除截图文件失败: {e}")
        else:
            print(f"⚠ 截图文件不存在: {screenshot_path}")
        
        return True
    
    def get_workflow_info(self, workflow_id: str) -> Optional[Dict]:
        """
        获取workflow信息（包括数据库记录和截图文件是否存在）
        
        Args:
            workflow_id: workflow的ID（如 control_12 或 control_12.png）
        
        Returns:
            workflow信息字典，如果不存在返回None
        """
        # 标准化ID格式
        if not workflow_id.endswith('.png'):
            workflow_id = f"{workflow_id}.png"
        
        workflow = self.db.get_workflow(workflow_id)
        if not workflow:
            return None
        
        # 检查截图文件是否存在
        catalog = workflow['catalog']
        screenshot_path = os.path.join(self.picture_dir, catalog, workflow_id)
        screenshot_exists = os.path.exists(screenshot_path)
        
        return {
            **workflow,
            'screenshot_path': screenshot_path,
            'screenshot_exists': screenshot_exists
        }
    
    def list_workflows_by_catalog(self, catalog: str) -> List[Dict]:
        """
        列出指定分类的所有workflow（包括截图文件状态）
        
        Args:
            catalog: 分类名称
        
        Returns:
            workflow信息列表
        """
        workflows = self.db.get_workflows_by_catalog(catalog)
        result = []
        
        for wf in workflows:
            workflow_id = wf['id']
            screenshot_path = os.path.join(self.picture_dir, catalog, workflow_id)
            screenshot_exists = os.path.exists(screenshot_path)
            
            result.append({
                **wf,
                'screenshot_path': screenshot_path,
                'screenshot_exists': screenshot_exists
            })
        
        return result
    
    def get_next_id(self, catalog: str) -> str:
        """
        获取下一个可用的ID（优先使用被删除的ID）
        
        Args:
            catalog: 分类名称
        
        Returns:
            下一个可用的ID，格式为{catalog}_{number}.png
        """
        # 1. 获取数据库中已存在的workflow
        existing_workflows = self.db.get_workflows_by_catalog(catalog)
        existing_ids = {wf['id'] for wf in existing_workflows}
        
        # 2. 获取文件系统中已存在的截图文件
        catalog_dir = os.path.join(self.picture_dir, catalog)
        file_ids = set()
        if os.path.exists(catalog_dir):
            for filename in os.listdir(catalog_dir):
                if filename.startswith(f"{catalog}_") and filename.endswith('.png'):
                    file_ids.add(filename)
        
        # 3. 找出所有已使用的ID（数据库或文件系统中存在的）
        used_ids = existing_ids | file_ids
        
        # 4. 提取所有已使用的数字
        used_numbers = set()
        for workflow_id in used_ids:
            try:
                # 从id中提取数字，如control_1.png -> 1
                num_str = workflow_id.replace(f"{catalog}_", "").replace(".png", "")
                num = int(num_str)
                used_numbers.add(num)
            except:
                continue
        
        # 5. 找到最小的可用数字（从1开始查找第一个未使用的）
        if not used_numbers:
            return f"{catalog}_1.png"
        
        max_num = max(used_numbers)
        # 查找1到max_num之间的第一个空缺
        for num in range(1, max_num + 1):
            if num not in used_numbers:
                return f"{catalog}_{num}.png"
        
        # 如果没有空缺，返回max_num + 1
        return f"{catalog}_{max_num + 1}.png"
    
    def check_consistency(self, catalog: str = None) -> Dict:
        """
        检查数据库和文件系统的一致性
        
        Args:
            catalog: 分类名称，如果为None则检查所有分类
        
        Returns:
            一致性检查结果
        """
        if catalog:
            catalogs = [catalog]
        else:
            # 获取所有分类
            all_workflows = self.db.get_all_workflows()
            catalogs = list(set(wf['catalog'] for wf in all_workflows))
        
        result = {
            'db_only': [],  # 只在数据库中存在
            'file_only': [],  # 只在文件系统中存在
            'consistent': []  # 两者都存在
        }
        
        for cat in catalogs:
            # 获取数据库中的workflow
            db_workflows = self.db.get_workflows_by_catalog(cat)
            db_ids = {wf['id'] for wf in db_workflows}
            
            # 获取文件系统中的文件
            catalog_dir = os.path.join(self.picture_dir, cat)
            file_ids = set()
            if os.path.exists(catalog_dir):
                for filename in os.listdir(catalog_dir):
                    if filename.startswith(f"{cat}_") and filename.endswith('.png'):
                        file_ids.add(filename)
            
            # 比较
            for db_id in db_ids:
                if db_id in file_ids:
                    result['consistent'].append(f"{cat}/{db_id}")
                else:
                    result['db_only'].append(f"{cat}/{db_id}")
            
            for file_id in file_ids:
                if file_id not in db_ids:
                    result['file_only'].append(f"{cat}/{file_id}")
        
        return result


if __name__ == "__main__":
    # 删除指定的workflow
    manager = WorkflowManager()
    
    print("=" * 80)
    print("删除workflow")
    print("=" * 80)
    
    # 删除 control_12
    print("\n正在删除 control_12...")
    manager.delete_workflow("control_12")
    
    # 删除 optimization_38
    print("\n正在删除 optimization_38...")
    manager.delete_workflow("optimization_38")
    
    print("\n" + "=" * 80)
    print("删除完成")
    print("=" * 80)

