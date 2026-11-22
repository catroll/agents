# xorriso repack of a hybrid ISO: `keep` can leave the MBR beyond the new end

## Symptom

Repacking a Debian netinst ISO with `xorriso -indev src -outdev dst ... -boot_image any keep`
printed:

    libburn : SORRY : Read start address 387071s larger than number of readable blocks 386304
    xorriso : NOTE : -return_with SORRY 32 triggered by problem severity SORRY

The output was a few hundred blocks shorter than the source, but the preserved
hybrid MBR still pointed past the new end.

## Procedure

- `-boot_image any replay` rebuilds the boot layout against the new image size;
  `any keep` preserves stale append/partition offsets.
- `xorriso -extract` keeps the source file mode; `chmod 0644` before editing.
- Patch only the default boot entry; do not autoinstall rescue/expert entries.
- Insert kernel parameters before `---`, not after.

## Negative result

The output existed and looked complete, but the repack returned 32; a script
that only checks the file's existence would ship a questionable hybrid ISO.
Check the xorriso exit code and `-report_el_torito as_mkisofs`.
