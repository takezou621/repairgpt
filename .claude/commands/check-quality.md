# コード品質チェックコマンド

このコマンドは、code-quality-inspectorエージェントを使用して、実装したコードの品質を詳細にチェックし、改善提案を行います。

## 使用方法
```
/check-quality <file-or-directory-path>
```

## 動作内容
1. 指定されたファイルまたはディレクトリのコードを分析
2. RepairGPTのコーディング規約への準拠をチェック
3. 潜在的なバグやパフォーマンス問題を検出
4. ベストプラクティスとの乖離を特定
5. 具体的な改善提案を提供

## エージェント実行
```
Task(
    description="Inspect code quality",
    prompt=f"""
    code-quality-inspectorエージェントとして、以下のコードの品質をチェックしてください：
    
    対象: {user_input}
    
    以下の観点で詳細な分析を行ってください：
    
    1. **コーディング規約の遵守**
       - PEP 8準拠（120文字の行長制限）
       - 型ヒントの完全性
       - docstringの品質
       - 命名規則（snake_case、PascalCase等）
    
    2. **コード品質**
       - 複雑度の評価（循環的複雑度）
       - 重複コードの検出
       - デッドコードの特定
       - 過度に長い関数/クラスの検出
    
    3. **セキュリティ**
       - SQLインジェクション対策
       - 入力検証の適切性
       - 認証・認可の実装
       - シークレット情報の取り扱い
    
    4. **パフォーマンス**
       - N+1クエリ問題
       - 不要な計算やループ
       - キャッシュの活用機会
       - 非同期処理の適切性
    
    5. **エラーハンドリング**
       - 例外処理の網羅性
       - エラーメッセージの適切性
       - ログ出力の品質
    
    6. **テスタビリティ**
       - 単体テストの容易さ
       - モックの可能性
       - 依存性注入の活用
    
    7. **RepairGPT固有の要件**
       - 修理ガイドの安全性警告
       - 多言語対応（i18n）の実装
       - iFixit API統合のベストプラクティス
    
    出力形式：
    1. 総合評価（A〜Dグレード）
    2. カテゴリ別の詳細評価
    3. 発見された問題のリスト（優先度付き）
    4. 具体的な改善提案（コード例付き）
    5. 次のアクション推奨事項
    """,
    subagent_type="code-quality-inspector"
)
```

## 使用例
```
/check-quality src/services/image_analysis.py
/check-quality src/api/routes/
/check-quality src/ui/repair_app.py
```

## 期待される出力
```markdown
# コード品質検査レポート

## 総合評価: B+

## カテゴリ別評価
- **コーディング規約**: A（95/100）
- **コード品質**: B（82/100）
- **セキュリティ**: A-（90/100）
- **パフォーマンス**: B（80/100）
- **エラーハンドリング**: B+（85/100）
- **テスタビリティ**: A-（88/100）

## 発見された問題

### 🔴 高優先度
1. **未処理の例外** (src/services/image_analysis.py:45)
   ```python
   # 現在のコード
   response = openai_client.analyze(image)
   
   # 推奨
   try:
       response = openai_client.analyze(image)
   except OpenAIError as e:
       logger.error(f"Image analysis failed: {e}")
       raise ImageAnalysisError("画像分析に失敗しました") from e
   ```

### 🟡 中優先度
2. **型ヒントの欠落** (src/services/image_analysis.py:23)
   ```python
   # 現在のコード
   def process_image(image_data):
   
   # 推奨
   def process_image(image_data: bytes) -> Dict[str, Any]:
   ```

### 🟢 低優先度
3. **キャッシュの活用機会** (src/services/image_analysis.py:78)
   - 同じ画像の分析結果をRedisにキャッシュすることを推奨

## 改善提案

1. **エラーハンドリングの強化**
   - カスタム例外クラスの作成
   - 適切なログレベルの使用
   - ユーザーフレンドリーなエラーメッセージ

2. **パフォーマンス最適化**
   - 画像のリサイズ処理を非同期化
   - バッチ処理の実装検討

3. **テストカバレッジの向上**
   - エッジケースのテスト追加
   - モックを使用した外部API依存の削減

## 次のアクション
1. 高優先度の問題を即座に修正
2. 単体テストを追加して現在の85%から95%のカバレッジを目指す
3. パフォーマンステストを実施
```

## 補足情報
- 自動修正可能な問題は提案と共に修正コードを提供
- プロジェクト全体の品質トレンドも追跡
- CI/CDパイプラインへの統合を推奨