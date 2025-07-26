# タスク整理コマンド

このコマンドは、kiro-task-organizerエージェントを使用して、.kiroディレクトリのステアリングドキュメントを分析し、開発タスクを適切なサイズに分割します。

## 使用方法
```
/organize-tasks <feature-description>
```

## 動作内容
1. .kiro/steering/内のドキュメント（product.md、structure.md、tech.md）を分析
2. 指定された機能やタスクを適切なサイズの開発タスクに分割
3. 各タスクに対して以下を定義：
   - タスクの詳細内容
   - 実装対象のファイル
   - 依存関係
   - 推定作業時間
   - テスト要件

## エージェント実行
```
Task(
    description="Organize development tasks",
    prompt=f"""
    kiro-task-organizerエージェントとして、以下のタスクを分析してください：
    
    タスク: {user_input}
    
    以下の手順で作業を進めてください：
    1. .kiro/steering/ディレクトリ内のドキュメントを読み込む
    2. RepairGPTプロジェクトの構造と技術スタックを理解する
    3. 指定されたタスクを、1つのコミットで完了できる適切なサイズのタスクに分割する
    4. 各タスクについて以下を明確にする：
       - タスクID（例: TASK-001）
       - タスクタイトル
       - 詳細説明
       - 実装対象ファイル
       - 依存タスク
       - 推定作業時間
       - テスト要件
    5. タスクの実行順序を提案する
    
    出力形式：
    マークダウン形式で、実行可能なタスクリストを作成してください。
    """,
    subagent_type="kiro-task-organizer"
)
```

## 使用例
```
/organize-tasks 修理ガイドのマルチモーダル対応を実装したい
/organize-tasks iFixit API統合を強化してキャッシュ機能を追加
/organize-tasks ユーザー認証システムをJWTベースに移行
```

## 期待される出力
```markdown
# タスク分割結果

## TASK-001: Vision API統合基盤の実装
- **説明**: OpenAI Vision APIとの連携基盤を構築
- **対象ファイル**: 
  - src/services/image_analysis.py (新規)
  - src/config/settings.py (更新)
- **依存**: なし
- **推定時間**: 2時間
- **テスト**: Vision APIモックを使用した単体テスト

## TASK-002: 画像アップロード機能の実装
- **説明**: Streamlit UIで画像アップロード機能を追加
- **対象ファイル**: 
  - src/ui/components/image_uploader.py (新規)
  - src/ui/repair_app.py (更新)
- **依存**: TASK-001
- **推定時間**: 1.5時間
- **テスト**: UIコンポーネントテスト

## 実行順序
1. TASK-001 → TASK-002 → ...
```