# MAI-METRICS: DIR / DOR / DRI and C1-C8 Model

Статус: Draft v0.1
Связанные документы: MAI Constitution, MAI-STD-001, MAI-MET-001

## 1. Назначение

Этот документ фиксирует измерительную модель Decision Reliability Engineering.

Метрики MAI оценивают не "качество проекта вообще", а надежность decision object относительно конкретного decision gate.

## 2. Основные метрики

| Метрика | Название | Что измеряет |
|---|---|---|
| DIR | Decision Information Reliability | Надежность конкретной информации относительно decision gate. |
| DOR | Decision Object Reliability | Надежность всего decision object как основания для действия. |
| DRI | Decision Reliability Index | Индекс надежности decision object по C1-C8. |

## 3. Каноническая модель C1-C8

| Код | Измерение | Краткое определение |
|---|---|---|
| C1 | Claim Consistency | Claims согласованы между собой, с источниками, evidence и scope. |
| C2 | Evidence Sufficiency | Evidence достаточно для уровня claims и выбранного gate. |
| C3 | Decision Architecture | Decision object содержит ясную архитектуру перехода от evidence к action. |
| C4 | Communication Integrity | Коммуникация не создает противоречий, перегрузки или ложной ясности. |
| C5 | Commercial Readiness | Коммерческий контур достаточен для проверяемого действия. |
| C6 | Risk Transparency | Риски, ограничения, liability, regulatory exposure и unknowns явно раскрыты. |
| C7 | Verification Traceability | Проверки, источники, validation path и evidence lineage прослеживаемы. |
| C8 | Decision Actionability | Есть допустимое следующее действие с условиями, владельцем и границами. |

## 4. Уровни DRI

| Уровень | Измерения | Центральный вопрос |
|---|---|---|
| Epistemic Reliability | C1, C2 | Можно ли доверять тому, что утверждается? |
| Decision Architecture | C3, C4, C7 | Можно ли превратить пакет в воспроизводимое решение? |
| Operational Readiness | C5, C6, C8 | Можно ли безопасно сделать следующий шаг? |

## 5. Шкала

| Балл | Интерпретация |
|---|---|
| 0-20 | Ненадежно для данного gate. |
| 21-40 | Слабая надежность; требуется внешнее восстановление логики. |
| 41-60 | Частичная надежность; интерес возможен, commitment преждевременен. |
| 61-80 | Используемо с условиями; допустимы ограниченные действия. |
| 81-100 | Надежно для выбранного gate при указанных предпосылках. |

## 6. Правила интерпретации

Высокий C2 не компенсирует низкий C3: сильная evidence base не означает, что decision object готов к решению.

Высокий C5 не компенсирует низкий C1: коммерческая привлекательность не исправляет противоречивые claims.

Высокий C8 может означать только низкообязательное действие. Например, Data Room request может быть highly actionable, даже если investment gate закрыт.

Overall DRI должен всегда сопровождаться gate-specific interpretation.

## 7. Минимальный вывод

Каждый отчет должен содержать:

```text
Epistemic Reliability      __/100
Decision Architecture      __/100
Operational Readiness      __/100
Overall DRI                __/100
Admissible Next Action     ______
Blocked Decision Gates     ______
```

## 8. Связь с failure patterns

Failure patterns объясняют, почему конкретные C-измерения проваливаются.

Примеры:

| Failure Pattern | Чаще всего снижает |
|---|---|
| MAI-FM-001 Silent Review Termination | C3, C4, C7, C8 |
| MAI-FM-002 Evidence Saturation | C2, C3, C7 |
| MAI-FM-003 Claim Inflation | C1, C2, C4 |
| MAI-FM-004 Authority Substitution | C2, C7 |
| MAI-FM-005 Decision Deferral | C3, C8 |
| MAI-FM-006 Semantic Overload | C3, C4, C8 |
