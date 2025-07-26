# フル開発ワークフローコマンド

このコマンドは、全てのエージェントを連携させて、機能の計画から実装、品質保証、PR作成まで一連の開発ワークフローを自動実行します。

## 使用方法
```
/full-workflow <feature-description>
```

## 動作内容
1. **タスク整理** (kiro-task-organizer)
2. **実装とテスト** (task-executor-pr-creator)
3. **品質チェック** (code-quality-inspector)
4. **QAテスト** (qa-engineer-tester)
5. **最終レビューとPR作成**

## エージェント実行フロー
```
# ステップ1: タスク整理
Task(
    description="Organize tasks for feature",
    prompt=f"""
    kiro-task-organizerエージェントとして、以下の機能を実装可能なタスクに分割してください：
    
    機能: {user_input}
    
    .kiro/steering/ディレクトリのドキュメントを参照し、RepairGPTプロジェクトに適したタスク分割を行ってください。
    各タスクは1つのコミットで完了できるサイズにしてください。
    """,
    subagent_type="kiro-task-organizer"
)

# ステップ2: 各タスクの実装
for task in tasks:
    Task(
        description=f"Implement {task.id}",
        prompt=f"""
        task-executor-pr-creatorエージェントとして、以下のタスクを実装してください：
        
        {task.details}
        
        RepairGPTのコーディング規約に従い、テストを含めて実装してください。
        各タスクは個別のブランチで実装し、コミットしてください。
        """,
        subagent_type="task-executor-pr-creator"
    )
    
    # ステップ3: 品質チェック
    Task(
        description=f"Check quality of {task.id}",
        prompt=f"""
        code-quality-inspectorエージェントとして、実装されたコードの品質をチェックしてください。
        
        対象: {task.implemented_files}
        
        問題が発見された場合は、修正提案を含めて報告してください。
        """,
        subagent_type="code-quality-inspector"
    )

# ステップ4: 統合QAテスト
Task(
    description="Run comprehensive QA tests",
    prompt=f"""
    qa-engineer-testerエージェントとして、実装された機能全体の包括的なテストを実行してください：
    
    機能: {user_input}
    実装されたタスク: {implemented_tasks}
    
    統合テスト、パフォーマンステスト、セキュリティテストを含めて実行し、
    発見された問題には修正提案を含めてください。
    """,
    subagent_type="qa-engineer-tester"
)

# ステップ5: 最終PR作成
Task(
    description="Create final PR",
    prompt=f"""
    task-executor-pr-creatorエージェントとして、全ての実装を統合した最終的なPRを作成してください：
    
    機能: {user_input}
    実装ブランチ: {feature_branches}
    
    以下を含むPRを作成：
    - 機能の概要
    - 実装された全タスクのリスト
    - テスト結果のサマリー
    - 品質チェック結果
    - デプロイメント手順（必要な場合）
    """,
    subagent_type="task-executor-pr-creator"
)
```

## 使用例
```
/full-workflow AI診断機能の精度向上（GPT-4からClaude-3への切り替えを含む）
/full-workflow 修理ガイドのPDF出力機能を追加
/full-workflow マルチテナント対応（企業向け機能）
```

## 期待される出力
```markdown
# フル開発ワークフロー実行結果

## 機能: AI診断機能の精度向上

### ステップ1: タスク分割完了
- TASK-001: Claude-3 APIクライアントの実装
- TASK-002: プロンプトテンプレートの最適化
- TASK-003: A/Bテスト機能の実装
- TASK-004: 移行スクリプトの作成

### ステップ2: 実装状況
- ✅ TASK-001: 実装完了（ブランチ: feature/claude-3-client）
- ✅ TASK-002: 実装完了（ブランチ: feature/optimize-prompts）
- ✅ TASK-003: 実装完了（ブランチ: feature/ab-testing）
- ✅ TASK-004: 実装完了（ブランチ: feature/migration-script）

### ステップ3: 品質チェック結果
- 総合評価: A-
- 修正実施: 3件の軽微な問題を自動修正

### ステップ4: QAテスト結果
- 実行テスト: 248件
- 成功: 245件
- 修正済み: 3件
- パフォーマンス: レスポンスタイム15%改善

### ステップ5: 最終PR
- **PR #156**: feat: Improve AI diagnosis accuracy with Claude-3
- **ステータス**: Ready for review
- **URL**: https://github.com/user/repairgpt/pull/156

## 次のアクション
1. PRのレビュー依頼
2. ステージング環境でのテスト
3. 本番デプロイメント計画の策定
```

## ワークフロー設定オプション
```yaml
# .claude/workflow-config.yml
full_workflow:
  parallel_tasks: true  # タスクを並列実行
  auto_fix_issues: true  # 軽微な問題を自動修正
  create_draft_pr: false  # ドラフトPRを作成
  run_integration_tests: true  # 統合テストを実行
  security_scan: true  # セキュリティスキャンを実行
```

## 注意事項
- 大規模な機能の場合、実行に時間がかかる場合があります
- 各ステップで問題が発生した場合は、手動介入が必要な場合があります
- PR作成前に、ローカルでの最終確認を推奨します