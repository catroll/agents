# ISO Maker (isomaker) — TODO

> Project: tools/isomaker
> Prefix: ISO
> Next ID: ISO-014
> Updated: 2026-11-21

## Theme: distro-neutral unattended installer builder (Debian 13 + Ubuntu 26.04)

### Batch B20261121-research — tooling research (target 2026-11-21, done)

- [x] **ISO-001** [P1][B20261121-research] Research the autoinstall/ISO tool landscape
  - Done when: a report compares the official stack and the known ISO/provisioning tools, and says whether the requirements are covered
  - Ev: `docs/iso-customization-research.md`; sample validated against Subiquity's schema
  - -> done 2026-11-21 (report + `examples/autoinstall.yaml`, schema validation passed)

### Batch B20261124-poc — first working Debian and Ubuntu ISOs (target 2026-11-28, open)

- [ ] **ISO-002** [P1][B20261124-poc] Lock the target release, firmware matrix and offline/online choice
  - Done when: Debian 13.7.0 + Ubuntu 26.04.1, UEFI/BIOS/Secure Boot, and install-time network are decided
  - Ev: target descriptor + decision recorded in `docs/architecture.md`
- [x] **ISO-003** [P1][B20261124-poc][dep ISO-008] Implement the render and build pipeline
  - Done when: one command turns a neutral profile into target artifacts and a patched ISO, with checksums and a manifest
  - Ev: Debian ISO lists `/preseed.cfg`; Ubuntu ISO lists `/autoinstall.yaml`
  - -> done 2026-11-21 (render/build CLI; synthetic ISOs patched for both adapters)
- [ ] **ISO-004** [P1][B20261124-poc][dep ISO-009,ISO-012] Add the QEMU/KVM install smoke test
  - Done when: CI installs from the patched ISO and asserts user, locale, keymap, timezone, disk layout and first-boot success
  - Ev: test log + guest assertions
- [x] **ISO-007** [P1][B20261124-poc][user] Decide the base image and tool boundary
  - Done when: snap hard-requirement, official-distro requirement, support duration, hardware generation and desktop/server parity are settled
  - Ev: `docs/base-image-decision.md`, `docs/architecture.md`
  - -> done 2026-11-21 (user selected Debian 13 latest stable; tool must stay distro-neutral)
- [x] **ISO-008** [P1][B20261124-poc] Define the distro-neutral profile schema and adapter contract
  - Done when: JSON Schema, target descriptor, semantic roles, secret references and capability/fail-closed rules are written and validated
  - Ev: `schemas/`, `isomaker/loader.py`, tests
  - -> done 2026-11-21 (strict schemas; semantic checks; 12 tests)
- [x] **ISO-009** [P1][B20261124-poc][dep ISO-008] Implement the Debian 13 adapter
  - Done when: neutral profile renders preseed, late-command, first-boot unit and build plan for Debian 13
  - Ev: `isomaker/adapters/debian.py`; rendered preseed inspected
  - -> done 2026-11-21 (desktop/server preseed; synthetic ISO build)
- [x] **ISO-010** [P1][B20261124-poc] Resolve and pin the two target releases
  - Done when: Debian 13.7.0 and Ubuntu 26.04.1 source ISO SHA256 and mirror are locked in the target descriptors/manifest
  - Ev: `targets/*.yaml`; manifests
  - -> done 2026-11-21 (Debian 13.7.0 and Ubuntu 26.04.1 hashes pinned)
- [x] **ISO-011** [P1][B20261124-poc][dep ISO-008] Add desktop and server profiles from the same schema
  - Done when: `desktop-gnome` and `server` profiles render and are tested separately, sharing the first-boot workflow
  - Ev: `profiles/desktop.yaml`, `profiles/server.yaml`, render tests
  - -> done 2026-11-21 (both profiles render for both targets; QEMU pending)
- [x] **ISO-012** [P1][B20261124-poc][dep ISO-008] Implement the Ubuntu 26.04 adapter
  - Done when: desktop and server targets render autoinstall/scripts and build a patched ISO; no_snap fails clearly
  - Ev: `isomaker/adapters/ubuntu.py`; synthetic ISO lists `/autoinstall.yaml`
  - -> done 2026-11-21 (snap kept; no_snap rejected; desktop/server render)
- [ ] **ISO-013** [P1][B20261124-poc][dep ISO-004] Build and boot the real distro ISOs
  - Done when: real Debian 13.7.0 and Ubuntu 26.04.1 ISOs are built from verified sources and installed unattended in QEMU
  - Ev: install logs, guest assertions, output ISO SHA256

### Batch B-backlog — unplanned (open)

- [ ] **ISO-005** [P2][B-backlog] Design the first-boot provisioning handoff
  - Done when: a systemd oneshot with retries runs Ansible/script, logs, and reports success or failure
  - Ev: failure-injection test
- [ ] **ISO-006** [P3][B-backlog] Evaluate the fully offline remaster
  - Done when: a package/language-pack bake path and its update cost are documented
  - Ev: offline VM install test
