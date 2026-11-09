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
        in
        { scaffold-resolves = pkgs.writeText "scaffold-resolves" (builtins.toJSON resolved); });

      templates.default = {
        path = ./scaffold;
        description = "A project that follows the regenerative process, with Threnos rules and skills";
      };
    };
}
