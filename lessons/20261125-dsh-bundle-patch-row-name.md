# A DSH bundle patch row's `name` is resolved from the profile root

## Trigger

- `dsh: warning: 1 entry did not activate` followed by
  `our-free-model (dsh-our-free-model): failed to import: Error [ERR_MODULE_NOT_FOUND]: Cannot find package 'dsh-our-free-model' imported from /home/catroll/.dsh/profiles/web/`
- Or the Plugins page shows a bundle as **配置状态 已启用 / 运行状态 未运行** while
  its package is installed and its models never appear.
- Or a bundle's patch row names a package that is not in the profile's
  `node_modules`: e.g. a scoped npm publish of a repo whose `package.json` name is
  bare.

## What was true (2026-11-25, `@ebony-vinyl/dsh-our-free-model@2.8.5`)

The installed package is scoped (`@ebony-vinyl/dsh-our-free-model`), but its
`cordis.patch.yml` inserts:

```yaml
- insert:
    - id: our-free-model
      name: 'dsh-our-free-model'
```

A row's `name` is a **module specifier resolved from the profile root**
(`/home/catroll/.dsh/profiles/web/`), not from the bundle package's own directory.
Nothing named `dsh-our-free-model` is installed there, so the Host half never
imports; `ctx.llm.registerAdapter()` never runs and no model rows exist. The npm
scoped tarball was repackaged from a repo whose package name is still
`dsh-our-free-model` (only `package.json` name was rewritten), so the patch name
and the installed specifier disagree. Upstream v2.9.0 has the same row.

`enabled` on the Plugins page is the saved selection, not load success; the plugin
manager README says an unloadable selected bundle is shown as 未运行.

## Check

```sh
P=~/.dsh/profiles/web/node_modules/<pkg>
grep -n "name:" "$P/cordis.patch.yml"            # must equal the installed specifier
journalctl --user -u dsh-web.service -n 80 | grep "did not activate" -A3
node -e "import('<row name>').then(()=>console.log('ok'),e=>console.log(e.code))"  # from the profile dir
```

## Fix

Either make the row name resolvable (npm alias in the profile's `package.json`,
then `pnpm install`):

```json
"dsh-our-free-model": "npm:@ebony-vinyl/dsh-our-free-model@2.8.5"
```

(verified: `import('dsh-our-free-model')` then resolves to the trusted package), or
install a tarball whose package name equals the patch row name. Never install the
third-party bare-named npm package when upstream warns it differs.

General rule: bundle patch row `name` = the package specifier as installed in the
profile; official bundles follow this (`@deepseek-ai/dsh-plugin-manager/tools`).
A scoped publish must rewrite every row name to the scoped name.
