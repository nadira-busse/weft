# Datetime normalization and timezone handling

This note documents a set of related implementation defects in `archive_conversation` that led to the current datetime-normalization design.

The problem was not one isolated parsing error. Input normalization, validation, explicit end-time handling and installation-level timezone configuration all had to agree on the same contract.

## Problem

The public archive input accepts two useful datetime forms:

```text
ISO 8601 datetime
HH:mm local time
```

A local time such as:

```text
06:00
```

does not contain a date or timezone by itself.

The archive workflow therefore needs to turn that input into an unambiguous datetime before downstream validation and persistence.

The same normalization layer also has to handle `end_time` correctly:

* a supplied datetime must be preserved;
* a supplied `HH:mm` value must be resolved to a date;
* an omitted `end_time` needs a deterministic fallback;
* all local-time interpretation must use one installation timezone.

Several defects became visible because those responsibilities were initially handled independently.

## Defect 1 — local time reached the date parser without a date

The intended interpretation of:

```text
start_time: 06:00
```

was the configured local date at 06:00.

The first implementation did not reliably combine the date and time before calling Make's date parser. The parser therefore received only:

```text
06:00
```

and rejected it as an invalid date.

The working implementation first builds a complete value:

```text
YYYY-MM-DD HH:mm
```

and only then parses it into the normalized ISO representation.

This established an important ordering rule:

```text
raw input
→ construct complete datetime
→ parse
→ normalize
→ validate
```

## Defect 2 — validation still checked the raw input

After the local-time parser had been fixed, `HH:mm` input could be normalized successfully but was still rejected by the validation route.

The reason was structural rather than syntactic.

Normalization produced an ISO datetime, but validation still inspected the original client value and effectively asked whether the raw `HH:mm` string already looked like ISO 8601.

That created two conflicting contracts inside the same workflow:

```text
input contract     → HH:mm is valid
normalization      → HH:mm is supported
validation         → raw input must already be ISO
```

The fix was to validate the normalized outputs instead of re-validating the original transport representation.

The resulting boundary is:

```text
client representation
→ normalization
→ canonical representation
→ validation
→ persistence
```

This keeps transport flexibility outside the rest of the workflow.

## Defect 3 — explicit `end_time` was overwritten

The initial `end_time` path always derived `ended_at` from the execution time.

That was correct only when no explicit end time had been supplied.

For example, an archive request containing:

```text
end_time: 06:47
```

could still produce an `ended_at` value corresponding to the later moment when the workflow happened to run.

That matters when a conversation is archived after it actually ended.

The corrected decision logic is:

```text
end_time missing
→ use the current archive time

end_time is an ISO datetime
→ preserve and normalize the supplied datetime

end_time is HH:mm and start_time contains a date
→ combine that date with the supplied end time

start_time and end_time are both HH:mm
→ use the current local date
```

An explicit client value therefore takes precedence over the fallback.

## Avoiding self-reference during normalization

One attempted implementation tried to derive `ended_at` from `started_at` while both values were being produced by the same Make module.

That does not work.

A module's outputs are only available after that module has completed, so one output cannot be treated as an already-resolved dependency of another output in the same execution step.

The same constraint influenced the timezone design later.

Where normalization requires information from another derived value, the dependency must either:

* come from an earlier module; or
* be recomputed directly from the available upstream input.

The current archive flow avoids self-referential normalization.

## Central timezone configuration

The early datetime expressions contained the timezone directly:

```text
Europe/Amsterdam
```

That worked for the original environment but made the normalization logic unnecessarily repetitive. Changing timezone would have required finding and editing multiple parsing and formatting expressions, and a missed replacement could have caused inconsistent datetime handling inside one workflow.

The canonical `archive_conversation` blueprint now contains a dedicated upstream Make variable:

```text
weft_timezone = Europe/Amsterdam
```

In the current blueprint this is the `set timezone` module. The datetime-normalization expressions reference `weft_timezone` instead of embedding `Europe/Amsterdam` repeatedly. The same variable is also reused where the workflow derives the Daily Log date from the normalized start time.

The sequence is:

```text
MCP input
→ Set variable: weft_timezone
→ deterministic normalization
→ validation
→ archive processing
```

This creates one explicit adjustment point for timezone handling. An installation that needs another timezone can change the value of `weft_timezone` in that Make module to the appropriate IANA timezone instead of editing the individual date expressions.

The current repository evidence runtime-tests the canonical `Europe/Amsterdam` value. It does not independently prove runtime behavior for every other IANA timezone.

## Alternatives considered

### Rely on the Make organization timezone

Make can provide an organization-level timezone.

That would remove one scenario variable, but it would make datetime behavior depend on an external setting that is not visible in the archive workflow itself.

For the reproducible reference implementation, keeping the timezone explicit inside the workflow was preferred over relying on a hidden organization-level setting.

### Pass timezone with every archive request

A timezone field could also be added to the public MCP contract.

That would support callers with different local-time contexts, but it would also expand the contract and its validation requirements.

The current model is one installation-level timezone variable. The canonical blueprint sets `weft_timezone` to `Europe/Amsterdam`; an installation can change that single Make variable when it needs a different IANA timezone. Per-request timezone handling is not part of the public contract.

### Derive values from another output in the same normalization module

This was rejected because it introduces an invalid self-reference.

## Current contract

The resulting datetime behavior is:

```text
ISO datetime with explicit offset
→ normalize the supplied datetime

HH:mm
→ interpret the local time using the current weft_timezone value

missing end_time
→ use the current time through the same weft_timezone configuration
```

Validation operates on normalized values rather than requiring every supported client representation to already be canonical.

## Historical-date boundary

A value such as:

```text
06:00
```

contains neither a calendar date nor enough information to reconstruct one later.

If a conversation is archived on a different day and only `HH:mm` values are supplied, the workflow cannot infer the original historical date reliably.

For delayed archiving, the request should therefore provide at least a dated `start_time`, for example:

```text
start_time: 2026-08-03T06:00:00+02:00
end_time: 06:47
```

The end time can then inherit the known date from the start time.

This is an input-information boundary rather than a parsing defect.

## Engineering outcome

The final design separates four concerns that had initially become coupled:

1. accepting more than one client datetime representation;
2. producing one canonical internal representation;
3. validating that canonical representation;
4. applying one explicit installation-level timezone variable.

The main lesson from the defects was that normalization is only useful when downstream validation and persistence consistently consume the normalized values.

The fix was therefore not simply a better date expression. It was a clearer boundary between external input and canonical workflow state.