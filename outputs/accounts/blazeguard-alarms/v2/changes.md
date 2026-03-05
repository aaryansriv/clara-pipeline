# Changelog — BlazeGuard Alarms
**Account ID:** blazeguard-alarms
**Date:** 2026-03-05 19:49 UTC
**Version:** v1 → v2

## Summary
Onboarding call completed. Agent configuration updated with confirmed operational details.

## LLM Extraction Notes
Updated office addresses, emergency routing rules, non-emergency routing rules, call transfer rules, and notification channels. Added pricing policy and post-call notification email.

## Field-Level Changes

### `non_emergency_routing_rules`
- **Before (v1):** `routine calls can wait until morning`
- **After (v2):** `routine calls can wait until morning, Milwaukee after-hours goes to email at milwaukee@blazeguardalarms.com`

### `office_address`
- **Before (v1):** `4200 North Harlem Avenue, Chicago`
- **After (v2):** `2211 West Fulton Street, Chicago; 890 North Plankinton Avenue, Milwaukee`

### `pricing_info`
- **Before (v1):** `None`
- **After (v2):** `{'service_call_fee': None, 'hourly_rate': None, 'billing_increment': None, 'disclose_on_request_only': True, 'notes': None}`

### `call_transfer_rules.retries`
- **Before (v1):** `None`
- **After (v2):** `3`

### `call_transfer_rules.message_if_fails`
- **Before (v1):** `None`
- **After (v2):** `our team has been paged and someone will call back within 15 minutes. If it's an active fire, please call 911.`

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** `None`
- **After (v2):** `40`

### `questions_or_unknowns`
- **Before (v1):** `["Kim's phone number", "Pete's phone number", 'specific routing rules for Chicago and Milwaukee', 'how to handle monitoring calls in ServiceTrade']`
- **After (v2):** `['how to handle monitoring calls in ServiceTrade', "Kim's phone number", "Pete's phone number", 'specific routing rules for Chicago and Milwaukee', 'Milwaukee ServiceTrade setup']`

### `notification_channels`
- **Before (v1):** `None`
- **After (v2):** `{'email': 'alerts@blazeguardalarms.com', 'sms': None, 'webhook': None}`

### `emergency_routing_rules`
- **Before (v1):** `[{'name': 'Kim', 'phone': None, 'order': 1, 'fallback': 'escalates to Ray'}, {'name': 'Pete', 'phone': None, 'order': 1, 'fallback': 'escalates to Ray'}, {'name': 'Ray', 'phone': '312-555-0166', 'order': 2, 'fallback': None}]`
- **After (v2):** `[{'name': 'Kim', 'phone': '312-555-0144', 'order': 1, 'fallback': 'escalates to Derek'}, {'name': 'Derek', 'phone': '312-555-0155', 'order': 2, 'fallback': 'escalates to Ray'}, {'name': 'Ray', 'phone': '312-555-0166', 'order': 3, 'fallback': None}]`

## Outstanding Items After Onboarding
- ⚠️ how to handle monitoring calls in ServiceTrade
- ⚠️ Kim's phone number
- ⚠️ Pete's phone number
- ⚠️ specific routing rules for Chicago and Milwaukee
- ⚠️ Milwaukee ServiceTrade setup