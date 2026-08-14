# Contract and retrieval debugging

This note documents several defects found while stabilizing the public `search_archive` and `get_context` behavior.

The individual failures appeared in different places — aggregation, Notion property mapping and content assembly — but they shared one pattern:

> A successful workflow execution is not enough if the returned object does not match the public contract.

The debugging work therefore focused on tracing values through the complete route rather than treating a successful Make run as proof of correct behavior.

## 1. Aggregation produced incomplete search results

### Observed behavior

`search_archive` could locate the correct Notion records while still returning incomplete result objects.

Fields in the normalized result could appear as `null`, even though the underlying archive record contained the expected values.

### Root cause

The result projection referenced the wrong Array Aggregator output after the scenario structure had changed.

The lookup itself was working.

The defect was between retrieval and response construction:

```text
correct Notion record
→ wrong aggregator source
→ incomplete public result
```

### Fix

The route was restored to an explicit projection chain:

```text
Notion Search
→ create normalized result object
→ aggregate results
→ return public response
```

The public result was kept separate from the raw Notion representation.

The tested search result fields are:

```text
id
title
project
summary
key-insights
model-origin
conversation_id
```

### Engineering consequence

Aggregator references are treated as bindings that must be reverified after route or module changes.

A visually successful scenario is not sufficient evidence because the workflow can find the right records and still map the wrong output into the contract.

Regression validation therefore checks the returned object, not only whether the Make scenario completed.

## 2. Stable identifiers disappeared during context retrieval

### Observed behavior

`get_context` could retrieve the correct archived conversation while returning:

```json
{
  "conversation_id": null
}
```

The value existed in Notion, so changing the public field name would not have addressed the underlying problem.

### Root cause

The parent route was not reading the value through the actual typed Notion output.

The stable conversation identifier is stored as rich text and needs to be mapped from the corresponding text projection exposed by the Notion module.

The working mapping uses the property's `plain_text` output.

### Engineering consequence

Notion properties are mapped according to their runtime output type rather than guessed from their display name.

When a field becomes `null`, the first question is therefore:

> Does the expected value reach the result-building module through the path we think it does?

Changing the public schema or coercing the type comes later, if the trace shows that the source value itself is correct.

## 3. Numeric metadata was lost through incorrect mapping

The same route returned a `null` `message_count`.

Again, the archive record already contained the value.

The correction was to map the actual Number property into the result object while preserving its numeric type.

No text conversion was required.

This matters because contract correctness includes types as well as values:

```text
Notion Number
→ Make numeric value
→ JSON number
```

Converting the property to text would have hidden one bug by introducing another contract mismatch.

## 4. `full_content` contained metadata that belonged outside the content field

### Observed behavior

The `get_context.full_content` string included both the archived conversation and presentation content such as:

```text
Full content
Details
Conversation ID
Start
Message count
Content length
```

Retrieval technically succeeded, but the field no longer had one clear meaning.

The corresponding `content_length` also measured the wrapper and metadata rather than only the archived conversation.

### Root cause

The archive page followed an established nine-item layout.

The formatter received the complete aggregated layout instead of only the item containing the archived conversation.

The formatter then behaved correctly: it normalized and joined exactly what the parent route supplied.

The defect therefore belonged to the parent route rather than to the shared formatter.

### Fix

The parent route narrows the aggregated page-content input before invoking the formatter.

The implementation uses:

```make
slice(...; 2; 3)
```

for the current archive layout.

In this layout, the selected position corresponds to the actual archived conversation content. The expression is an internal implementation detail; it is not part of the public request or response contract.

The resulting responsibility split is:

```text
get_context
→ identify the content that belongs to the public field

notion_text_formatter
→ normalize the selected content fragments

result builder
→ attach structured metadata separately
```

This avoided a broader redesign of the shared formatter.

## Why the formatter was not changed

A possible response to the mixed-content problem would have been to teach the shared formatter how to identify and discard page-specific metadata.

That would have made a reusable child workflow aware of one particular parent layout.

It would also have increased the regression surface for every caller of the formatter.

The narrower fix was therefore preferred:

> Correct the caller that supplied the wrong input instead of expanding the shared component to compensate for it.

This kept content selection in `get_context` and formatting in the formatter.

## 5. Testing the fixed-position assumption

The narrowed input introduced another question.

If one archived conversation could be split into several top-level page items, selecting one established position might truncate longer conversations.

That assumption needed runtime evidence rather than argument.

### Regression fixture

A retrieval fixture containing 10,000 characters of test content was archived and retrieved through `get_context`.

The returned content contained:

```text
10,011 characters
```

The additional 11 characters were the expected role prefix:

```text
The expected prefix was `ASSISTANT: `, including the trailing space.
```

The test verified that:

* the expected beginning and ending markers were present;
* all validation checkpoints were present;
* no truncation was detected;
* no duplication was detected;
* content order was preserved;
* metadata labels were absent from `full_content`;
* `content_length` matched the normalized returned content.

### What this proves

The test supports the fixed-position selection for the current archive layout and the tested 10,000-character fixture.

It does not establish that every future Notion page structure or arbitrarily large payload will always produce the same top-level content arrangement.

That distinction is intentional: the repository records the tested boundary rather than generalizing beyond the available evidence.

## 6. Public contract stabilization

The debugging work reinforced a boundary between implementation objects and public response objects.

`search_archive` does not expose raw Notion records.

`get_context` does not require callers to interpret presentation text to recover record metadata.

Instead, the public layer returns normalized structured values.

For search results, this includes the established result projection.

For context retrieval, conversation content and metadata are separate fields.

This also makes contract validation more useful because the schema can describe the response independently of Notion's native object shape.

Some invariants remain test responsibilities rather than schema responsibilities. For example, a standard JSON Schema can validate the type of `results_count` and the shape of `results`, but it does not by itself enforce:

```text
results_count == number of returned result objects
```

That relationship belongs in contract or regression tests.

## 7. Debugging approach that emerged

The defects produced a repeatable investigation sequence:

### 1. Verify the source record

Confirm that the expected value actually exists in Notion.

### 2. Trace the runtime output

Inspect the output of the module that first exposes that value inside Make.

### 3. Inspect the result-building input

Confirm that the expected value reaches the module responsible for constructing the public response.

### 4. Preserve the source type

Do not convert a Number to text or flatten structured content merely to remove a `null`.

### 5. Compare against the public contract

A successful route must still be rejected as incorrect if the returned object violates field, type or content semantics.

### 6. Add a regression case for the assumption behind the fix

The long-content fixture is an example of this step: the narrow `slice` correction was not treated as sufficient until the risk of truncating larger stored content had been exercised.

## Engineering outcome

The important result was not one corrected aggregator index or one Notion mapping expression.

The retrieval path became easier to reason about because responsibilities were separated:

```text
Notion
→ storage representation

Make route
→ lookup and projection

formatter
→ content normalization

public contract
→ stable external representation

regression tests
→ verification of behavior across those boundaries
```

That separation also limited the fixes.

The shared formatter did not need a broad redesign, raw Notion structures did not need to become part of the public contract, and type mismatches were not hidden by coercion.

The debugging process therefore became part of the architecture: trace the real runtime value, fix the layer that owns the defect, and add evidence for the assumption introduced by the correction.