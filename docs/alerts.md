# Alert Rules and Runbooks

> **Owner**: Long  
> **Last Updated**: 2026-04-20  
> **Alert config**: [config/alert_rules.yaml](../config/alert_rules.yaml)  
> **SLO config**: [config/slo.yaml](../config/slo.yaml)

---

## 1. High Latency P95

**Severity**: 🟠 High (P2)  
**Trigger**: `latency_p95_ms > 3000 for 5m`  
**Related SLO**: latency_p95 (target: 95%, threshold: 3000ms, window: 28d)

### Symptoms
- P95 latency vượt quá 3000ms trong 5 phút liên tục
- User phản hồi response chậm, timeout
- Dashboard panel "Latency P95" spike đỏ

### Debug Steps (Metrics → Traces → Logs)
1. **Metrics**: Mở dashboard → Panel "Latency P95" → Xác định thời điểm spike bắt đầu
2. **Traces**: Vào Langfuse → Filter traces theo thời gian spike → Tìm spans chậm nhất
3. **Logs**: `cat data/logs.jsonl | jq 'select(.latency_ms > 3000)' | head -10`
   - So sánh RAG span vs LLM span → xác định bottleneck
4. **Incident toggles**: Check xem `rag_slow` incident có đang enabled không
   ```bash
   python scripts/inject_incident.py --status
   ```

### Mitigation
- Nếu RAG chậm: truncate long queries, dùng fallback retrieval source
- Nếu LLM chậm: giảm prompt size, switch sang model nhanh hơn
- Nếu cả hai: scale up service, enable request queue

### Escalation
1. **0-5 phút**: On-call engineer tự xử lý theo runbook
2. **5-15 phút**: Escalate lên Tech Lead, notify team qua Slack
3. **>15 phút**: Page SRE team, cân nhắc rollback deployment gần nhất

---

## 2. High Error Rate

**Severity**: 🔴 Critical (P1)  
**Trigger**: `error_rate_pct > 2% for 5m`  
**Related SLO**: error_rate (target: 98%, threshold: 2%, window: 28d)

### Symptoms
- Tỉ lệ lỗi vượt 2% trong 5 phút
- Users nhận được error responses (500, timeout)
- Dashboard panel "Error Rate %" vượt threshold line

### Debug Steps (Metrics → Traces → Logs)
1. **Metrics**: Dashboard → Panel "Error Rate" → Xác nhận spike, check error breakdown
2. **Traces**: Langfuse → Filter traces có `status: error` → Xem error spans
3. **Logs**: Group lỗi theo type:
   ```bash
   cat data/logs.jsonl | jq 'select(.level == "error") | .error_type' | sort | uniq -c | sort -rn
   ```
4. **Root cause**: Xác định lỗi từ LLM, tool, hay schema:
   - LLM error → check API key, rate limits, model availability
   - Tool error → check tool dependencies, input validation
   - Schema error → check request/response format changes

### Mitigation
- **Immediate**: Rollback latest deployment nếu error bắt đầu sau deploy
- **LLM failure**: Retry với fallback model (e.g., gpt-3.5 thay vì gpt-4)
- **Tool failure**: Disable failing tool, route qua alternative path
- **Schema error**: Fix validation, deploy hotfix

### Escalation
1. **0-5 phút**: On-call xử lý ngay — P1 severity, phải acknowledge trong 5 phút
2. **5-10 phút**: Escalate Tech Lead + Product Owner (user impact)
3. **>10 phút**: War room — all hands, cân nhắc feature flag off hoặc full rollback

---

## 3. Cost Budget Spike

**Severity**: 🟠 High (P2)  
**Trigger**: `daily_cost_usd > 2.5 for 15m`  
**Related SLO**: cost_budget (target: 100%, budget: $2.5/day, window: 1d)

### Symptoms
- Chi phí LLM vượt budget $2.5/ngày
- Token usage tăng đột biến
- Dashboard panel "Cost Estimate" vượt budget line

### Debug Steps (Metrics → Traces → Logs)
1. **Metrics**: Dashboard → Panel "Cost Estimate" → Xem cost trend, "Token Usage" → So sánh input vs output tokens
2. **Traces**: Langfuse → Sort by `cost_estimate` descending → Tìm requests tốn kém nhất
   - Split traces theo feature và model → identify nguồn chi phí chính
3. **Logs**: Tính cost breakdown:
   ```bash
   cat data/logs.jsonl | jq 'select(.cost_estimate != null) | {feature, model, cost_estimate}' | head -20
   ```
4. **Check**: `cost_spike` incident có đang enabled không

### Mitigation
- **Immediate**: Shorten prompts, giảm max_tokens
- **Short-term**: Route easy/simple requests sang cheaper model (e.g., gpt-3.5-turbo)
- **Long-term**: Implement prompt caching, batch requests, smart routing

### Escalation
1. **Budget 80%**: Warning notification tới FinOps owner
2. **Budget 100%**: Alert team-oncall, cân nhắc throttle traffic
3. **Budget 150%**: Escalate Engineering Manager, implement hard cost cap

---

## 4. Low Quality Score

**Severity**: 🟡 Warning (P3)  
**Trigger**: `quality_score_avg < 0.75 for 10m`  
**Related SLO**: quality_score (target: 95%, threshold: 0.75, window: 28d)

### Symptoms
- Quality score trung bình giảm dưới threshold 0.75
- User feedback tiêu cực tăng
- Regenerate rate tăng cao

### Debug Steps (Metrics → Traces → Logs)
1. **Metrics**: Dashboard → Panel "Quality Score" → Check trend
2. **Traces**: Langfuse → Filter low-quality responses → Xem retrieval context có liên quan không
3. **Logs**: Phân tích responses chất lượng thấp:
   ```bash
   cat data/logs.jsonl | jq 'select(.quality_score < 0.75) | {query: .query[:50], quality_score, model}' | head -10
   ```

### Mitigation
- Check RAG retrieval relevance — prompt tuning
- Review recent model/prompt changes
- Tăng retrieval k-value, thêm re-ranking step

### Escalation
1. **0-30 phút**: Monitor trend, thu thập data
2. **>30 phút**: Notify ML team để review model quality
3. **>1 giờ**: Cân nhắc rollback prompt/model changes

---

## Appendix: Debug Commands Cheat Sheet

```bash
# Check alert rule match
cat data/logs.jsonl | jq 'select(.latency_ms > 3000)' | wc -l

# PII leak check
cat data/logs.jsonl | grep -E '\b[\w.-]+@[\w.-]+\.\w+\b' | wc -l

# Inject test incident
python scripts/inject_incident.py --scenario rag_slow

# View recent errors
cat data/logs.jsonl | jq 'select(.level == "error")' | tail -5

# Cost summary
cat data/logs.jsonl | jq '[.cost_estimate // 0] | add'
```
