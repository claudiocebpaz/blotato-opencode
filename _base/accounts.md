# Blotato accounts — TEMPLATE

> Fill in this table with the accounts connected to **your** Blotato workspace.
> Get the real IDs with `python scripts/blotato.py accounts` (or `GET /users/me/accounts`).
> Replace each `<PLACEHOLDER>` with the value the API returns. Don't commit private IDs
> that you don't want to share.

## Available accounts

| Platform | accountId | Subaccount / Page | pageId | Handle |
|---|---|---|---|---|
| LinkedIn | `<ACCOUNT_ID>` | `<PAGE_NAME>` | `<PAGE_ID>` | — |
| X / Twitter | `<ACCOUNT_ID>` | — | — | `<PLATFORM_HANDLE>` |
| Instagram | `<ACCOUNT_ID>` | — | — | `<PLATFORM_HANDLE>` |
| Facebook | `<ACCOUNT_ID>` | `<PAGE_NAME>` | `<PAGE_ID>` | — |

## Notes
- **LinkedIn Company Page** → post with `--account <ACCOUNT_ID> --page <PAGE_ID>`.
- **LinkedIn personal profile** → `--account <ACCOUNT_ID>` (without `--page`).
- **X / IG / Facebook** → `--account <ACCOUNT_ID>` (Facebook to a page uses `--page <PAGE_ID>`).
- If a platform isn't connected in Blotato yet, connect it before posting.
