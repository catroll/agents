# A wrapping flex row split two icon buttons that must stay together

## Symptom

A toolbar was a wrapping flex row containing a search field and two 40px icon
buttons (theme and settings). At some toolbar widths the settings icon rendered
on the next line instead of to the right of the theme icon.

Reproduced by constraining the toolbar to 280px:

```text
search   left=820  top=40  w=232
theme    left=1060 top=40  w=40
settings left=1060 top=88  w=40
```

## Cause

Flex line packing is sequential. The search item (`flex-basis: 220px`), the
theme button (40px) and one gap fit on the first line; adding the settings button
plus its gap exceeded 280px, so only the settings button wrapped. Independent
flex items have no reason to stay together, even when they are semantically one
control group.

## Fix

Wrap the tightly coupled buttons in a child that never wraps internally:

```css
.actions {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}
```

The group is now one flex item. The whole pair moves to the next line together,
so the second button is always to the right of the first.

## Check

Set the toolbar to widths from 100px to 300px and assert both buttons have the
same `getBoundingClientRect().top` and different `left` values; repeat at the
normal desktop and mobile viewport widths.
