# pack

## What it does

Turns a learning pack JSON into the files people read:

- `<pack>.html`: a self-contained page that works offline and prints well. Each cited ID opens the finding or evidence it refers to, the findings in scope that the pack does not cite are listed, and the footer carries the status phrase and the ProbeMatrix credit;
- `<pack>.md`: the same content as Markdown, for email, a wiki or a document.

It first runs the full [check-pack](check-pack.md). If the check finds a problem, nothing is written. A pack that has not been signed off renders with a **DRAFT** label.

## When to use it

After [check-pack](check-pack.md) passes. Run it again after every edit of the JSON; the HTML is rebuilt each time.

## Synopsis

```text
pmlc pack ws pack [--out OUT] [--no-md]
```

## Arguments

| Argument | What it is |
|---|---|
| `ws` | The workspace folder |
| `pack` | The learning pack JSON |

## Flags

| Flag | Value | Default | What it does |
|---|---|---|---|
| `--out` | folder | the run's outputs folder | Where to write the HTML and Markdown |
| `--no-md` | none | off | Write only the HTML |
| `-h`, `--help` | none | | Show the flags and stop |

## Examples

The Hazira board brief from the [check-pack](check-pack.md) example:

```bash
python3 $E pack $WS $OUT/board-brief.json
```

```text
warning: coverage: cites 3 of 308 relevant findings (under a quarter)
warning: no handling block: rendered as draft (internal)
HTML written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.html
Markdown written to hazira/pmlc-runs/2020-09-24-hazira-gas-release-fire/outputs/board-brief.md
```

Only the HTML, into another folder:

```bash
python3 $E pack $WS $OUT/board-brief.json --no-md --out print
```

```text
warning: coverage: cites 3 of 308 relevant findings (under a quarter)
warning: no handling block: rendered as draft (internal)
HTML written to print/board-brief.html
```

A pack with a problem is not rendered:

```bash
python3 $E pack $WS bad.json
```

```text
sections[1].items[0].cites[1]: FND-00000000 is not in this workspace
warning: no handling block: rendered as draft (internal)
1 problem(s) in bad.json. Nothing written.
```

## Common problems

- **"Nothing written."** The pack failed its check. Fix the problems listed above that line, then run pack again.
- **The page says DRAFT.** It will until a reviewer signs it off with [sign-off](sign-off.md), and always while the investigation is in progress or no finding has been edited by a person in ProbeMatrix.
- **Old HTML after an edit.** pack does not watch the file. Run it again after each change.
- **Where did the files go?** Without `--out`, into the run's outputs folder; [run-path](run-path.md) prints it.

## Related

- [check-pack](check-pack.md) runs first.
- [causal-item](causal-item.md) makes a graph item for a pack.
- [dashboard](dashboard.md) is the whole-organisation view.
- [Skills](../Skills.md): every audience skill ends with check-pack and pack.
