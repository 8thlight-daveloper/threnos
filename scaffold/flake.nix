{
  description = "A project built the regenerative way";

  inputs.threnos.url = "github:8thlight-daveloper/threnos";
  inputs.nixpkgs.follows = "threnos/nixpkgs";

  outputs = { self, threnos, ... }:
    threnos.lib.projectOutputs {
      src = self;
      # Recipes the justfile must define. Add the mutation recipes when CI runs them.
      recipes = [ "check" ];
      # Tools this project needs beyond the Threnos set, such as pkgs.go.
      extraPackages = pkgs: [ ];
    };
}
