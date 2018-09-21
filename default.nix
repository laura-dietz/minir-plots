{ fetchFromGitHub, python3Packages }:

let
  squmfit = import ./squmfit.nix { inherit fetchFromGitHub python3Packages; };
in python3Packages.buildPythonPackage {
  pname = "minir-plots";
  version = "0.1";
  src = ./.;
  propagatedBuildInputs = with python3Packages; [ numpy scipy matplotlib pandas ];
}

