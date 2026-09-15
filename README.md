# stuft2/agents

A Codex plugin marketplace maintained by [stuft2](https://github.com/stuft2).

## Install the marketplace

```bash
codex plugin marketplace add https://github.com/stuft2/agents
```

## Repository layout

```text
.agents/plugins/marketplace.json  # Marketplace catalog
plugins/                          # Plugin packages
```

Each plugin belongs at `plugins/<plugin-name>/` and must include a
`.codex-plugin/plugin.json` manifest. Add its catalog entry to
`.agents/plugins/marketplace.json` using a source path of
`./plugins/<plugin-name>`.

## Add a plugin

From the plugin-creator skill directory, run:

```bash
python3 scripts/create_basic_plugin.py my-plugin \
  --path /path/to/agents/plugins \
  --marketplace-path /path/to/agents/.agents/plugins/marketplace.json \
  --with-marketplace
```

Validate the generated plugin before committing it:

```bash
python3 scripts/validate_plugin.py /path/to/agents/plugins/my-plugin
```

## License

[MIT](LICENSE)
