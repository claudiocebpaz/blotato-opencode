# Cuentas de Blotato — TEMPLATE

> Completá esta tabla con las cuentas conectadas a **tu** workspace de Blotato.
> Obtené los IDs reales con `python scripts/blotato.py accounts` (o `GET /users/me/accounts`).
> Reemplazá cada `<PLACEHOLDER>` por el valor que devuelva la API. No commitees IDs privados
> que no quieras compartir.

## Cuentas disponibles

| Plataforma | accountId | Subaccount / Page | pageId | Handle |
|---|---|---|---|---|
| LinkedIn | `<ACCOUNT_ID>` | `<PAGE_NAME>` | `<PAGE_ID>` | — |
| X / Twitter | `<ACCOUNT_ID>` | — | — | `<PLATFORM_HANDLE>` |
| Instagram | `<ACCOUNT_ID>` | — | — | `<PLATFORM_HANDLE>` |
| Facebook | `<ACCOUNT_ID>` | `<PAGE_NAME>` | `<PAGE_ID>` | — |

## Notas
- **LinkedIn Company Page** → se postea con `--account <ACCOUNT_ID> --page <PAGE_ID>`.
- **LinkedIn perfil personal** → `--account <ACCOUNT_ID>` (sin `--page`).
- **X / IG / Facebook** → `--account <ACCOUNT_ID>` (Facebook a página usa `--page <PAGE_ID>`).
- Si una plataforma todavía no está conectada en Blotato, conectala antes de postear.
