# 12. Next free management IP with a fallback prefix

## What you'll learn

- A **fallback** step: `reserve_fallback` runs only when `reserve_primary` has `status == 'failed'`.
- A step that runs when **either** earlier step succeeded, using `or` in its condition.
- Choosing a value from whichever step worked, inside a `with:` value:

```yaml
address: "{{ results.reserve_primary.return_value.address if results.reserve_primary.status == 'success' else results.reserve_fallback.return_value.address }}"
```

| Step | Runs when | Does |
| --- | --- | --- |
| `reserve_primary` | always | Takes the next free address in the preferred prefix. Fails if the prefix is full |
| `reserve_fallback` | `reserve_primary` failed | Takes the next free address in the fallback prefix |
| `assign_ip` | either reservation succeeded | Puts the address on the management interface and makes it the primary IPv4 |

The lab seed creates `10.20.255.0/29` (AMS01) and `10.21.255.0/29` (NYC02) with every address already used, so they are full for real. It also creates the fallback prefixes `10.20.254.0/24` and `10.21.254.0/24`.

## Why the fallback run still shows Failed

`reserve_primary` really failed, so the run ends **Failed** even though the fallback worked and the device got an address. Open the run to see the fallback and the assignment marked **Success**. If you would rather have a full preferred pool count as a normal outcome, have the first step return `{"available": false}` instead of failing, and branch on that value as example 13 does.

## How to run

1. Run the [lab seed](../README.md#lab-setup).
2. Choose **Run** on **12. Next free management IP with a fallback prefix**.
3. Pick **AMS01**, `ams01-acc-sw03`, and `Management1`.
4. **Preferred path:** choose `10.20.254.0/24` as preferred and anything as fallback. `reserve_fallback` is skipped.
5. **Fallback path:** choose `10.20.255.0/29` as preferred and `10.20.254.0/24` as fallback. Or turn on **Treat the preferred prefix as full** with any preferred prefix.
6. With **Apply** off, the steps only report the address they found. With **Apply** on, the address is reserved and the device's primary IPv4 changes in this lab.

## Next

[13. Software upgrade with pre and post checks](13-upgrade-with-pre-post-checks.md) branches on a value a step returns, not on whether it failed.
