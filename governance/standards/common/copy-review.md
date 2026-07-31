# User-Facing Copy Review Standard

## Purpose

Ensure all new or modified user-facing copy (Chinese/English names, descriptions, etc.) is confirmed by the product owner before release.

## Scope

`runtime-release`

## Checklist

- [ ] Do new/modified enum display names have corresponding Chinese and English copy?
- [ ] Has the copy been confirmed by the product owner?
- [ ] Has the confirmed copy been synchronized to all locations?
  - Java enum comments
  - i18n properties files
  - SQL scripts (e.g., `event_name` in `audit_event_types`)

## BLOCKER Conditions

- Unconfirmed user-facing copy exists
- Copy confirmed but not synchronized to all locations
