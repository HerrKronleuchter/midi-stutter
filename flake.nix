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
        ];

        # Python & Libraries from nixpkgs
        myPythonEnv = pkgs.python3.withPackages (py: [
          py.click
          py.mido
        ]);

        # Nix development tools
        nixdevEnv = with pkgs; [
          nixd
          deadnix
          nixd
          nix-diff
          nixfmt-rfc-style
          statix
        ];

      in
      {
        devShells.default = pkgs.mkShell {
          name = "dev-shell";
          packages = mydevEnv ++ [ myPythonEnv ];
          shellHook = ''
            echo "DevShell is now active"
            python --version
            exec fish
          '';
        };
        devShells.nix = pkgs.mkShell {
          name = "nixdev-shell";
          packages = [
            nixdevEnv

          ];
          shellHook = ''
            echo "NixDevShell is now active"
          '';
        };
      }
    );
}
