# タスク実装＆PR作成コマンド

このコマンドは、task-executor-pr-creatorエージェントを使用して、kiro-task-organizerが作成したタスクを実装し、テストを書いてPRを作成します。

## 使用方法
```
/implement-task <task-id-or-description>
```

## 動作内容
1. 指定されたタスクの詳細を確認
2. 必要なファイルの変更を実装
3. 単体テストを作成・実行
4. コード品質チェック（Black、flake8、mypy）
5. PRを作成してGitHubにプッシュ

## エージェント実行
```
Task(
    description="Implement task and create PR",
    prompt=f"""
    task-executor-pr-creatorエージェントとして、以下のタスクを実装してください：
    
    タスク: {user_input}
    
    以下の手順で作業を進めてください：
    1. タスクの詳細を理解する（kiro-task-organizerの出力があれば参照）
    2. RepairGPTのコーディング規約に従って実装する：
       - PEP 8準拠
       - 型ヒント必須
       - docstring必須
       - 120文字の行長制限
    3. 実装に必要なファイルを作成・更新
    4. 単体テストを作成（pytest使用）
    5. テストを実行して全て合格することを確認
    6. コード品質チェックを実行：
       - black src/ tests/ --line-length=120
       - flake8 src/ tests/ --max-line-length=120
       - mypy src/
    7. 意味のあるコミットメッセージでコミット
    8. PRを作成（タイトルとdescriptionを含む）
    
    PR作成時の注意：
    - タイトルは "feat:", "fix:", "refactor:" などのプレフィックスを使用
    - descriptionには実装内容、テスト結果、関連するissue番号を含める
    - RepairGPTのPRテンプレートに従う
    
    実装時の注意：
    - 既存のコードスタイルに合わせる
    - エラーハンドリングを適切に実装
    - セキュリティを考慮（入力検証、認証など）
    """,
    subagent_type="task-executor-pr-creator"
)
```

## 使用例
```
/implement-task TASK-001
/implement-task Vision API統合基盤の実装
/implement-task image_analysis.pyにOpenAI Vision APIクライアントを追加
```

## 期待される出力
```markdown
# タスク実装完了レポート

## 実装内容
- ✅ src/services/image_analysis.py を作成
- ✅ Vision APIクライアントクラスを実装
- ✅ 画像分析メソッドを追加
- ✅ エラーハンドリングを実装

## テスト結果
- ✅ 5個の単体テストを作成
- ✅ 全テスト合格（5/5）
- ✅ カバレッジ: 95%

## 品質チェック
- ✅ Black: フォーマット完了
- ✅ flake8: エラーなし
- ✅ mypy: 型チェック合格

## PR情報
- **ブランチ**: feature/vision-api-integration
- **PRタイトル**: feat: Add Vision API integration for image analysis
- **PR番号**: #142
- **URL**: https://github.com/user/repairgpt/pull/142

## 次のステップ
レビュー待ち。マージ後はTASK-002の実装に進めます。
```

## 補足情報
- このコマンドは新規ブランチを作成して作業します
- 既存のテストが失敗する場合は修正も行います
- PRにはGitHub Actionsの結果も含まれます