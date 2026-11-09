{
  description = "Threnos: the regenerative software process, its rules, and its skills";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      lib = nixpkgs.lib;
      systems = [ "aarch64-darwin" "aarch64-linux" "x86_64-linux" ];
      forAllSystems = build: lib.genAttrs systems (system: build nixpkgs.legacyPackages.${system});
      threnos = import ./nix/lib.nix { inherit lib self; };

      # What a project flake exposes. See scaffold/flake.nix.
      # devShell and packages are functions of pkgs. devShell returns { packages, env, shellHook }.
      projectOutputs = { src, recipes ? [ "check" "mutate" "mutate-plan" "mutate-summary" "mutate-report" ], devShell ? (_: { }), packages ? (_: { }) }:
        let
          each = forAllSystems (pkgs: threnos.mkProject {
            inherit pkgs src recipes;
            devShell = devShell pkgs;
            packages = packages pkgs;
          });
        in
        {
          devShells = lib.mapAttrs (_: project: { default = project.devShell; }) each;
          apps = lib.mapAttrs (_: project: project.apps) each;
          packages = lib.mapAttrs (_: project: project.packages) each;
          checks = lib.mapAttrs (_: project: project.checks) each;
        };
    in
    {
      lib = threnos // { inherit projectOutputs systems; };

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell { packages = threnos.devPackages pkgs; };
      });

      # Everything with each skill at its default. Projects build their own through lib.projectOutputs.
      packages = forAllSystems (pkgs: {
        threnos-tree = threnos.mkTree pkgs (threnos.resolve ./scaffold/.agents/threnos.toml);
      });

      checks = forAllSystems (pkgs:
        let
          resolved = threnos.resolve ./scaffold/.agents/threnos.toml;
          seedTree = threnos.mkTree pkgs resolved;
        in
        {
          scaffold-resolves = pkgs.writeText "scaffold-resolves" (builtins.toJSON resolved);
          records-tests = pkgs.runCommand "records-tests" { } ''
            cd ${./tools/records}
            ${threnos.recordsPython pkgs}/bin/python -B -m unittest
            touch $out
          '';
          acceptance-imports-tests = pkgs.runCommand "acceptance-imports-tests" { } ''
            cd ${./languages/go/acceptance-imports}
            ${threnos.recordsPython pkgs}/bin/python -B -m unittest
            touch $out
          '';
          # The seeds a project gets must stand alone: no broken links, and the live ones formatted.
          # lychee builds an HTTP client even offline, and the build sandbox on Linux has no certificates.
          seeds-links = pkgs.runCommand "seeds-links" { nativeBuildInputs = [ pkgs.lychee ]; SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"; } ''
            cd ${seedTree}/seed
            lychee --offline --include-fragments --no-progress '**/*.md'
            touch $out
          '';
          seeds-formatted = pkgs.runCommand "seeds-formatted" { nativeBuildInputs = [ (threnos.markdownPython pkgs) ]; } ''
            cd ${seedTree}/seed
            mdformat --check --wrap 120 $(find . -name '*.md' -not -path './docs/reference/templates/*')
            touch $out
          '';
          # Threnos's own records are method decisions, so the check runs on them here.
          records-self = pkgs.runCommand "records-self" { } ''
            ${threnos.recordsPython pkgs}/bin/python ${./tools/records/check.py} --framework ${./.}
            touch $out
          '';
        });

      templates.default = {
        path = ./scaffold;
        description = "A project that follows the regenerative process, with Threnos rules and skills";
      };
    };
}
