# Changelog — PeakFire Services
**Account ID:** peakfire-services
**Date:** 2026-03-05 19:50 UTC
**Version:** v1 → v2

## Summary
Onboarding call completed. Agent configuration updated with confirmed operational details.

## LLM Extraction Notes
Updated business hours, office address, emergency definitions, and routing rules. Added non-emergency routing rules and notification channels.

## Field-Level Changes

### `integration_constraints`
- **Before (v1):** `['Uses Housecall Pro', 'Do not auto-create jobs for warranty inquiry calls']`
- **After (v2):** `['Uses Housecall Pro', 'Do not auto-create jobs for warranty inquiry calls', 'Do not create jobs for competitor research calls']`

### `non_emergency_routing_rules`
- **Before (v1):** `None`
- **After (v2):** `Politely decline competitor research calls and do not create a job. For warranty inquiries, provide email warranty@peakfireservices.com`

### `business_hours.start`
- **Before (v1):** `None`
- **After (v2):** `7:30 AM`

### `business_hours.end`
- **Before (v1):** `None`
- **After (v2):** `5:30 PM`

### `business_hours.timezone`
- **Before (v1):** `None`
- **After (v2):** `MST Denver`

### `business_hours.days`
- **Before (v1):** `['Monday', 'Friday']`
- **After (v2):** `['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']`

### `office_address`
- **Before (v1):** `None`
- **After (v2):** `4455 South Monaco Street, Denver, Colorado, 80237`

### `call_transfer_rules.message_if_fails`
- **Before (v1):** `None`
- **After (v2):** `The team has been notified and someone will call back within 20 minutes`

### `call_transfer_rules.timeout_seconds`
- **Before (v1):** `None`
- **After (v2):** `50`

### `questions_or_unknowns`
- **Before (v1):** `['Confirm business hours', 'Notification preferences', 'Special rules', 'Phone numbers for on-call team members']`
- **After (v2):** `['Phone numbers for on-call team members', 'Confirm pricing info', 'Notification preferences', 'Special rules', 'Confirm pricing structure and billing details', 'Confirm business hours']`

### `notification_channels`
- **Before (v1):** `None`
- **After (v2):** `{'email': ['dispatch@peakfireservices.com', 'sandra@peakfireservices.com'], 'sms': None, 'webhook': None}`

### `emergency_definition`
- **Before (v1):** `['Active fire', 'Suppression system discharge', 'CO alarm triggered', 'Panel goes offline completely']`
- **After (v2):** `['Active fire or smoke', 'Suppression system discharge', 'CO alarm triggered', 'Alarm panel completely offline']`

## Outstanding Items After Onboarding
- ⚠️ Phone numbers for on-call team members
- ⚠️ Confirm pricing info
- ⚠️ Notification preferences
- ⚠️ Special rules
- ⚠️ Confirm pricing structure and billing details
- ⚠️ Confirm business hours