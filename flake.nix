{
  description = "Midi Stutter";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils"; 
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        # individual pkgs
        mydevEnv = with pkgs; [
          fish

          #### Nix development
          # deadnix
          # nixd
          # nix-diff
          # nixfmt-rfc-style
          # statix
        ];

        # Python & Libraries from nixpkgs
        myPythonEnv = pkgs.python3.withPackages (py: [
          # py.python-dotenv
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          name = "dev-shell";
          packages = [
            myPythonEnv
            mydevEnv
          ];
          shellHook = ''
            echo "DevShell is now active"
            python --version
            exec fish
          '';
        };
      }
    );
}
 