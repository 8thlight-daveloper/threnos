{
  description = "A project built the regenerative way";

  inputs.threnos.url = "github:8thlight-daveloper/threnos";
  inputs.nixpkgs.follows = "threnos/nixpkgs";

  outputs = { self, threnos, ... }:
    threnos.lib.projectOutputs {
      src = self;
      # Recipes the justfile must define. Drop the mutation recipes if the project never runs mutation in CI.
      recipes = [ "check" "mutate" "mutate-plan" "mutate-summary" "mutate-report" ];
      # The project's dev shell, added to the Threnos tools. Each field is optional.
      # Example: { packages = [ pkgs.go ]; env.GODEBUG = "gcshrinkstackoff=1"; shellHook = "unset GOROOT"; }
      devShell = pkgs: { packages = [ ]; env = { }; shellHook = ""; };
      # The project's own outputs, such as its built binary as packages.default.
      packages = pkgs: { };
    };
}
