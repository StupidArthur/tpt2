# encoding: utf-8

import os
import sqlite3
import json
import csv
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class WorkflowDB:
    """Workflow数据库管理类"""
    
    def __init__(self, db_path: str = None):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径，默认为tool目录下的workflow.db
        """
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "workflow.db")
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建workflow表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                workflow_json TEXT NOT NULL,
                catalog TEXT NOT NULL,
                items TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建索引以提高查询性能
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_catalog ON workflows(catalog)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_workflow_json ON workflows(workflow_json)')
        
        conn.commit()
        conn.close()
    
    def add_workflow(self, workflow_id: str, workflow_json: str, catalog: str, items: List[str]) -> bool:
        """
        添加或更新workflow记录
        
        Args:
            workflow_id: workflow的ID（文件名，如control_1.png）
            workflow_json: workflow的JSON字符串
            catalog: 分类（如control, statistics等）
            items: 语料列表
        
        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            items_json = json.dumps(items, ensure_ascii=False)
            
            cursor.execute('''
                INSERT OR REPLACE INTO workflows 
                (id, workflow_json, catalog, items, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (workflow_id, workflow_json, catalog, items_json, datetime.now()))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"添加workflow失败: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """
        根据ID获取workflow记录
        
        Args:
            workflow_id: workflow的ID
        
        Returns:
            workflow记录字典，如果不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workflows WHERE id = ?', (workflow_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'workflow_json': row['workflow_json'],
                'catalog': row['catalog'],
                'items': json.loads(row['items']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    
    def get_workflow_by_json(self, workflow_json: str) -> Optional[Dict]:
        """
        根据workflow JSON字符串获取记录
        
        Args:
            workflow_json: workflow的JSON字符串
        
        Returns:
            workflow记录字典，如果不存在返回None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workflows WHERE workflow_json = ?', (workflow_json,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row['id'],
                'workflow_json': row['workflow_json'],
                'catalog': row['catalog'],
                'items': json.loads(row['items']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        return None
    
    def get_workflows_by_catalog(self, catalog: str) -> List[Dict]:
        """
        根据分类获取所有workflow记录
        
        Args:
            catalog: 分类名称
        
        Returns:
            workflow记录列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workflows WHERE catalog = ? ORDER BY id', (catalog,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row['id'],
            'workflow_json': row['workflow_json'],
            'catalog': row['catalog'],
            'items': json.loads(row['items']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        } for row in rows]
    
    def get_all_workflows(self) -> List[Dict]:
        """
        获取所有workflow记录
        
        Returns:
            所有workflow记录列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM workflows ORDER BY catalog, id')
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row['id'],
            'workflow_json': row['workflow_json'],
            'catalog': row['catalog'],
            'items': json.loads(row['items']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        } for row in rows]
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        删除workflow记录
        
        Args:
            workflow_id: workflow的ID
        
        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM workflows WHERE id = ?', (workflow_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"删除workflow失败: {e}")
            return False
    
    def get_next_id(self, catalog: str) -> str:
        """
        获取下一个可用的ID（文件名）
        
        Args:
            catalog: 分类名称
        
        Returns:
            下一个ID，格式为{catalog}_{number}.png
        """
        workflows = self.get_workflows_by_catalog(catalog)
        if not workflows:
            return f"{catalog}_1.png"
        
        # 提取所有数字并找到最大值
        max_num = 0
        for wf in workflows:
            try:
                # 从id中提取数字，如control_1.png -> 1
                filename = wf['id']
                if filename.endswith('.png'):
                    num_str = filename.replace(f"{catalog}_", "").replace(".png", "")
                    num = int(num_str)
                    max_num = max(max_num, num)
            except:
                continue
        
        return f"{catalog}_{max_num + 1}.png"
    
    def export_to_csv(self, output_path: str = None) -> str:
        """
        导出所有数据到CSV文件
        
        Args:
            output_path: 输出文件路径，默认为tool目录下的workflows.csv
        
        Returns:
            输出文件路径
        """
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), "workflows.csv")
        
        workflows = self.get_all_workflows()
        
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Workflow JSON', 'Catalog', 'Items', 'Created At', 'Updated At'])
            
            for wf in workflows:
                items_str = '; '.join(wf['items'][:5])  # 只显示前5个items
                if len(wf['items']) > 5:
                    items_str += f" ... (共{len(wf['items'])}个)"
                writer.writerow([
                    wf['id'],
                    wf['workflow_json'],
                    wf['catalog'],
                    items_str,
                    wf['created_at'],
                    wf['updated_at']
                ])
        
        return output_path
    
    def export_to_txt(self, output_path: str = None) -> str:
        """
        导出所有数据到TXT文件（类似name_map.txt格式）
        
        Args:
            output_path: 输出文件路径，默认为tool目录下的workflows.txt
        
        Returns:
            输出文件路径
        """
        if output_path is None:
            output_path = os.path.join(os.path.dirname(__file__), "workflows.txt")
        
        workflows = self.get_all_workflows()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("文件名\t工作流标识\n")
            for wf in workflows:
                f.write(f"{wf['id']}\t{wf['workflow_json']}\n")
        
        return output_path
    
    def search_workflows(self, keyword: str = None, catalog: str = None) -> List[Dict]:
        """
        搜索workflow记录
        
        Args:
            keyword: 关键词，在workflow_json或items中搜索
            catalog: 分类筛选
        
        Returns:
            匹配的workflow记录列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if catalog and keyword:
            cursor.execute('''
                SELECT * FROM workflows 
                WHERE catalog = ? AND (workflow_json LIKE ? OR items LIKE ?)
                ORDER BY catalog, id
            ''', (catalog, f'%{keyword}%', f'%{keyword}%'))
        elif catalog:
            cursor.execute('SELECT * FROM workflows WHERE catalog = ? ORDER BY id', (catalog,))
        elif keyword:
            cursor.execute('''
                SELECT * FROM workflows 
                WHERE workflow_json LIKE ? OR items LIKE ?
                ORDER BY catalog, id
            ''', (f'%{keyword}%', f'%{keyword}%'))
        else:
            cursor.execute('SELECT * FROM workflows ORDER BY catalog, id')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row['id'],
            'workflow_json': row['workflow_json'],
            'catalog': row['catalog'],
            'items': json.loads(row['items']),
            'created_at': row['created_at'],
            'updated_at': row['updated_at']
        } for row in rows]
    
    def migrate_from_name_map(self, name_map_path: str = None, collected_results_path: str = None) -> int:
        """
        从name_map.txt迁移数据到数据库
        
        Args:
            name_map_path: name_map.txt文件路径
            collected_results_path: collected_results.json文件路径
        
        Returns:
            成功迁移的记录数
        """
        if name_map_path is None:
            name_map_path = os.path.join(os.path.dirname(__file__), "picture", "name_map.txt")
        if collected_results_path is None:
            collected_results_path = os.path.join(os.path.dirname(__file__), "collected_results.json")
        
        # 读取collected_results.json
        with open(collected_results_path, 'r', encoding='utf-8') as f:
            collected_data = json.load(f)
        
        # 读取name_map.txt
        migrated_count = 0
        with open(name_map_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 跳过表头
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t', 1)
                if len(parts) != 2:
                    continue
                
                filename = parts[0].strip()
                workflow_json = parts[1].strip()
                
                # 从collected_results.json中获取catalog和items
                if workflow_json in collected_data:
                    catalog = collected_data[workflow_json].get('catalog', 'unknown')
                    items = collected_data[workflow_json].get('items', [])
                    
                    if self.add_workflow(filename, workflow_json, catalog, items):
                        migrated_count += 1
        
        return migrated_count


if __name__ == "__main__":
    # 测试代码
    db = WorkflowDB()
    
    # 迁移数据
    print("开始从name_map.txt迁移数据...")
    count = db.migrate_from_name_map()
    print(f"成功迁移 {count} 条记录")
    
    # 导出为CSV和TXT
    csv_path = db.export_to_csv()
    txt_path = db.export_to_txt()
    print(f"已导出CSV到: {csv_path}")
    print(f"已导出TXT到: {txt_path}")
    
    # 测试查询
    print("\n测试查询功能:")
    print(f"总记录数: {len(db.get_all_workflows())}")
    print(f"control分类记录数: {len(db.get_workflows_by_catalog('control'))}")
    print(f"statistics分类记录数: {len(db.get_workflows_by_catalog('statistics'))}")

