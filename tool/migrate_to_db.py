# encoding: utf-8

"""
从name_map.txt迁移数据到SQLite数据库的脚本
"""

from workflow_db import WorkflowDB


def main():
    """主函数"""
    print("=" * 60)
    print("开始迁移数据从name_map.txt到SQLite数据库")
    print("=" * 60)
    
    # 创建数据库实例
    db = WorkflowDB()
    
    # 执行迁移
    count = db.migrate_from_name_map()
    
    print(f"\n迁移完成！")
    print(f"成功迁移 {count} 条记录")
    
    # 导出为CSV和TXT格式
    print("\n正在导出数据...")
    csv_path = db.export_to_csv()
    txt_path = db.export_to_txt()
    
    print(f"✓ CSV文件已导出到: {csv_path}")
    print(f"✓ TXT文件已导出到: {txt_path}")
    
    # 显示统计信息
    print("\n数据库统计信息:")
    print(f"  总记录数: {len(db.get_all_workflows())}")
    
    catalogs = ['control', 'statistics', 'optimization', 'evaluation', 'prediction', 'simulation']
    for catalog in catalogs:
        workflows = db.get_workflows_by_catalog(catalog)
        if workflows:
            print(f"  {catalog}: {len(workflows)} 条记录")
    
    print("\n迁移完成！")


if __name__ == "__main__":
    main()

