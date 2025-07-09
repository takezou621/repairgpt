# RepairGPT デプロイメント・運用ガイド

## 1. デプロイメント概要

### 1.1 デプロイメント戦略
- **開発環境**: ローカル開発（Docker Compose）
- **ステージング環境**: クラウド環境でのテスト
- **本番環境**: 高可用性・スケーラブルなクラウド環境

### 1.2 インフラ構成
```mermaid
graph TD
    A[Load Balancer] --> B[Web Server]
    B --> C[Application Server]
    C --> D[Database]
    C --> E[Redis Cache]
    C --> F[File Storage]
    
    G[CI/CD Pipeline] --> H[Container Registry]
    H --> I[Kubernetes Cluster]
    I --> C
```

## 2. 環境構成

### 2.1 開発環境（Local）

#### 2.1.1 Docker Compose設定
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/repairgpt
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./src:/app/src
      - ./uploads:/app/uploads
  
  streamlit:
    build: 
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://app:8000
    depends_on:
      - app
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=repairgpt
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### 2.1.2 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY . .

# アプリケーションの起動
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2.1.3 Streamlit用Dockerfile
```dockerfile
# Dockerfile.streamlit
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements-streamlit.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-streamlit.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

### 2.2 ステージング環境

#### 2.2.1 Kubernetes設定
```yaml
# k8s/staging/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: repairgpt-api
  namespace: staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: repairgpt-api
  template:
    metadata:
      labels:
        app: repairgpt-api
    spec:
      containers:
      - name: api
        image: repairgpt/api:staging
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: repairgpt-secrets
              key: database-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: repairgpt-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: repairgpt-api-service
  namespace: staging
spec:
  selector:
    app: repairgpt-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### 2.2.2 ConfigMap設定
```yaml
# k8s/staging/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: repairgpt-config
  namespace: staging
data:
  LOG_LEVEL: "INFO"
  DEBUG: "false"
  API_VERSION: "v1"
  CORS_ORIGINS: "http://localhost:3000,https://staging.repairgpt.com"
```

#### 2.2.3 Secret設定
```yaml
# k8s/staging/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: repairgpt-secrets
  namespace: staging
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  openai-api-key: <base64-encoded-api-key>
  claude-api-key: <base64-encoded-claude-key>
```

### 2.3 本番環境

#### 2.3.1 本番用Deployment
```yaml
# k8s/production/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: repairgpt-api
  namespace: production
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: repairgpt-api
  template:
    metadata:
      labels:
        app: repairgpt-api
    spec:
      containers:
      - name: api
        image: repairgpt/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: repairgpt-secrets
              key: database-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "1000m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 2.3.2 HPA設定
```yaml
# k8s/production/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: repairgpt-api-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: repairgpt-api
  minReplicas: 5
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 3. CI/CD パイプライン

### 3.1 GitHub Actions設定
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  
  # 手動実行用
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
  
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push API image
      uses: docker/build-push-action@v3
      with:
        context: .
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/api:latest
          ghcr.io/${{ github.repository }}/api:${{ github.sha }}
    
    - name: Build and push Streamlit image
      uses: docker/build-push-action@v3
      with:
        context: .
        file: Dockerfile.streamlit
        push: true
        tags: |
          ghcr.io/${{ github.repository }}/streamlit:latest
          ghcr.io/${{ github.repository }}/streamlit:${{ github.sha }}
  
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to staging
      run: |
        kubectl apply -f k8s/staging/
        kubectl rollout status deployment/repairgpt-api -n staging
  
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      run: |
        echo "${{ secrets.KUBE_CONFIG }}" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig
    
    - name: Deploy to production
      run: |
        kubectl apply -f k8s/production/
        kubectl rollout status deployment/repairgpt-api -n production
    
    - name: Verify deployment
      run: |
        kubectl get pods -n production
        kubectl get services -n production
```

### 3.2 デプロイメントスクリプト
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}

echo "Deploying to $ENVIRONMENT with image tag $IMAGE_TAG"

# 環境固有の設定
case $ENVIRONMENT in
  staging)
    NAMESPACE="staging"
    REPLICAS=2
    ;;
  production)
    NAMESPACE="production"
    REPLICAS=5
    ;;
  *)
    echo "Invalid environment: $ENVIRONMENT"
    exit 1
    ;;
esac

# Kubernetes設定の適用
kubectl apply -f k8s/common/
kubectl apply -f k8s/$ENVIRONMENT/

# デプロイメントの更新
kubectl set image deployment/repairgpt-api api=ghcr.io/repairgpt/api:$IMAGE_TAG -n $NAMESPACE
kubectl set image deployment/repairgpt-streamlit streamlit=ghcr.io/repairgpt/streamlit:$IMAGE_TAG -n $NAMESPACE

# デプロイメントの完了を待機
kubectl rollout status deployment/repairgpt-api -n $NAMESPACE --timeout=300s
kubectl rollout status deployment/repairgpt-streamlit -n $NAMESPACE --timeout=300s

echo "Deployment completed successfully"

# ヘルスチェック
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# 簡単なヘルスチェック
API_URL=$(kubectl get service repairgpt-api-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl -f http://$API_URL/health || echo "Health check failed"
```

## 4. 監視・ログ

### 4.1 Prometheus設定
```yaml
# k8s/monitoring/prometheus.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    
    scrape_configs:
    - job_name: 'repairgpt-api'
      static_configs:
      - targets: ['repairgpt-api-service:80']
      metrics_path: /metrics
      scrape_interval: 5s
    
    - job_name: 'postgres'
      static_configs:
      - targets: ['postgres-exporter:9187']
    
    - job_name: 'redis'
      static_configs:
      - targets: ['redis-exporter:9121']
```

### 4.2 Grafana ダッシュボード
```json
{
  "dashboard": {
    "title": "RepairGPT Metrics",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m])) by (method, endpoint)",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) by (endpoint)",
            "legendFormat": "{{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

### 4.3 ログ設定
```yaml
# k8s/logging/fluentd.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: kube-system
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/*repairgpt*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      read_from_head true
      format json
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch
      port 9200
      logstash_format true
      logstash_prefix repairgpt
    </match>
```

## 5. バックアップ・災害復旧

### 5.1 データベースバックアップ
```bash
#!/bin/bash
# scripts/backup_db.sh

set -e

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="repairgpt_backup_$TIMESTAMP.sql"

# データベースバックアップの実行
kubectl exec -n production deployment/postgres -- pg_dump -U postgres repairgpt > $BACKUP_DIR/$BACKUP_FILE

# バックアップファイルの圧縮
gzip $BACKUP_DIR/$BACKUP_FILE

# 古いバックアップの削除（30日以上前）
find $BACKUP_DIR -name "repairgpt_backup_*.sql.gz" -mtime +30 -delete

# S3にアップロード
aws s3 cp $BACKUP_DIR/$BACKUP_FILE.gz s3://repairgpt-backups/database/

echo "Database backup completed: $BACKUP_FILE.gz"
```

### 5.2 データベース復旧
```bash
#!/bin/bash
# scripts/restore_db.sh

set -e

BACKUP_FILE=${1:-latest}

if [ "$BACKUP_FILE" = "latest" ]; then
  BACKUP_FILE=$(ls -t /backups/repairgpt_backup_*.sql.gz | head -1)
fi

echo "Restoring database from: $BACKUP_FILE"

# バックアップファイルの展開
gunzip -c $BACKUP_FILE > /tmp/restore.sql

# データベースの復元
kubectl exec -n production deployment/postgres -- psql -U postgres -d repairgpt -f /tmp/restore.sql

# 一時ファイルの削除
rm /tmp/restore.sql

echo "Database restore completed"
```

### 5.3 災害復旧計画
```yaml
# DR計画の概要
Recovery Time Objective (RTO): 4時間
Recovery Point Objective (RPO): 1時間

手順:
1. 障害の確認と影響範囲の特定
2. 代替環境の準備
3. データベースの復旧
4. アプリケーションの起動
5. 動作確認
6. DNS切り替え
7. 利用者への通知
```

## 6. セキュリティ対策

### 6.1 Network Policy
```yaml
# k8s/security/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: repairgpt-network-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: repairgpt-api
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: database
    ports:
    - protocol: TCP
      port: 5432
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
```

### 6.2 Pod Security Policy
```yaml
# k8s/security/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: repairgpt-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

### 6.3 SSL/TLS設定
```yaml
# k8s/security/tls-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: repairgpt-tls
  namespace: production
type: kubernetes.io/tls
data:
  tls.crt: <base64-encoded-certificate>
  tls.key: <base64-encoded-private-key>
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: repairgpt-ingress
  namespace: production
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.repairgpt.com
    secretName: repairgpt-tls
  rules:
  - host: api.repairgpt.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: repairgpt-api-service
            port:
              number: 80
```

## 7. パフォーマンス最適化

### 7.1 Redis Cache設定
```yaml
# k8s/cache/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        volumeMounts:
        - name: redis-data
          mountPath: /data
      volumes:
      - name: redis-data
        persistentVolumeClaim:
          claimName: redis-pvc
```

### 7.2 データベース最適化
```sql
-- インデックスの作成
CREATE INDEX CONCURRENTLY idx_chat_messages_session_created 
ON chat_messages(session_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_repair_guides_device_issue 
ON repair_guides(device_id, issue_id, is_active);

-- 古いデータの削除（日次実行）
DELETE FROM chat_messages 
WHERE created_at < NOW() - INTERVAL '1 year';

-- 統計情報の更新
ANALYZE chat_messages;
ANALYZE repair_guides;
```

### 7.3 CDN設定
```yaml
# CloudFront設定例
Distribution:
  Origins:
  - DomainName: api.repairgpt.com
    Id: repairgpt-api
    CustomOriginConfig:
      HTTPPort: 80
      HTTPSPort: 443
      OriginProtocolPolicy: https-only
  
  DefaultCacheBehavior:
    TargetOriginId: repairgpt-api
    ViewerProtocolPolicy: redirect-to-https
    CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # Managed-CachingDisabled
    OriginRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf  # Managed-CORS-S3Origin
  
  CacheBehaviors:
  - PathPattern: "/static/*"
    TargetOriginId: repairgpt-api
    ViewerProtocolPolicy: redirect-to-https
    CachePolicyId: 658327ea-f89d-4fab-a63d-7e88639e58f6  # Managed-CachingOptimized
```

## 8. 運用手順

### 8.1 デプロイメント手順
```bash
# 1. 事前確認
./scripts/pre-deployment-check.sh

# 2. バックアップ作成
./scripts/backup_db.sh

# 3. デプロイメント実行
./scripts/deploy.sh production v1.2.3

# 4. 動作確認
./scripts/health_check.sh production

# 5. 問題がある場合はロールバック
./scripts/rollback.sh production
```

### 8.2 監視・アラート設定
```yaml
# Alertmanager設定
groups:
- name: repairgpt-alerts
  rules:
  - alert: HighErrorRate
    expr: sum(rate(http_requests_total{status=~"5.."}[5m])) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} requests/second"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le)) > 2
    for: 5m
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds"
  
  - alert: DatabaseConnectionFailure
    expr: up{job="postgres"} == 0
    for: 2m
    annotations:
      summary: "Database connection failure"
      description: "Unable to connect to database"
```

### 8.3 メンテナンス手順
```bash
#!/bin/bash
# scripts/maintenance.sh

set -e

ENVIRONMENT=${1:-production}
OPERATION=${2:-status}

case $OPERATION in
  start)
    echo "Starting maintenance mode for $ENVIRONMENT"
    kubectl apply -f k8s/maintenance/maintenance-page.yaml -n $ENVIRONMENT
    kubectl scale deployment repairgpt-api --replicas=0 -n $ENVIRONMENT
    ;;
  
  stop)
    echo "Stopping maintenance mode for $ENVIRONMENT"
    kubectl scale deployment repairgpt-api --replicas=5 -n $ENVIRONMENT
    kubectl delete -f k8s/maintenance/maintenance-page.yaml -n $ENVIRONMENT
    ;;
  
  status)
    echo "Checking maintenance status for $ENVIRONMENT"
    kubectl get pods -n $ENVIRONMENT
    kubectl get services -n $ENVIRONMENT
    ;;
  
  *)
    echo "Usage: $0 <environment> <start|stop|status>"
    exit 1
    ;;
esac
```

## 9. トラブルシューティング

### 9.1 よくある問題と解決方法

#### 9.1.1 Pod起動エラー
```bash
# ログの確認
kubectl logs -f deployment/repairgpt-api -n production

# 設定の確認
kubectl describe deployment repairgpt-api -n production

# リソース不足の確認
kubectl top nodes
kubectl top pods -n production
```

#### 9.1.2 データベース接続エラー
```bash
# データベースPodの確認
kubectl get pods -n production -l app=postgres

# データベースログの確認
kubectl logs -f deployment/postgres -n production

# 接続テスト
kubectl exec -it deployment/repairgpt-api -n production -- python -c "
import psycopg2
import os
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
print('Database connection successful')
"
```

#### 9.1.3 パフォーマンス問題
```bash
# メトリクスの確認
kubectl port-forward service/prometheus 9090:9090 -n monitoring

# APM ツールでのトレース確認
kubectl port-forward service/jaeger 16686:16686 -n monitoring

# データベースのスロークエリ確認
kubectl exec -it deployment/postgres -n production -- psql -U postgres -d repairgpt -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### 9.2 緊急時対応手順

#### 9.2.1 サービス停止時
```bash
# 1. 問題の特定
kubectl get pods -n production
kubectl get services -n production
kubectl get events -n production --sort-by='.lastTimestamp'

# 2. 緊急復旧
kubectl rollout restart deployment/repairgpt-api -n production

# 3. 代替手段の有効化
kubectl apply -f k8s/emergency/fallback-service.yaml -n production
```

#### 9.2.2 データベース障害時
```bash
# 1. スレーブDBへの切り替え
kubectl patch deployment repairgpt-api -n production -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "api",
          "env": [{
            "name": "DATABASE_URL",
            "value": "postgresql://postgres:password@postgres-slave:5432/repairgpt"
          }]
        }]
      }
    }
  }
}'

# 2. 読み取り専用モードの有効化
kubectl set env deployment/repairgpt-api READ_ONLY_MODE=true -n production
```

## 10. 継続的改善

### 10.1 定期的なタスク
- **日次**: ログ確認、バックアップ確認
- **週次**: パフォーマンス分析、セキュリティ更新確認
- **月次**: 容量計画見直し、依存関係更新
- **四半期**: 災害復旧テスト、運用手順見直し

### 10.2 改善計画
1. **自動化拡大**: 運用タスクの自動化
2. **監視強化**: より詳細なメトリクス収集
3. **パフォーマンス最適化**: 継続的な性能改善
4. **セキュリティ強化**: 定期的なセキュリティ監査