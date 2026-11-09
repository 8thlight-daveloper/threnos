{ lib, self }:
let
  states = [ "on" "off" "ejected" ];
  registry = builtins.fromTOML (builtins.readFile ../skills/manifest.toml);
  skillDirs = builtins.attrNames (lib.filterAttrs (_: kind: kind == "directory") (builtins.readDir ../skills));

  defaultOf = name: (registry.skills.${name} or { }).default or "on";
  requiresOf = name: (registry.skills.${name} or { }).requires or [ ];
  citedBy = name: (registry.skills.${name} or { }).citedByRules or false;

  checked =
    assert lib.assertMsg (builtins.all (name: builtins.elem name skillDirs) (builtins.attrNames (registry.skills or { })))
      "skills/manifest.toml lists a skill that has no folder in skills/";
    assert lib.assertMsg
      (builtins.all (name: builtins.all (needed: builtins.elem needed skillDirs) (requiresOf name)) skillDirs)
      "skills/manifest.toml requires a skill that has no folder in skills/";
    assert lib.assertMsg (builtins.all (name: builtins.elem (defaultOf name) states) skillDirs)
      "skills/manifest.toml gives a skill a default other than on, off, or ejected";
    true;

  # Reads a project's manifest and returns what each skill and the rules are set to.
  # Throws on a state or skill it does not know, or on a missing required skill.
  resolve = manifestPath:
    assert checked;
    let
      manifest = if builtins.pathExists manifestPath then builtins.fromTOML (builtins.readFile manifestPath) else { };
      chosen = manifest.skills or { };
      unknown = builtins.filter (name: !(builtins.elem name skillDirs)) (builtins.attrNames chosen);
      stateOf = name: chosen.${name} or (defaultOf name);
      badState = builtins.filter (name: !(builtins.elem (stateOf name) states)) skillDirs;
      inState = wanted: builtins.filter (name: stateOf name == wanted) skillDirs;
      present = name: stateOf name != "off";
      rules = (manifest.rules or { }).regenerative or "on";

      missing = lib.concatMap
        (name: map (needed: { inherit name needed; }) (builtins.filter (needed: !(present needed)) (requiresOf name)))
        (builtins.filter present skillDirs);
      mentionRules = builtins.filter (name: stateOf name == "off" && citedBy name) skillDirs;

      warn = lib.foldl' (value: name: lib.warn "Skill ${name} is off, and the shared rules tell agents to use it." value);
    in
    assert lib.assertMsg (unknown == [ ]) "The manifest names skills that do not exist: ${toString unknown}";
    assert lib.assertMsg (badState == [ ]) "Each skill must be on, off, or ejected. Fix: ${toString badState}";
    assert lib.assertMsg (builtins.elem rules [ "on" "ejected" ]) "rules.regenerative must be on or ejected";
    assert lib.assertMsg (missing == [ ])
      (lib.concatMapStringsSep "; " (each: "${each.name} requires ${each.needed}, which is off") missing);
    warn
      {
        on = inState "on";
        off = inState "off";
        ejected = inState "ejected";
        inherit rules;
      }
      (if rules == "on" then mentionRules else [ ]);

  ownedEntries = resolved:
    lib.optional (resolved.rules == "on") ".agents/rules/regenerative.md"
    ++ lib.concatMap (name: [ ".agents/skills/${name}" ".claude/skills/${name}" ]) resolved.on;

  ejectedEntries = resolved:
    lib.optional (resolved.rules == "ejected") ".agents/rules/regenerative.md"
    ++ lib.concatMap (name: [ ".agents/skills/${name}" ".claude/skills/${name}" ]) resolved.ejected;

  lines = list: lib.concatStringsSep "\n" list + "\n";

  mkTree = pkgs: resolved:
    pkgs.runCommand "threnos-tree" { } ''
      mkdir -p $out/.agents/skills $out/.agents/rules $out/.claude/skills $out/seed
      ${lib.optionalString (resolved.rules == "on") "cp ${../rules/regenerative.md} $out/.agents/rules/regenerative.md"}
      ${lib.concatMapStrings (name: ''
        cp -r ${../skills + "/${name}"} $out/.agents/skills/${name}
        ln -s ../../.agents/skills/${name} $out/.claude/skills/${name}
      '') resolved.on}
      cp ${../templates/AGENTS.md} $out/seed/AGENTS.md
      cp ${../templates/CLAUDE.md} $out/seed/CLAUDE.md
      cp ${pkgs.writeText "owned" (lines (ownedEntries resolved))} $out/owned.txt
      cp ${pkgs.writeText "ejected" (lines (ejectedEntries resolved))} $out/ejected.txt
    '';

  # True when path $1 in the project holds the same thing as path $2 in the tree.
  same = ''
    same() {
      if [ -L "$2" ]; then
        [ -L "$1" ] && [ "$(readlink "$1")" = "$(readlink "$2")" ]
      else
        [ -e "$1" ] && [ ! -L "$1" ] && diff -r "$1" "$2" > /dev/null
      fi
    }
  '';

  mkSync = pkgs: tree:
    pkgs.writeShellApplication {
      name = "threnos-sync";
      runtimeInputs = [ pkgs.coreutils pkgs.diffutils pkgs.gnugrep ];
      text = ''
        tree=${tree}
        owned_file=.agents/.threnos-owned
        ${same}
        release() { chmod -R u+w "$1" 2> /dev/null || true; }

        previous=()
        if [ -f "$owned_file" ]; then mapfile -t previous < "$owned_file"; fi
        mapfile -t owned < <(grep . "$tree/owned.txt" || true)
        mapfile -t ejected < <(grep . "$tree/ejected.txt" || true)

        contains() { local needle=$1; shift; local each; for each in "$@"; do [ "$each" = "$needle" ] && return 0; done; return 1; }

        for entry in "''${previous[@]}"; do
          [ -n "$entry" ] || continue
          contains "$entry" "''${owned[@]}" && continue
          if [ -e "$entry" ] || [ -L "$entry" ]; then
            if contains "$entry" "''${ejected[@]}"; then
              [ -L "$entry" ] || release "$entry"
              echo "ejected  $entry"
            else
              release "$entry"
              rm -rf "$entry"
              echo "removed  $entry"
            fi
          fi
        done

        refused=0
        for entry in "''${owned[@]}"; do
          [ -n "$entry" ] || continue
          if { [ -e "$entry" ] || [ -L "$entry" ]; } && ! contains "$entry" "''${previous[@]}" && ! same "$entry" "$tree/$entry"; then
            echo "refused  $entry exists and differs. Set it to ejected in .agents/threnos.toml, or remove it." >&2
            refused=1
          fi
        done
        [ "$refused" = 0 ] || exit 1

        for entry in "''${owned[@]}"; do
          [ -n "$entry" ] || continue
          if same "$entry" "$tree/$entry"; then continue; fi
          release "$entry"
          rm -rf "$entry"
          mkdir -p "$(dirname "$entry")"
          cp -R --no-preserve=mode,ownership "$tree/$entry" "$entry"
          [ -L "$entry" ] || chmod -R a-w "$entry"
          echo "wrote    $entry"
        done

        for seed in AGENTS.md CLAUDE.md; do
          if [ ! -e "$seed" ]; then
            cp --no-preserve=mode,ownership "$tree/seed/$seed" "$seed"
            echo "seeded   $seed"
          fi
        done

        mkdir -p .agents
        [ -f "$owned_file" ] && release "$owned_file"
        printf '%s\n' "''${owned[@]}" | sort > "$owned_file"
      '';
    };

  devPackages = pkgs: [
    pkgs.git
    pkgs.gh
    pkgs.jq
    pkgs.just
    pkgs.lychee
    pkgs.markdownlint-cli2
    (pkgs.python3.withPackages (ps: [ ps.mdformat ps.mdformat-gfm ps.mdformat-frontmatter ]))
    pkgs.osv-scanner
    pkgs.uv
    pkgs.vale
  ];

  mkChecks = { pkgs, src, resolved, tree, recipes }: {
    threnos-drift = pkgs.runCommand "threnos-drift" { nativeBuildInputs = [ pkgs.diffutils ]; } ''
      ${same}
      cd ${src}
      status=0
      while read -r entry; do
        [ -n "$entry" ] || continue
        if ! same "$entry" ${tree}/"$entry"; then
          echo "drift: $entry differs from Threnos. Run: nix run .#sync" >&2
          status=1
        fi
      done < ${tree}/owned.txt
      ${lib.concatMapStrings (name: ''
        for entry in .agents/skills/${name} .claude/skills/${name}; do
          if [ -e "$entry" ] || [ -L "$entry" ]; then
            echo "drift: $entry should be absent because ${name} is off. Run: nix run .#sync" >&2
            status=1
          fi
        done
      '') resolved.off}
      [ "$status" = 0 ]
      touch $out
    '';

    threnos-recipes = pkgs.runCommand "threnos-recipes" { nativeBuildInputs = [ pkgs.just ]; } ''
      found=" $(just --justfile ${src}/justfile --summary) "
      status=0
      for recipe in ${toString recipes}; do
        case "$found" in
          *" $recipe "*) ;;
          *) echo "justfile has no recipe named $recipe" >&2; status=1 ;;
        esac
      done
      [ "$status" = 0 ]
      touch $out
    '';
  };

  # The outputs a project flake exposes for each system.
  # devShell is { packages, env, shellHook }. Its packages add to devPackages, and env sets variables in the shell.
  # packages holds the project's own outputs and may not use the name threnos-tree.
  mkProject = { pkgs, src, recipes ? [ "check" "mutate" "mutate-plan" "mutate-summary" "mutate-report" ], devShell ? { }, packages ? { } }:
    let
      resolved = resolve (src + "/.agents/threnos.toml");
      tree = mkTree pkgs resolved;
    in
    {
      devShell = pkgs.mkShell ({
        packages = devPackages pkgs ++ (devShell.packages or [ ]);
        shellHook = devShell.shellHook or "";
      } // (devShell.env or { }));
      apps.sync = {
        type = "app";
        program = lib.getExe (mkSync pkgs tree);
      };
      packages = assert lib.assertMsg (!(packages ? threnos-tree)) "packages.threnos-tree is reserved for the Threnos sync tree";
        packages // { threnos-tree = tree; };
      checks = mkChecks { inherit pkgs src resolved tree recipes; };
    };
in
{
  inherit resolve mkTree mkSync mkChecks mkProject devPackages registry;
}
