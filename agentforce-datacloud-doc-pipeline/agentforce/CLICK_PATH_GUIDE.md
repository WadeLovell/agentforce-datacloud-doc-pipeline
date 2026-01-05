# Salesforce Data Cloud + Agentforce Click Path Guide

This document provides exact UI navigation paths for configuring
Data Cloud and Agentforce for a middle-market banking POC.

---

## Prerequisites Checklist

Before starting, verify:

- [ ] Salesforce Data Cloud license enabled
- [ ] Agentforce license enabled
- [ ] Financial Services Cloud (FSC) enabled (if using FSC Data Kit)
- [ ] User has: System Administrator OR Data Cloud Admin + Agentforce Admin permissions
- [ ] Connected App created for API access

---

## PART 1: Data Cloud Configuration

### Step 1.1: Create Data Stream (Unstructured)

**Click Path:**
```
Setup → Data Cloud → Data Streams → New Data Stream
```

**Configuration:**
| Field | Value |
|-------|-------|
| Data Stream Name | `Procedure_Documentation_Stream` |
| Data Stream Type | `Unstructured` |
| Description | `Procedure-level documentation for Agentforce grounding` |

### Step 1.2: Create Data Lake Object (DLO)

**Click Path:**
```
Setup → Data Cloud → Data Lake Objects → New Data Lake Object
```

**Configuration:**
| Field | Value |
|-------|-------|
| DLO Name | `Agentforce_Support_Procedures` |
| Category | `Unstructured` |

**Add Fields:**
| Field Name | Type |
|------------|------|
| `content` | Text (Long) |
| `product` | Text |
| `module` | Text |
| `version` | Text |
| `persona` | Text |
| `content_type` | Text |
| `source_file` | Text |
| `title` | Text |

### Step 1.3: Configure Semantic Index

**Click Path:**
```
Setup → Data Cloud → Data Lake Objects → Agentforce_Support_Procedures → Indexing
```

**Configuration:**
| Setting | Value |
|---------|-------|
| Index Type | `Semantic` |
| Language | `English` |
| Content Field | `content` |
| Chunk Size | `800 tokens` |
| Chunk Overlap | `15%` |

### Step 1.4: Manual Upload (POC)

**Click Path:**
```
Setup → Data Cloud → Data Streams → Procedure_Documentation_Stream → Upload Files
```

1. Select all `.md` files from `output/datacloud_markdown/`
2. Map fields to schema
3. Click **Upload**
4. Wait for indexing to complete (~5-10 minutes for POC volume)

---

## PART 2: Agentforce Configuration

### Step 2.1: Create the Agent

**Click Path:**
```
Setup → Agentforce → Agents → New Agent
```

**Configuration:**
| Field | Value |
|-------|-------|
| Agent Name | `Support Procedure Agent` |
| API Name | `Support_Procedure_Agent` |
| Agent Type | `Support` |
| Status | `Active` |
| Description | `Support agent grounded exclusively in Data Cloud procedure documentation` |

### Step 2.2: Bind Data Source

**Click Path:**
```
Agentforce → Agents → Support Procedure Agent → Data Sources → Add
```

**Configuration:**
| Field | Value |
|-------|-------|
| Source Type | `Data Cloud` |
| Data Type | `Unstructured` |
| Dataset | `Agentforce_Support_Procedures` |
| Search Mode | `Semantic` |
| Language | `English` |

### Step 2.3: Configure Retrieval

**Click Path:**
```
Agentforce → Agents → Support Procedure Agent → Retrieval Settings
```

**Core Settings:**
| Setting | Value |
|---------|-------|
| Retrieval Strategy | `Semantic` |
| Top Results (Top-K) | `5` |
| Require Grounding | ✅ Enabled |
| Allow Ungrounded | ❌ Disabled |

**Static Filters (Add Both):**

Filter 1:
| Field | Operator | Value |
|-------|----------|-------|
| `persona` | equals | `support_agent` |

Filter 2:
| Field | Operator | Value |
|-------|----------|-------|
| `content_type` | equals | `procedure` |

**Dynamic Filters (Optional for Multi-Product):**
- `product` ← Context Variable: `Product`
- `module` ← Context Variable: `Module`

### Step 2.4: Create Prompt in Prompt Builder

**Click Path:**
```
Setup → Prompt Builder → New Prompt
```

**Configuration:**
| Field | Value |
|-------|-------|
| Prompt Type | `Agent Prompt` |
| Name | `Support_Procedure_Response` |

**System Instructions (Copy Verbatim):**
```
You are a support agent for a middle-market banking institution.

Use only retrieved Data Cloud documentation.
Return procedures as numbered steps in the order provided.
Do not invent, infer, or merge steps.
If no procedure is retrieved, state that the procedure is not documented.

For compliance: Always cite the source document when providing procedures.
```

**Response Settings:**
| Setting | Value |
|---------|-------|
| Response Style | `Procedural` |
| Numbered Steps | `Required` |
| Citations | `Required` |

**Assign to Agent:**
```
Prompt Builder → Support_Procedure_Response → Assign → Support Procedure Agent
```

### Step 2.5: Configure Guardrails

**Click Path:**
```
Agentforce → Agents → Support Procedure Agent → Guardrails
```

**Grounding Controls:**
| Setting | Value |
|---------|-------|
| Require Retrieval | ✅ Enabled |
| Allow External Knowledge | ❌ Disabled |

**Hallucination Controls:**
| Setting | Value |
|---------|-------|
| Allow Step Inference | ❌ Disabled |
| Allow Cross-Document Merging | ❌ Disabled |

**Fallback Message:**
```
I do not have a documented procedure for that request. 
Please contact your supervisor or compliance officer for guidance.
```

### Step 2.6: Enable Citations

**Click Path:**
```
Agentforce → Agents → Support Procedure Agent → Citations
```

**Configuration:**
| Setting | Value |
|---------|-------|
| Enable Citations | ✅ |
| Source Label | `Data Cloud Procedure` |
| Include Metadata | `product`, `module`, `version`, `source_file` |

### Step 2.7: Enable Observability (Recommended)

**Click Path:**
```
Agentforce → Agents → Support Procedure Agent → Monitoring
```

**Enable:**
- [x] Log Retrieval Results
- [x] Log Applied Filters  
- [x] Log Citations

**Retention:** 90 days (align to bank policy)

---

## PART 3: Validation Checklist

Before demo or client review, verify:

| Test | Expected Result |
|------|-----------------|
| Ask for documented procedure | Numbered steps with citation |
| Ask for undocumented procedure | Fallback message displayed |
| Check citation metadata | Product/module/version visible |
| Review logs | Retrieval + filters logged |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No results returned | Verify indexing complete in Data Cloud |
| Wrong procedures returned | Check filter configuration |
| Citations missing | Enable in Agent Citations settings |
| Steps out of order | Verify numbered_steps=required in Prompt Builder |

---

## Next Steps (POC → Production)

1. Replace manual upload with API ingestion
2. Implement JWT OAuth for production security
3. Add version diffing for incremental updates
4. Configure scheduled re-indexing
5. Integrate with FSC Data Kit for unified data model
