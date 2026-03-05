# Changelog — Shield Sprinkler Co.
**Account ID:** shield-sprinkler-co
**Date:** 2026-03-05 19:49 UTC
**Version:** v1 → v2

## Summary
Onboarding call completed. Agent configuration updated with confirmed operational details.

## LLM Extraction Notes
Updated emergency definitions, added James as third in the on-call chain, defined call transfer rules, and specified integration constraints and notification channels.

## Field-Level Changes

### `integration_constraints`
- **Before (v1):** `['Uses ServiceTrade', 'no auto-create jobs for backflow testing']`
- **After (v2):** `['Uses ServiceTrade', 'no auto-create jobs for backflow testing', 'Recognize Desert Fire Systems as internal callers']`

### `non_emergency_routing_rules`
- **Before (v1):** `None`
- **After (v2):** `Transfer directly to Donna for Desert Fire Systems calls`

### `office_address`
- **Before (v1):** `None`
- **After (v2):** `3344 North 7th Street, Phoenix, Arizona, 85014`

### `pricing_info`
- **Before (v1):** `None`
- **After (v2):** `{'service_call_fee': None, 'hourly_rate': None, 'billing_increment': None, 'disclose_on_request_only': True, 'notes': None}`

### `call_transfer_rules.retries`
- **Before (v1):** `None`
- **After (v2):** `3`

### `call_transfer_rules.message_if_fails`
- **Before (v1):** `None`
- **After (v2):** `We've been paged and someone will call back within 10 minutes.`

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** `None`
- **After (v2):** `30`

### `questions_or_unknowns`
- **Before (v1):** `["Tyler's phone number", "Donna's phone number", 'timeout rules', 'retries', 'message if call transfer fails']`
- **After (v2):** `["Donna's phone number", "Tyler's phone number", 'service_call_fee', 'retries', 'timeout rules', 'billing_increment', 'hourly_rate', 'message if call transfer fails']`

### `notification_channels`
- **Before (v1):** `None`
- **After (v2):** `{'email': 'office@shieldsprinkler.com', 'sms': None, 'webhook': None}`

### `emergency_routing_rules`
- **Before (v1):** `[{'name': 'Tyler', 'phone': None, 'order': 1, 'fallback': 'Donna'}, {'name': 'Donna', 'phone': None, 'order': 2, 'fallback': None}]`
- **After (v2):** `[{'name': 'Tyler', 'phone': '602-555-0133', 'order': 1, 'fallback': 'Donna'}, {'name': 'Donna', 'phone': '602-555-0177', 'order': 2, 'fallback': 'James'}, {'name': 'James', 'phone': '602-555-0191', 'order': 3, 'fallback': None}]`

### `emergency_definition`
- **Before (v1):** `['active sprinkler discharge', 'major panel fault']`
- **After (v2):** `['active water discharge from any sprinkler component', 'system alarm with a fault code', 'fire panel going completely offline']`

## Outstanding Items After Onboarding
- ⚠️ Donna's phone number
- ⚠️ Tyler's phone number
- ⚠️ service_call_fee
- ⚠️ retries
- ⚠️ timeout rules
- ⚠️ billing_increment
- ⚠️ hourly_rate
- ⚠️ message if call transfer fails