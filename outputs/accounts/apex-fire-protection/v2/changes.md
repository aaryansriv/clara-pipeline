# Changelog — Apex Fire Protection
**Account ID:** apex-fire-protection
**Date:** 2026-03-05 19:49 UTC
**Version:** v1 → v2

## Summary
Onboarding call completed. Agent configuration updated with confirmed operational details.

## LLM Extraction Notes
Updated business hours, office address, emergency definitions, routing rules, and integration constraints. Added panel fault as a semi-emergency and clarified pricing and notification channels.

## Field-Level Changes

### `integration_constraints`
- **Before (v1):** `['Uses ServiceTrade', 'Do not auto-create sprinkler or suppression jobs']`
- **After (v2):** `['Uses ServiceTrade', 'Do not auto-create sprinkler or suppression jobs', 'Do not log alarm monitoring calls as service jobs']`

### `business_hours.start`
- **Before (v1):** `8:00`
- **After (v2):** `7:30`

### `business_hours.end`
- **Before (v1):** `6:00`
- **After (v2):** `5:00`

### `business_hours.timezone`
- **Before (v1):** `None`
- **After (v2):** `Central`

### `office_address`
- **Before (v1):** `None`
- **After (v2):** `8820 Westpark Drive, Suite 200, Houston, Texas 77063`

### `pricing_info.disclose_on_request_only`
- **Before (v1):** `False`
- **After (v2):** `True`

### `call_transfer_rules.retries`
- **Before (v1):** `None`
- **After (v2):** `1`

### `call_transfer_rules.message_if_fails`
- **Before (v1):** `None`
- **After (v2):** `Our team has been paged and someone will call back within 15 minutes. If it's an active fire situation, please call 911 immediately.`

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** `None`
- **After (v2):** `45`

### `questions_or_unknowns`
- **Before (v1):** `["Janet's phone number", "Dave's phone number", "Marcus' phone number", 'office address', 'exact routing rules', 'timeouts']`
- **After (v2):** `["Marcus' phone number", "Dave's phone number", "Janet's phone number", 'timeouts', 'office address', 'exact routing rules']`

### `notification_channels`
- **Before (v1):** `None`
- **After (v2):** `{'email': 'dispatch@apexfireprotection.com', 'sms': None, 'webhook': None}`

### `emergency_routing_rules`
- **Before (v1):** `[{'name': 'Janet', 'phone': None, 'order': 1, 'fallback': 'Marcus'}, {'name': 'Marcus', 'phone': None, 'order': 2, 'fallback': 'Dave'}, {'name': 'Dave', 'phone': None, 'order': 3, 'fallback': None}]`
- **After (v2):** `[{'name': 'Janet', 'phone': '713-555-0142', 'order': 1, 'fallback': 'Marcus'}, {'name': 'Marcus', 'phone': '713-555-0198', 'order': 2, 'fallback': 'Dave'}, {'name': 'Dave', 'phone': '713-555-0207', 'order': 3, 'fallback': None}]`

### `emergency_definition`
- **Before (v1):** `['active sprinkler discharge', 'fire alarm triggered', 'CO alarm going off', 'active life safety event']`
- **After (v2):** `['active sprinkler discharge', 'fire alarm triggered', 'CO alarm going off', 'active life safety event', 'panel fault']`

## Outstanding Items After Onboarding
- ⚠️ Marcus' phone number
- ⚠️ Dave's phone number
- ⚠️ Janet's phone number
- ⚠️ timeouts
- ⚠️ office address
- ⚠️ exact routing rules